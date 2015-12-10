from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.db.models.functions import Lower
import json

from django.utils.dateparse import parse_datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from yourguy.models import Order, Vendor, VendorAgent, OrderDeliveryStatus, Area, User, DeliveryGuy, Consumer, Address, Product, OrderItem, ProofOfDelivery, Picture
from api.views import user_role, ist_day_start, ist_day_end, is_userexists, is_consumerexists, send_sms, send_email, days_in_int, time_delta
from api.views import is_today_date, log_exception, ist_datetime

from api_v2.utils import is_pickup_time_acceptable, is_consumer_has_same_address_already, is_correct_pincode, is_vendor_has_same_address_already
from api_v2.views import paginate

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import constants
from datetime import datetime, timedelta
import time

import math
import pytz
from django.db.models import Q
from itertools import chain
from dateutil.rrule import rrule, WEEKLY
from api.push import send_push
from django.db.models import Prefetch

def send_dg_notification(dg, order_ids):
    try:
        data = { 
        'message':'A new order has been assigned to you.', 
        'type': 'order_assigned', 
        'data':{
        'order_id': order_ids
        }
        }
        send_push(dg.device_token, data)
    except Exception, e:
        log_exception(e, 'Push notification not sent in order assignment')
        pass

def send_sms_to_dg_about_mass_orders(dg, order_ids):
    try:
        message = 'New Orders are assigned to you. Order IDs: {}'.format(order_ids)
        send_sms(dg.user.username, message)
    except Exception, e:
        log_exception(e, 'Order assignment mass SMS')
        pass

def send_sms_to_dg_about_order(date, dg, order):
    try:
        pickup_date_string = date.strftime("%b%d")
        ist_date_time = ist_datetime(order.pickup_datetime)
        pickup_time_string = ist_date_time.time().strftime("%I:%M%p")
        pickup_total_string = "%s,%s" % (pickup_date_string, pickup_time_string)
        message = 'New Order:{},Pickup:{},Client:{},Cust:{},{},{},COD:{}'.format(order.id, 
            pickup_total_string,
            order.vendor.store_name, 
            order.consumer.user.first_name,
            order.consumer.user.username,
            order.delivery_address,
            order.cod_amount)
        send_sms(dg.user.username, message)
    except Exception, e:
        log_exception(e, 'Order assignment Single SMS')
        pass
    
def is_recurring_order(order):
    if len(order.delivery_status.all()) > 1:
        return True
    else:
        return False    

def is_user_permitted_to_update_order(user, order):
    is_permissible = False
    role = user_role(user)
    if (role == constants.VENDOR):
        vendor_agent = get_object_or_404(VendorAgent, user = user)
        vendor = vendor_agent.vendor
        if order.vendor == vendor:
            is_permissible = True
    elif (role == constants.OPERATIONS) or (role == constants.DELIVERY_GUY):
        is_permissible = True    
    return is_permissible

def can_updated_order(delivery_status, status):
    if status == constants.ORDER_STATUS_INTRANSIT:
        if delivery_status.order_status == constants.ORDER_STATUS_QUEUED:
            return True
        else:
            return False  
    elif status == constants.ORDER_STATUS_DELIVERED:
        if delivery_status.order_status == constants.ORDER_STATUS_INTRANSIT:
            return True
        else:
            return False  
    elif status == constants.ORDER_STATUS_PICKUP_ATTEMPTED:
        if delivery_status.order_status == constants.ORDER_STATUS_QUEUED:
            return True
        else:
            return False
    elif status == constants.ORDER_STATUS_CANCELLED:
        if delivery_status.order_status == constants.ORDER_STATUS_QUEUED:
            return True
        else:
            return False
    elif status == constants.ORDER_STATUS_DELIVERY_ATTEMPTED:
        if delivery_status.order_status == constants.ORDER_STATUS_INTRANSIT:
            return True
        else:
            return False
    else:
        return False

def create_proof(proof_dict):
    try:
        if proof_dict is not None:
            receiver_name = proof_dict['receiver_name']
            signature_name = proof_dict['signature']
            pictures = proof_dict['image_names']
        
            signature = Picture.objects.create(name = signature_name)
            proof = ProofOfDelivery.objects.create(receiver_name = receiver_name, signature = signature)
            for picture in pictures:
                proof.pictures.add(Picture.objects.create(name = picture))                       
                proof.save()        
    except Exception, e:
        log_exception(e, 'create_proof')
    return proof

# UPDATE DELIVERY STATUS -----------------------------------------------------------
def update_delivery_status_delivery_attempted(delivery_status, dg_remarks, attempted_datetime):
    delivery_status.order_status = constants.ORDER_STATUS_DELIVERY_ATTEMPTED
    delivery_status.completed_datetime = attempted_datetime
    if dg_remarks is not None:
        delivery_status.cod_remarks = dg_remarks
    delivery_status.save()

def update_delivery_status_pickup_attempted(delivery_status, dg_remarks, attempted_datetime):
    delivery_status.order_status = constants.ORDER_STATUS_PICKUP_ATTEMPTED
    delivery_status.pickedup_datetime = attempted_datetime
    if dg_remarks is not None:
        delivery_status.cod_remarks = dg_remarks
    delivery_status.save()

def update_delivery_status_pickedup(delivery_status, pickedup_datetime, proof, dg_remarks):
    delivery_status.order_status = constants.ORDER_STATUS_INTRANSIT
    delivery_status.pickedup_datetime = pickedup_datetime
    if proof is not None:
        delivery_status.pickup_proof = proof
    if dg_remarks is not None:
        delivery_status.cod_remarks = dg_remarks
    delivery_status.save()

def update_delivery_status_delivered(delivery_status, delivered_at, delivered_datetime, is_cod_collected, proof, delivery_remarks, cod_collected_amount):
    delivery_status.order_status = constants.ORDER_STATUS_DELIVERED
    delivery_status.delivered_at = delivered_at
    delivery_status.completed_datetime = delivered_datetime
    if is_cod_collected is not None:
        delivery_status.is_cod_collected = is_cod_collected
    if proof is not None:
        delivery_status.delivery_proof = proof                    
    if delivery_remarks is not None:
        delivery_status.cod_remarks = delivery_remarks
    if cod_collected_amount is not None:
        delivery_status.cod_collected_amount = float(cod_collected_amount)
    delivery_status.save()
# ---------------------------------------------------------------------------

def address_string(address):
    try:
        if len(address.full_address) > 1:
            address_string = address.full_address + ', ' + address.pin_code
        else:
            address_string = address.flat_number + ',' + address.building + ',' +  address.street + ',' 
            if address.area is not None:
                address_string = address_string +  address.area.area_name
        return address_string
    except Exception, e:
        print e
        return ''
    
def order_details(delivery_status):
    if delivery_status.order.pickup_datetime is not None:
        new_pickup_datetime = datetime.combine(delivery_status.date, delivery_status.order.pickup_datetime.time())
        new_pickup_datetime = pytz.utc.localize(new_pickup_datetime)
    else:
        new_pickup_datetime = None

    if delivery_status.order.delivery_datetime is not None:
        new_delivery_datetime = datetime.combine(delivery_status.date, delivery_status.order.delivery_datetime.time())
        new_delivery_datetime = pytz.utc.localize(new_delivery_datetime)
    else:
        new_delivery_datetime = None
        
    res_order = {
            'id' : delivery_status.id,
            'pickup_datetime' : new_pickup_datetime,
            'delivery_datetime' : new_delivery_datetime,
            'pickup_address':address_string(delivery_status.order.pickup_address),
            'delivery_address':address_string(delivery_status.order.delivery_address),
            'status' : delivery_status.order_status,
            'is_recurring' : delivery_status.order.is_recurring,
            'is_reported' : delivery_status.is_reported,
            'reported_reason' : delivery_status.reported_reason,
            'cod_amount' : delivery_status.order.cod_amount,
            'customer_name' : delivery_status.order.consumer.user.first_name,
            'customer_phonenumber' : delivery_status.order.consumer.user.username,
            'vendor_name' : delivery_status.order.vendor.store_name,
            'delivered_at' : delivery_status.delivered_at,
            
            'order_placed_datetime': delivery_status.order.created_date_time,
            'pickedup_datetime' : delivery_status.pickedup_datetime,
            'completed_datetime' : delivery_status.completed_datetime,
            'notes':delivery_status.order.notes,
            'vendor_order_id':delivery_status.order.vendor_order_id,
            'vendor_phonenumber':delivery_status.order.vendor.phone_number,
            'total_cost':delivery_status.order.total_cost,
            'cod_collected_amount':delivery_status.cod_collected_amount,
            'cod_remarks':delivery_status.cod_remarks,
            'delivery_charges':delivery_status.order.delivery_charges
            }

    if delivery_status.pickup_guy is not None:
        res_order['pickupguy_id'] = delivery_status.pickup_guy.id
        res_order['pickupguy_name'] = delivery_status.pickup_guy.user.first_name
        res_order['pickupguy_phonenumber'] = delivery_status.pickup_guy.user.username
    else:
        res_order['pickupguy_id'] = None
        res_order['pickupguy_name'] = None
        res_order['pickupguy_phonenumber'] = None
        
    if delivery_status.delivery_guy is not None:
        res_order['deliveryguy_id'] = delivery_status.delivery_guy.id
        res_order['deliveryguy_name'] = delivery_status.delivery_guy.user.first_name
        res_order['deliveryguy_phonenumber'] = delivery_status.delivery_guy.user.username
    else:
        res_order['deliveryguy_id'] = None
        res_order['deliveryguy_name'] = None
        res_order['deliveryguy_phonenumber'] = None

    order_items_array = []
    for order_item in delivery_status.order.order_items.all():
        order_item_obj = {}
        order_item_obj['product_name'] = order_item.product.name
        order_item_obj['quantity'] = order_item.quantity
        order_item_obj['cost'] = order_item.cost
        order_items_array.append(order_item_obj)

    res_order['order_items'] = order_items_array
    return res_order


def update_daily_status(delivery_status):
    if delivery_status is not None:
        if delivery_status.order.pickup_datetime is not None:
            new_pickup_datetime = datetime.combine(delivery_status.date, delivery_status.order.pickup_datetime.time())
            new_pickup_datetime = pytz.utc.localize(new_pickup_datetime)
        else:
            new_pickup_datetime = None

        if delivery_status.order.delivery_datetime is not None:
            new_delivery_datetime = datetime.combine(delivery_status.date, delivery_status.order.delivery_datetime.time())
            new_delivery_datetime = pytz.utc.localize(new_delivery_datetime)
        else:
            new_delivery_datetime = None

        res_order = {
            'id' : delivery_status.id,
            'pickup_datetime' : new_pickup_datetime,
            'delivery_datetime' : new_delivery_datetime,
            'pickup_address':address_string(delivery_status.order.pickup_address),
            'delivery_address':address_string(delivery_status.order.delivery_address),
            'status' : delivery_status.order_status,
            'is_recurring' : delivery_status.order.is_recurring,
            'is_reported' : delivery_status.is_reported,
            'reported_reason' : delivery_status.reported_reason,
            'cod_amount' : delivery_status.order.cod_amount,
            'cod_collected':delivery_status.cod_collected_amount,
            'customer_name' : delivery_status.order.consumer.user.first_name,
            'vendor_name' : delivery_status.order.vendor.store_name,
            'delivered_at' : delivery_status.delivered_at,
            'is_reverse_pickup':delivery_status.order.is_reverse_pickup
        }

        if delivery_status.delivery_guy is not None:
            res_order['deliveryguy_id'] = delivery_status.delivery_guy.id
            res_order['deliveryguy_name'] = delivery_status.delivery_guy.user.first_name
            res_order['deliveryguy_phonenumber'] = delivery_status.delivery_guy.user.username
        else:
            res_order['deliveryguy_id'] = None
            res_order['deliveryguy_name'] = None
            res_order['deliveryguy_phonenumber'] = None
        
        if delivery_status.pickup_guy is not None:
            res_order['pickupguy_id'] = delivery_status.pickup_guy.id
            res_order['pickupguy_name'] = delivery_status.pickup_guy.user.first_name
            res_order['pickupguy_phonenumber'] = delivery_status.pickup_guy.user.username
        else:
            res_order['pickupguy_id'] = None
            res_order['pickupguy_name'] = None
            res_order['pickupguy_phonenumber'] = None

        order_items_array = []
        for order_item in delivery_status.order.order_items.all():
            order_item_obj = {}
            order_item_obj['product_name'] = order_item.product.name
            order_item_obj['quantity'] = order_item.quantity
            order_item_obj['cost'] = order_item.cost
            order_items_array.append(order_item_obj)

        res_order['order_items'] = order_items_array

        return res_order
    else:
        return None 

def deliveryguy_list(delivery_status):
    if delivery_status.order.pickup_datetime is not None:
        new_pickup_datetime = datetime.combine(delivery_status.date, delivery_status.order.pickup_datetime.time())
        new_pickup_datetime = pytz.utc.localize(new_pickup_datetime)
    else:
        new_pickup_datetime = None

    if delivery_status.order.delivery_datetime is not None:
        new_delivery_datetime = datetime.combine(delivery_status.date, delivery_status.order.delivery_datetime.time())
        new_delivery_datetime = pytz.utc.localize(new_delivery_datetime)
    else:
        new_delivery_datetime = None

    res_order = {
        'id' : delivery_status.id,
        'pickup_datetime' : new_pickup_datetime,
        'delivery_datetime' : new_delivery_datetime,
        'pickup_address':address_string(delivery_status.order.pickup_address),
        'delivery_address':address_string(delivery_status.order.delivery_address),
        'status' : delivery_status.order_status,
        'is_reported' : delivery_status.is_reported,
        'reported_reason' : delivery_status.reported_reason,
        'customer_name' : delivery_status.order.consumer.user.first_name,
        'vendor_name' : delivery_status.order.vendor.store_name,
        'vendor_order_id':delivery_status.order.vendor_order_id
    }
    return res_order
        

def order_dict_dg(delivery_status):
    if delivery_status.order.pickup_datetime is not None:
        new_pickup_datetime = datetime.combine(delivery_status.date, delivery_status.order.pickup_datetime.time())
        new_pickup_datetime = pytz.utc.localize(new_pickup_datetime)
    else:
        new_pickup_datetime = None

    if delivery_status.order.delivery_datetime is not None:
        new_delivery_datetime = datetime.combine(delivery_status.date, delivery_status.order.delivery_datetime.time())
        new_delivery_datetime = pytz.utc.localize(new_delivery_datetime)
    else:
        new_delivery_datetime = None

    res_order = {
        'id' : delivery_status.id,
        'pickup_datetime' : new_pickup_datetime,
        'delivery_datetime' : new_delivery_datetime,
        'pickup_address':address_string(delivery_status.order.pickup_address),
        'delivery_address':address_string(delivery_status.order.delivery_address),
        'status' : delivery_status.order_status,
        'customer_name' : delivery_status.order.consumer.user.first_name,
        'vendor_name' : delivery_status.order.vendor.store_name,
        'vendor_order_id':delivery_status.order.vendor_order_id,
        'cod_amount' : delivery_status.order.cod_amount,
        'customer_phonenumber' : delivery_status.order.consumer.user.username,
        'notes':delivery_status.order.notes,
        'vendor_order_id':delivery_status.order.vendor_order_id,
        'total_cost':delivery_status.order.total_cost,
        'is_reported' : delivery_status.is_reported,
        'reported_reason' : delivery_status.reported_reason,
    }
    return res_order

class OrderViewSet(viewsets.ViewSet):
    """
    Order viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def destroy(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, pk=None):
        delivery_status = get_object_or_404(OrderDeliveryStatus, id = pk)

        # VENDOR PERMISSION CHECK ==============
        role = user_role(request.user)
        if role == 'vendor':
            vendor_agent = get_object_or_404(VendorAgent, user = request.user)
            vendor = vendor_agent.vendor
            if delivery_status.order.vendor.id != vendor.id:
                content = {'error':'Access privileges', 'description':'You cant access other vendor orders'}
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
        
        result  = order_details(delivery_status)
        return Response(result, status = status.HTTP_200_OK)        

    def list(self, request):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `consumer_id` or 'vendor_id' query parameter in the URL.
        """ 
        vendor_id = request.QUERY_PARAMS.get('vendor_id', None)
        area_code = request.QUERY_PARAMS.get('area_code', None)
        dg_phone_number = request.QUERY_PARAMS.get('dg_username', None)
        page = request.QUERY_PARAMS.get('page', None)
        date_string = request.QUERY_PARAMS.get('date', None)
        order_id = request.QUERY_PARAMS.get('order_id', None)
        search_query = request.QUERY_PARAMS.get('search', None)
        filter_order_status = request.QUERY_PARAMS.get('order_status', None)
        filter_time_start = request.QUERY_PARAMS.get('time_start', None)
        filter_time_end = request.QUERY_PARAMS.get('time_end', None)
        is_cod = request.QUERY_PARAMS.get('is_cod', None)

        # ORDER STATUS CHECK --------------------------------------------------        
        order_statuses = []
        if filter_order_status is not None:
            order_statuses = filter_order_status.split(',')
        
        for order_status in order_statuses:
            if order_status == constants.ORDER_STATUS_PLACED or order_status == constants.ORDER_STATUS_QUEUED or order_status == constants.ORDER_STATUS_INTRANSIT or order_status == constants.ORDER_STATUS_PICKUP_ATTEMPTED or order_status == constants.ORDER_STATUS_DELIVERED or order_status == constants.ORDER_STATUS_DELIVERY_ATTEMPTED or order_status == constants.ORDER_STATUS_CANCELLED or order_status == constants.ORDER_STATUS_REJECTED:
                pass
            else:
                content = {
                'error':'Incorrect order_status', 
                'description':'Options: QUEUED, INTRANSIT, PICKUPATTEMPTED, DELIVERED, DELIVERYATTEMPTED, CANCELLED'
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # -------------------------------------------------------------------------

        # DATE FILTERING ----------------------------------------------------------
        if date_string is not None:
            date = parse_datetime(date_string)
        else:
            date = datetime.today()

        day_start = ist_day_start(date)
        day_end = ist_day_end(date)

        delivery_status_queryset = OrderDeliveryStatus.objects.filter(date__gte = day_start, date__lte = day_end)
        # --------------------------------------------------------------------------
        
        role = user_role(request.user)

        # DELIVERY GUY FILTERING ---------------------------------------------------
        delivery_guy = None
        if role == constants.DELIVERY_GUY:
            delivery_guy = get_object_or_404(DeliveryGuy, user = request.user)
            delivery_status_queryset = delivery_status_queryset.filter(Q(delivery_guy=delivery_guy) | Q(pickup_guy=delivery_guy))

        else:
            if dg_phone_number is not None:
                if dg_phone_number.isdigit():
                    user = get_object_or_404(User, username = dg_phone_number)
                    delivery_guy = get_object_or_404(DeliveryGuy, user = user)
                    delivery_status_queryset = delivery_status_queryset.filter(Q(delivery_guy=delivery_guy) | Q(pickup_guy=delivery_guy))
                elif dg_phone_number == 'UNASSIGNED_DELIVERY':
                    delivery_status_queryset = delivery_status_queryset.filter(Q(delivery_guy = None))
                elif dg_phone_number == 'UNASSIGNED_PICKUP':
                    delivery_status_queryset = delivery_status_queryset.filter(Q(pickup_guy = None))
                elif dg_phone_number == 'UNASSIGNED':
                    delivery_status_queryset = delivery_status_queryset.filter(Q(pickup_guy = None) & Q(delivery_guy = None))
        # --------------------------------------------------------------------------

        # VENDOR FILTERING ---------------------------------------------------------
        vendor = None
        if role == constants.VENDOR:
            vendor_agent = get_object_or_404(VendorAgent, user = request.user)
            vendor = vendor_agent.vendor
        else:
            if vendor_id is not None:
                vendor = get_object_or_404(Vendor, pk = vendor_id)

        if vendor is not None:
            delivery_status_queryset = delivery_status_queryset.filter(order__vendor = vendor)
        # ----------------------------------------------------------------------------

        # COD FILTERING --------------------------------------------------------------
        if is_cod is not None:
            is_cod_bool = json.loads(is_cod.lower())
            if is_cod_bool is True:
                delivery_status_queryset = delivery_status_queryset.filter(order__cod_amount__gt = 0)
            else:
                delivery_status_queryset = delivery_status_queryset.filter(order__cod_amount = 0)
        # ----------------------------------------------------------------------------

        # TIME SLOT FILTERING --------------------------------------------------------
        if filter_time_end is not None and filter_time_start is not None:
            filter_time_start = parse_datetime(filter_time_start)
            filter_time_end = parse_datetime(filter_time_end)
            delivery_status_queryset = delivery_status_queryset.filter(order__pickup_datetime__gte = filter_time_start, order__pickup_datetime__lte = filter_time_end)
        # ----------------------------------------------------------------------------

        # SEARCH KEYWORD FILTERING ---------------------------------------------------
        if search_query is not None:
            if search_query.isdigit():
                delivery_status_queryset = delivery_status_queryset.filter(Q(id=search_query) | 
                    Q(order__consumer__user__username=search_query) |
                    Q(order__vendor_order_id=search_query))
            else:
                delivery_status_queryset = delivery_status_queryset.filter(Q(order__consumer__user__first_name__icontains=search_query) |
                    Q(order__vendor_order_id=search_query))
        # ----------------------------------------------------------------------------             
        
        # ORDER STATUS FILTERING ---------------------------------------------------
        if len(order_statuses) > 0:
            order_filter_queryset = []
            for order_status in order_statuses:
                order_filter_queryset.append(delivery_status_queryset.filter(order_status = order_status))
            
            delivery_status_queryset = list(chain(*order_filter_queryset))
        # --------------------------------------------------------------------------

        total_orders_count = len(delivery_status_queryset)
        if role == constants.DELIVERY_GUY:
            delivery_statuses = delivery_status_queryset
            result = []
            for single_delivery in delivery_statuses:
                delivery_status_dict = order_dict_dg(single_delivery)
                if delivery_status_dict is not None:
                    result.append(delivery_status_dict)
            
            response_content = { 
            "data": result, 
            "total_pages": 1, 
            "total_orders":total_orders_count
            }
            return Response(response_content, status = status.HTTP_200_OK)
        
        else:
            # PAGINATION  ----------------------------------------------------------------
            if page is not None:
                page = int(page)
            else:
                page = 1    
            
            total_pages =  int(total_orders_count/constants.PAGINATION_PAGE_SIZE) + 1
            if page > total_pages or page<=0:
                response_content = {
                "error": "Invalid page number"
                }
                return Response(response_content, status = status.HTTP_400_BAD_REQUEST)
            else:
                delivery_statuses = paginate(delivery_status_queryset, page)
            # ----------------------------------------------------------------------------
        
            # UPDATING DELIVERY STATUS OF THE DAY  ---------------------------------------
            result = []
            for single_delivery_status in delivery_statuses:
                delivery_status = update_daily_status(single_delivery_status)
                if delivery_status is not None:
                    result.append(delivery_status)
            
            response_content = {
            "data": result, 
            "total_pages": total_pages, 
            "total_orders" : total_orders_count
            }

            return Response(response_content, status = status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def upload_excel(self, request, pk):
        
        # VENDOR ONLY ACCESS CHECK =========
        role = user_role(self.request.user)
        if role == 'vendor':
            vendor_agent = get_object_or_404(VendorAgent, user = self.request.user)
            vendor = vendor_agent.vendor
        else:
            content = {'error':'API Access limited.', 'description':'You cant access this API'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        # =======================
        try:
            pickup_address_id = request.data['pickup_address_id']
            orders = request.data['orders']
        except Exception, e:
            content = {'error':'Incomplete params. pickup_address_id, orders'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
                        
        for single_order in orders:
            try:
                pickup_datetime = single_order['pickup_datetime']
                vendor_order_id = single_order['vendor_order_id']

                # Optional =======
                cod_amount = single_order.get('cod_amount')
                notes = single_order.get('notes')
                        
                # Customer details =======
                consumer_name = single_order['customer_name']
                consumer_phone_number = single_order['customer_phone_number']
                
                # Delivery address ======= 
                delivery_full_address = single_order['delivery_full_address']
                delivery_pin_code = single_order['delivery_pincode']
                delivery_landmark = single_order.get('delivery_landmark')
                
                # PINCODE IS INTEGER CHECK ===== 
                if is_correct_pincode(delivery_pin_code) is False:
                    content = {'error':'Incorrect pin_code', 
                    'description':'Pincode should be an integer with 6 digits.'}
                    return Response(content, status = status.HTTP_400_BAD_REQUEST)
            
            except Exception, e:
                content = {
                'error':'Incomplete params', 
                'description':'pickup_datetime, customer_name, customer_phone_number, pickup address id , delivery address'
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)

            try:
                pickup_datetime = parse_datetime(pickup_datetime)
                if is_pickup_time_acceptable(pickup_datetime) is False:
                    content = {
                    'error':'Pickup date or time not acceptable', 
                    'description':'Pickup time can only be between 5.30AM to 10.00PM and past dates are not allowed'
                    }
                    return Response(content, status = status.HTTP_400_BAD_REQUEST)

                delivery_timedelta = timedelta(hours = 4, minutes = 0)
                delivery_datetime = pickup_datetime + delivery_timedelta

            except Exception, e:
                content = {'error':'Error parsing dates'}
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
            
            # CREATE A NEW ORDER ONLY IF VENDOR_ORDER_ID IS UNIQUE
            try:
                if is_userexists(consumer_phone_number) is True:
                    user = get_object_or_404(User, username = consumer_phone_number)
                    if is_consumerexists(user) is True:
                        consumer = get_object_or_404(Consumer, user = user)
                    else:
                        consumer = Consumer.objects.create(user = user)
                        consumer.associated_vendor.add(vendor)
                else:
                    user = User.objects.create(username = consumer_phone_number, first_name = consumer_name, password = '')
                    consumer = Consumer.objects.create(user = user)
                    consumer.associated_vendor.add(vendor)
                
                # ADDRESS CHECK ----------------------------------
                try:
                    pickup_address = get_object_or_404(Address, pk = pickup_address_id)
                        
                    # CHECK IF THE CONSUMER HAS SAME DELIVERY ADDRESS ------------ 
                    delivery_address = is_consumer_has_same_address_already(consumer, delivery_pin_code)
                    if delivery_address is None:
                        delivery_address = Address.objects.create(full_address = delivery_full_address, pin_code = delivery_pin_code)
                        if delivery_landmark is not None:
                            delivery_address.landmark = delivery_landmark
                        consumer.addresses.add(delivery_address)
                except:
                    content = {
                    'error':' Error parsing addresses'
                    }
                    return Response(content, status = status.HTTP_400_BAD_REQUEST)
                # -------------------------------------------------------

                # CREATE NEW ORDER --------------------------------------
                new_order = Order.objects.create(created_by_user = request.user, 
                                                vendor = vendor, 
                                                consumer = consumer, 
                                                pickup_address = pickup_address, 
                                                delivery_address = delivery_address, 
                                                pickup_datetime = pickup_datetime, 
                                                delivery_datetime = delivery_datetime,
                                                vendor_order_id = vendor_order_id)
                
                if cod_amount is not None and float(cod_amount) > 0:
                    new_order.is_cod = True
                    new_order.cod_amount = float(cod_amount)
                
                if notes is not None:
                    new_order.notes = notes
                new_order.save()
                
                delivery_status = OrderDeliveryStatus.objects.create(date = pickup_datetime, order = new_order)
            except Exception, e:
                content = {
                'error':'Unable to create orders with the given details'
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
        
        content = {
        'message':'Your Orders has been placed.'
        }
        return Response(content, status = status.HTTP_201_CREATED)
        
    def create(self, request):
        role = user_role(self.request.user)
        if role == 'vendor':
            vendor_agent = get_object_or_404(VendorAgent, user = self.request.user)
            vendor = vendor_agent.vendor
        else:   
            content = {
            'error':'API Access limited.', 
            'description':'You cant access this API'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        
        # PARSING REQUEST PARAMS ------------------------
        try:
            order_date = request.data['order_date']
            timeslots = request.data['timeslots']

            product_id = request.data['product_id']
            product = get_object_or_404(Product, pk = product_id)
            
            consumers = request.data['consumers']            
            
            vendor_address_id = request.data['vendor_address_id']
            vendor_address = get_object_or_404(Address, pk = vendor_address_id)
            is_reverse_pickup = request.data['is_reverse_pickup']
                        
            cod_amount = request.data.get('cod_amount')
            notes = request.data.get('notes')
            vendor_order_id = request.data.get('vendor_order_id')
            total_cost = request.data.get('total_cost')

        except Exception, e:
            content = {
            'error':'Incomplete parameters', 
            'description':'order_date, timeslots, customers, product_id, recurring, vendor_address_id, is_reverse_pickup. Optional: cod_amount, notes, total_cost, vendor_order_id'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # ---------------------------------------------------
        
        # TIMESLOT PARSING -----------------------------------
        order_datetime = parse_datetime(order_date)
        try:
            timeslot_start = timeslots['timeslot_start']
            timeslot_end = timeslots['timeslot_end']
        except Exception, e:
            content = {
            'error':'Incomplete parameters', 
            'description':'timeslot_start, timeslot_start are mandatory parameters'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # ---------------------------------------------------

        # CREATING DATES OF DELIVERY ------------------------
        delivery_dates = []
        try:
            recurring = request.data['recurring']
            try:
                start_date_string = recurring['start_date']
                end_date_string = recurring['end_date']
                by_day = recurring['by_day']  
                
                if start_date_string is not None:
                    start_date = parse_datetime(start_date_string)
                    end_date = parse_datetime(end_date_string)
                    int_days = days_in_int(by_day)
                
                    rule_week = rrule(WEEKLY, dtstart=start_date, until=end_date, byweekday=int_days)
                    delivery_dates = list(rule_week)

                # ACCEPTING ADDITIONAL DATES PARAM IN RECURRING ----------------
                additional_dates = recurring.get('additional_dates')
                if additional_dates is not None:
                    for additional_date in additional_dates:
                        delivery_dates.append(parse_datetime(additional_date))
                # ---------------------------------------------------
                
                if len(delivery_dates) <=0:
                    content = {
                    'error':'Incomplete dates', 
                    'description':'Please check the dates'
                    }
                    return Response(content, status = status.HTTP_400_BAD_REQUEST)

            except:
                content = {
                'error':'Incomplete parameters', 
                'description':'start_date, end_date, by_day should be mentioned for recurring events'
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
        except:
            delivery_dates.append(order_datetime)
        # --------------------------------------------------------------
        
        # CREATING NEW ORDER FOR EACH CUSTOMER -------------------------
        if len(consumers) == 0:
            content = {
            'status':'No customers. Please provide customer details [id, address_id]'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)    
        # --------------------------------------------------------------
        
        # CREATING NEW ORDER FOR EACH CUSTOMER -------------------------
        time_obj = time.strptime(timeslot_start,"%H:%M:%S")
        pickup_datetime = order_datetime.replace(hour = time_obj.tm_hour, minute = time_obj.tm_min)
        
        if is_pickup_time_acceptable(pickup_datetime) is False:
            content = {
            'error':'Pickup date or time not acceptable', 
            'description':'Pickup time can only be between 5.30AM to 10.00PM and past dates are not allowed'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        delivery_timedelta = timedelta(hours = 4, minutes = 0) # DELIVERY IS 4 HOURS FROM PICKUP
        delivery_datetime = pickup_datetime + delivery_timedelta
        # --------------------------------------------------------------

        new_order_ids = []
        for cons in consumers:
            
            consumer_id = cons['id']
            consumer_address_id = cons['address_id']
            
            consumer = get_object_or_404(Consumer, pk = consumer_id)
            consumer_address = get_object_or_404(Address, pk = consumer_address_id)
            
            if is_reverse_pickup:
                pickup_adr = consumer_address
                delivery_adr = vendor_address
            else:
                pickup_adr = vendor_address
                delivery_adr = consumer_address
            
            try:
                new_order = Order.objects.create(created_by_user = request.user,
                    vendor = vendor, 
                    consumer = consumer, 
                    pickup_address = pickup_adr, 
                    delivery_address = delivery_adr, 
                    pickup_datetime = pickup_datetime, 
                    delivery_datetime = delivery_datetime,
                    is_reverse_pickup = is_reverse_pickup)
            
            except Exception, e:
                print e
                content = {
                'error':' Error placing new order'
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
            # ---------------------------------------------------
            
            # ADDING OPTIONAL ATTRIBUTES TO NEW ORDER CREATED ------------------
            if notes is not None:
                new_order.notes = notes
            
            if cod_amount is not None and float(cod_amount) > 0:
                new_order.is_cod = True
                new_order.cod_amount = float(cod_amount)
            
            if vendor_order_id is not None:
                new_order.vendor_order_id = vendor_order_id

            if total_cost is not None:
                new_order.total_cost = total_cost

            for date in delivery_dates:
                delivery_status = OrderDeliveryStatus.objects.create(date = date, order = new_order)
                new_order_ids.append(delivery_status.id)

            if len(delivery_dates) > 1:
                new_order.is_recurring = True

            # ORDER ITEMS ----------------------------------------
            order_item = OrderItem.objects.create(product = product, quantity = 1)
            new_order.order_items.add(order_item)            
            # -------------------------------------------------------------           
            
            new_order.save()
        # -------------------------------------------------------------       
        
        # FINAL RESPONSE ----------------------------------------------
        if len(new_order_ids) > 0:
            content = {
            'status':'orders added',
            'order_ids':new_order_ids
            }
            return Response(content, status = status.HTTP_201_CREATED)    
        else:
            content = {
            'status':'There is some problem adding orders, please try again.'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)    
        # -------------------------------------------------------------
    

    @detail_route(methods=['post'])
    def place_order(self, request, pk): 
        role = user_role(self.request.user)
        if role == 'vendor':
            vendor_agent = get_object_or_404(VendorAgent, user = self.request.user)
            vendor = vendor_agent.vendor
        else:   
            content = {
            'error':'API Access limited.', 
            'description':'You cant access this API'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        # PARSING REQUEST PARAMS ------------------------
        try:            
            pickup_datetime = request.data['pickup_datetime']
            
            consumer_name = request.data['customer_name']
            consumer_phone_number = request.data['customer_phone_number']
    
            pickup_address = request.data['pickup_address']
            delivery_address = request.data['delivery_address']
            is_reverse_pickup = request.data['is_reverse_pickup']            
            
            order_items = request.data['order_items']

            total_cost = request.data.get('total_cost')
            vendor_order_id = request.data.get('vendor_order_id')
            
            cod_amount = request.data.get('cod_amount')
            notes = request.data.get('notes')

        except Exception, e:
            content = {
            'error':'Incomplete parameters', 
            'description':'pickup_datetime, customer_name, customer_phone_number, pickup_address{pickup_full_address, pickup_pin_code, pickup_landmark(optional)}, delivery_address{delivery_full_address, delivery_pin_code, delivery_landmark(optional)}, is_reverse_pickup, order_items { product_id, quantity }, total_cost, vendor_order_id, cod_amount, notes'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # ---------------------------------------------------
        
        # PICKUP AND DELIVERY DATES PARSING ------------------------
        try:
            pickup_datetime = parse_datetime(pickup_datetime)
            if is_pickup_time_acceptable(pickup_datetime) is False:
                    content = {
                    'error':'Pickup date or time not acceptable', 
                    'description':'Pickup time can only be between 5.30AM to 10.00PM and past dates are not allowed'
                    }
                    return Response(content, status = status.HTTP_400_BAD_REQUEST)            
            delivery_timedelta = timedelta(hours = 4, minutes = 0)
            delivery_datetime = pickup_datetime + delivery_timedelta
        except Exception, e:
            content = {'error':'Error parsing dates'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # ---------------------------------------------------
        
        # CREATING DATES OF DELIVERY ------------------------
        delivery_dates = []
        try:
            recurring = request.data['recurring']
            try:
                start_date_string = recurring['start_date']
                end_date_string = recurring['end_date']
                by_day = recurring['by_day']  
                
                if start_date_string is not None:
                    start_date = parse_datetime(start_date_string)
                    end_date = parse_datetime(end_date_string)
                    int_days = days_in_int(by_day)
                
                    rule_week = rrule(WEEKLY, dtstart=start_date, until=end_date, byweekday=int_days)
                    delivery_dates = list(rule_week)

                # ACCEPTING ADDITIONAL DATES PARAM IN RECURRING ----------------
                additional_dates = recurring.get('additional_dates')
                if additional_dates is not None:
                    for additional_date in additional_dates:
                        delivery_dates.append(parse_datetime(additional_date))
                # ---------------------------------------------------
                
                if len(delivery_dates) <=0:
                    content = {
                    'error':'Incomplete dates', 
                    'description':'Please check the dates'
                    }
                    return Response(content, status = status.HTTP_400_BAD_REQUEST)

            except:
                content = {
                'error':'Incomplete parameters', 
                'description':'start_date, end_date, by_day should be mentioned for recurring events'
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
        except:
            delivery_dates.append(pickup_datetime)
        # ---------------------------------------------------

        try:
            # CREATING USER & CONSUMER IF DOESNT EXISTS ------------------------
            if is_userexists(consumer_phone_number) is True:
                user = get_object_or_404(User, username = consumer_phone_number)
                if is_consumerexists(user) is True:
                    consumer = get_object_or_404(Consumer, user = user)
                else:
                    consumer = Consumer.objects.create(user = user)
                    consumer.associated_vendor.add(vendor)
            else:
                user = User.objects.create(username = consumer_phone_number, first_name = consumer_name, password = '')
                consumer = Consumer.objects.create(user = user)
                consumer.associated_vendor.add(vendor)
            # ---------------------------------------------------
            
            # ADDRESS CHECK ---------------------------------------------------
            try:
                pickup_full_address = pickup_address['full_address']
                pickup_pin_code = pickup_address['pincode']
                pickup_landmark = pickup_address.get('landmark')
                
                delivery_full_address = delivery_address['full_address']
                delivery_pin_code = delivery_address['pincode']
                delivery_landmark = delivery_address.get('landmark')
            except:
                content = {
                'error':' Address issue',
                'description':'full_address, pincode, landmark [optional]'
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
            # ---------------------------------------------------
            
            # SORTING PICKUP AND DELIVERY ADDRESSES ------------------------------
            try:
                if is_reverse_pickup is False:
                    delivery_adr = is_consumer_has_same_address_already(consumer, delivery_pin_code)
                    if delivery_adr is None:
                        delivery_adr = Address.objects.create(full_address = delivery_full_address, pin_code = delivery_pin_code)
                        if delivery_landmark is not None:
                            delivery_adr.landmark = delivery_landmark
                        consumer.addresses.add(delivery_adr)
                    
                    pickup_adr = is_vendor_has_same_address_already(vendor, pickup_pin_code)
                    if pickup_adr is None:
                        pickup_adr = Address.objects.create(full_address = pickup_full_address, pin_code = pickup_pin_code)
                        if pickup_landmark is not None:
                            pickup_adr.landmark = pickup_landmark
                        vendor.addresses.add(pickup_adr)
                else:
                    pickup_adr = is_consumer_has_same_address_already(consumer, pickup_pin_code)
                    if pickup_adr is None:
                        pickup_adr = Address.objects.create(full_address = pickup_full_address, pin_code = pickup_pin_code)
                        if pickup_landmark is not None:
                            pickup_adr.landmark = pickup_landmark
                        consumer.addresses.add(pickup_adr)
                    
                    delivery_adr = is_vendor_has_same_address_already(vendor, delivery_pin_code)
                    if delivery_adr is None:
                        delivery_adr = Address.objects.create(full_address = delivery_full_address, pin_code = delivery_pin_code)
                        if delivery_landmark is not None:
                            delivery_adr.landmark = delivery_landmark
                        vendor.addresses.add(delivery_adr)
        
            except:
                content = {
                'error':' Error parsing addresses'
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
            # ---------------------------------------------------
            
            # CREATING NEW ORDER ---------------------------------------------  
            try:
                new_order = Order.objects.create(created_by_user = request.user,
                    vendor = vendor, 
                    consumer = consumer, 
                    pickup_address = pickup_adr, 
                    delivery_address = delivery_adr, 
                    pickup_datetime = pickup_datetime, 
                    delivery_datetime = delivery_datetime,
                    is_reverse_pickup = is_reverse_pickup)
            except Exception, e:
                content = {
                'error':' Error placing new order'
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
            # ---------------------------------------------------
            
            # ADDING OPTIONAL ATTRIBUTES TO NEW ORDER CREATED ------------------
            if notes is not None:
                new_order.notes = notes
            
            if cod_amount is not None and float(cod_amount) > 0:
                new_order.is_cod = True
                new_order.cod_amount = float(cod_amount)
            
            if vendor_order_id is not None:
                new_order.vendor_order_id = vendor_order_id

            if total_cost is not None:
                new_order.total_cost = total_cost

            delivery_ids = []
            for date in delivery_dates:
                delivery_status = OrderDeliveryStatus.objects.create(date = date, order =new_order)
                delivery_ids.append(delivery_status.id)
                
            if len(delivery_dates) > 1:
                new_order.is_recurring = True

            # ORDER ITEMS ----------------------------------------
            try:
                for item in order_items:
                    product_id = item['product_id']
                    quantity = item ['quantity']
                    product = get_object_or_404(Product, pk = product_id)
                    order_item = OrderItem.objects.create(product = product, quantity = quantity)
                    new_order.order_items.add(order_item)
            except Exception, e:
                print 'product_id is incorrect'
                pass
            
            new_order.save()
            # ---------------------------------------------------
            
            # CONFIRMATION MESSAGE TO OPS -------------------------
            # message = constants.ORDER_PLACED_MESSAGE_OPS.format(new_order.id, vendor.store_name)
            # send_sms(constants.OPS_PHONE_NUMBER, message)

            # CONFIRMATION MESSAGE TO CUSTOMER ------------------
            # message_client = constants.ORDER_PLACED_MESSAGE_CLIENT.format(new_order.id)
            # send_sms(vendor.phone_number, message_client)
            # ---------------------------------------------------

            content = {
            'data':{
            'order_id':delivery_ids
            }, 
            'message':'Your Order has been placed.'
            }
            return Response(content, status = status.HTTP_201_CREATED)
            
        except Exception, e:
            content = {'error':'Unable to create orders with the given details'}    
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def cancel(self, request, pk):        
        delivery_status = get_object_or_404(OrderDeliveryStatus, id = pk)
        if is_user_permitted_to_update_order(request.user, delivery_status.order) is False:
            content = {
            'error': "You don't have permissions to cancel this order."
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
                
        
        # UPDATE THE DELIVERY STATUS OBJECT -------------------------
        is_cancelled = False        
        if can_updated_order(delivery_status, constants.ORDER_STATUS_CANCELLED):
            delivery_status.order_status = constants.ORDER_STATUS_CANCELLED
            delivery_status.save()
            is_cancelled = True
        else:
            content = {
            'error': "The order has already been processed, now you cant update the status."
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # ------------------------------------------------------------       
        
        if is_cancelled:
            # message = constants.ORDER_CANCELLED_MESSAGE_CLIENT.format(delivery_status.order.consumer.user.first_name, delivery_status.id)
            # send_sms(order.vendor.phone_number, message)
            content = {
            'description':'Order has been canceled'
            }
            return Response(content, status = status.HTTP_200_OK)
        else:
            content = {
            'error':'Order cancellation failed'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['put'])
    def report(self, request, pk=None):
        try:
            order_ids = request.data['order_ids']
            reported_reason = request.data['reported_reason']
        except Exception, e:
            content = {
            'error':'order_ids, reported_reason are mandatory parameters'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        
        role = user_role(request.user)
        if role == constants.DELIVERY_GUY:
            email_orders = []
            for order_id in order_ids:
                delivery_status = get_object_or_404(OrderDeliveryStatus, pk = order_id)                
                delivery_status.is_reported = True
                delivery_status.reported_reason = reported_reason
                delivery_status.save()
                
                order_detail = {
                'order_id':delivery_status.id,
                'vendor':delivery_status.order.vendor.store_name,
                'customer_name':delivery_status.order.consumer.user.first_name
                }
                email_orders.append(order_detail)
            
            # SEND AN EMAIL TO OPERATIONS ---------------------------------------------
            delivery_guy = get_object_or_404(DeliveryGuy, user = request.user)
            subject = '%s Reported Issue'% (delivery_guy.user.first_name)
            
            body = 'Hello,\n\n%s has reported an issue about the following orders. \n\nIssue: %s\n'% (delivery_guy.user.first_name, reported_reason)
            for email_order in email_orders:
                string = '\nOrder no: %s Client Name: %s Customer Name: %s'% (email_order['order_id'], email_order['vendor'], email_order['customer_name'])
                body = body + string
            
            body = body + '\n\nThanks \n-YourGuy BOT'
            send_email(constants.EMAIL_REPORTED_ORDERS, subject, body)
            # --------------------------------------------------------------------------
            
            content = {
            'data':'Successfully reported'
            }
            return Response(content, status = status.HTTP_200_OK)
        else:
            content = {
            'error':'You dont have permissions to report about the orders'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['put'])
    def multiple_pickup_attempted(self, request, pk=None):         
        try:
            order_ids = request.data['order_ids']
            date_string = request.data['date']
            delivery_remarks = request.data['delivery_remarks']
            pickedup_datetime_string = request.data['pick_attempted_datetime']
        except Exception, e:
            content = {
            'error':'order_ids, date, delivery_remarks, pick_attempted_datetime are mandatory parameters'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        
        try:
            order_date  = parse_datetime(date_string)
            pickedup_datetime = parse_datetime(pickedup_datetime_string)            
        except Exception, e:
            log_exception(e, 'parsing date in multiple_pickup_attempted')
            content = {
            'error':'Parsing error for pickedup_datetime or date'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
            
        for order_id in order_ids:
            try:
                delivery_status = get_object_or_404(OrderDeliveryStatus, pk = order_id)
                if is_user_permitted_to_update_order(request.user, delivery_status.order) is False:
                    content = {
                    'error': "You don't have permissions to update this order."
                    }
                    return Response(content, status = status.HTTP_400_BAD_REQUEST)

                if can_updated_order(delivery_status, constants.ORDER_STATUS_PICKUP_ATTEMPTED):
                    update_delivery_status_pickup_attempted(delivery_status, delivery_remarks, pickedup_datetime)
                else:
                    content = {
                    'error': "Order already processed cant attempt the pickup now"
                    }
                    return Response(content, status = status.HTTP_400_BAD_REQUEST)

            except Exception, e:
                log_exception(e, 'multiple_pickup_attempted')
                content = {
                'error':'Order update failed',
                'data':{'order_id':order_id}
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
        
        content = {
        "data": 'Orders attempted',
        }
        return Response(content, status = status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def multiple_pickups(self, request, pk=None):        
        
        # INPUT PARAM CHECK -------------------------------------------------
        try:
            order_ids   = request.data['order_ids']
            date_string = request.data['date'] 
            
            pickedup_datetime_string = request.data.get('pickedup_datetime')
            pop_dict = request.data.get('pop')
            delivery_remarks = request.data.get('delivery_remarks')
        except Exception, e:
            content = {
            'error':'order_ids, date, pickedup_datetime are mandatory parameters and pop, delivery_remarks are optional'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # -------------------------------------------------------------------
        
        # DATE FORMAT CHECK -------------------------------------------------
        try:
            order_date  = parse_datetime(date_string)
            if pickedup_datetime_string is not None:
                pickedup_datetime = parse_datetime(pickedup_datetime_string) 
            else: 
                pickedup_datetime = datetime.now() 
        except Exception, e:
            content = {
            'error':'date format error'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # -------------------------------------------------------------------                    
        
        new_pop = None
        for order_id in order_ids:
            try:
                delivery_status = get_object_or_404(OrderDeliveryStatus, pk = order_id)
                if is_user_permitted_to_update_order(request.user, delivery_status.order) is False:
                    content = {
                    'error': "You don't have permissions to update this order."
                    }
                    return Response(content, status = status.HTTP_400_BAD_REQUEST)
                
                if can_updated_order(delivery_status, constants.ORDER_STATUS_INTRANSIT):
                    # POP ------------------------------------------------------------------------
                    if new_pop is None and pop_dict is not None:
                        new_pop = create_proof(pop_dict)                    
                    # ----------------------------------------------------------------------------
                    update_delivery_status_pickedup(delivery_status, pickedup_datetime, new_pop, delivery_remarks)
                else:
                    content = {
                    'error': "Cant update as the order is not queued"
                    }
                    return Response(content, status = status.HTTP_400_BAD_REQUEST)
                    
            except Exception, e:
                log_exception(e, 'multiple_pickup_attempted')
                content = {
                'error':'Order update failed',
                'data':{'order_id':order_id}
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)        
        content = {
        "data": 'Orders pickedup',
        }
        return Response(content, status = status.HTTP_200_OK)
        
    @detail_route(methods=['post'])
    def picked_up(self, request, pk=None):
        delivery_status = get_object_or_404(OrderDeliveryStatus, pk = pk)
        if is_user_permitted_to_update_order(request.user, delivery_status.order) is False:
            content = {
            'error': "You don't have permissions to update this order."
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        pop_dict = request.data.get('pop')
        pickup_attempted = request.data.get('pickup_attempted')
        delivery_remarks = request.data.get('delivery_remarks')
        
        # PICKEDUP DATE TIME --------------------------------------------------------
        pickedup_datetime_string = request.data.get('pickedup_datetime')
        if pickedup_datetime_string is not None:
            pickedup_datetime = parse_datetime(pickedup_datetime_string) 
        else:
            pickedup_datetime = datetime.now() 
        # ----------------------------------------------------------------------------
        
        # DATA FILTERING FOR RECURRING ORDERS -----------------------
        date_string = request.data['date']
        try:
            order_date = parse_datetime(date_string)
        except Exception, e:
            content = {
            'error':'Incorrect date', 
            'description':'date format is not appropriate'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # ----------------------------------------------------------------------------
        
        is_order_updated = False
        is_order_picked_up = False        
        
        if can_updated_order(delivery_status, constants.ORDER_STATUS_INTRANSIT):
            if pickup_attempted is not None and pickup_attempted == True:
                update_delivery_status_pickup_attempted(delivery_status, delivery_remarks, pickedup_datetime)
                is_order_updated = True
                is_order_picked_up = False
            else:
                # POP ------------------------------------------------------------------------
                new_pop = None
                if pop_dict is not None:
                    new_pop = create_proof(pop_dict)
                # ----------------------------------------------------------------------------
                update_delivery_status_pickedup(delivery_status, pickedup_datetime, new_pop, delivery_remarks)
                is_order_updated = True
                is_order_picked_up = True
        else:
            content = {
            'error': "Cant update as the order is not queued"
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)        
        
        if is_order_updated:
            if is_order_picked_up is True and delivery_status.order.is_reverse_pickup is True:
                # SEND A CONFIRMATION MESSAGE TO THE CUSTOMER
                end_consumer_phone_number = delivery_status.order.consumer.user.username
                message = 'Dear %s, we have picked your order behalf of %s - Team YourGuy' % (delivery_status.order.consumer.user.first_name, delivery_status.order.vendor.store_name)
                send_sms(end_consumer_phone_number, message)

            content = {
            'description':'Order has been updated'
            }
            return Response(content, status = status.HTTP_200_OK)
        else:
            content = {
            'error':'Order update failed'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def delivered(self, request, pk=None):   
        delivery_status = get_object_or_404(OrderDeliveryStatus, pk = pk)
        if is_user_permitted_to_update_order(request.user, delivery_status.order) is False:
            content = {
            'error': "You don't have permissions to update this order."
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
                
        # REQUEST PARAMETERS ---------------------------------------------
        date_string = request.data['date']
        is_cod_collected = request.data.get('cod_collected')        
        cod_collected_amount = request.data.get('cod_collected_amount')
        delivery_remarks = request.data.get('cod_remarks')
        delivery_remarks = request.data.get('delivery_remarks')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        # ----------------------------------------------------------------
        
        # DELIVERED DATE TIME ---------------------------------------------
        delivered_datetime_string = request.data.get('delivered_datetime')
        if delivered_datetime_string is not None:
            delivered_datetime = parse_datetime(delivered_datetime_string) 
        else:
            delivered_datetime = datetime.now()
        # ----------------------------------------------------------------
                
        # DELIVERY ATTEMPTED CASE HANDLED --------------------------------        
        delivery_attempted = request.data.get('delivery_attempted')
        if delivery_attempted is not None and delivery_attempted is True:
            order_status = constants.ORDER_STATUS_DELIVERY_ATTEMPTED
            delivered_at = constants.DELIVERED_AT_NONE
        else:
            order_status = constants.ORDER_STATUS_DELIVERED
            delivered_at = request.data.get('delivered_at')               
            try:
                if delivered_at == 'DOOR_STEP' or delivered_at == 'SECURITY' or delivered_at == 'RECEPTION' or delivered_at == 'CUSTOMER':
                    pass
                else:
                    content = {
                    'error':' delivered_at value is missing or wrong. Options: DOOR_STEP, SECURITY, RECEPTION, CUSTOMER'
                    }
                    return Response(content, status = status.HTTP_400_BAD_REQUEST)
            except Exception, e:
                content = {
                'error':' delivered_at value is missing or wrong. Options: DOOR_STEP, SECURITY, RECEPTION, CUSTOMER'
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # ----------------------------------------------------------------
                
        # UPDATE THE DELIVERY STATUS OF THE PARTICULAR DAY ----------------------        
        try:
            order_date = parse_datetime(date_string)
        except Exception, e:
            content = {
            'error':'Incorrect date', 
            'description':'date format is not appropriate'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # ------------------------------------------------------------------------
                
        # UPDATING THE DELIVERY STATUS OF THE PARTICULAR DAY -----------------------
        is_order_updated = False
        if can_updated_order(delivery_status, constants.ORDER_STATUS_DELIVERED):
            try:
                # POD -------------------------------------------------------------
                pod_dict = request.data.get('pod')
                new_pod = None
                if pod_dict is not None:
                    new_pod = create_proof(pod_dict)
                # ----------------------------------------------------------------
                if order_status == constants.ORDER_STATUS_DELIVERY_ATTEMPTED:
                    update_delivery_status_delivery_attempted(delivery_status, delivery_remarks, delivered_datetime)
                else:    
                    update_delivery_status_delivered(delivery_status, delivered_at, delivered_datetime, is_cod_collected, new_pod, delivery_remarks, cod_collected_amount)
                is_order_updated = True
            except Exception, e:
                log_exception(e, 'order_delivered')
        else:
            content = {
            'error': "The order has already been processed, now you cant update the status."
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # -----------------------------------------------------------------------       
        
        # Final Response ---------------------------------------------------------
        if is_order_updated:            
            # CONFIRMATION MESSAGE TO CUSTOMER --------------------------------------
            if cod_collected_amount is not None and float(cod_collected_amount) > 0:
                end_consumer_phone_number = delivery_status.order.consumer.user.username
                message = 'Dear %s, we have received the payment of %srs behalf of %s - Team YourGuy' % (delivery_status.order.consumer.user.first_name, cod_collected_amount, delivery_status.order.vendor.store_name)
                send_sms(end_consumer_phone_number, message)
            # -----------------------------------------------------------------------
            
            # UPDATE CUSTOMER LOCATION ----------------------------------------------
            if order_status == constants.ORDER_STATUS_DELIVERED and latitude is not None and longitude is not None:            
                address_id = delivery_status.order.delivery_address.id
                address = get_object_or_404(Address, pk = address_id)        
                address.latitude = latitude
                address.longitude = longitude
                address.save()
            # -----------------------------------------------------------------------

            content = {
            'description':'Order has been updated'
            }
            return Response(content, status = status.HTTP_200_OK)
        else:
            content = {
            'error':'Order update failed'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # -----------------------------------------------------------------------

    @detail_route(methods=['post'])
    def assign_order(self, request, pk = None):
        
        # INPUT PARAM CHECK ---------------------------------------------
        try:
            dg_id = request.data['dg_id']
            delivery_ids = request.data['order_ids']
            date_string = request.data['date']
            assignment_type = request.data['assignment_type']
        except Exception, e:
            content = {
            'error':'dg_id, order_ids, date, assignment_type are Mandatory'
            }    
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # ---------------------------------------------------------------
       
        # MAX ORDERS PER DG CHECK ---------------------------------------
        delivery_count = len(delivery_ids)
        if delivery_count > 50:
            content = {
            'error':'Cant assign more than 50 orders at a time.'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # ---------------------------------------------------------------

        # ASSIGNMENT TYPE CHECK -----------------------------------------
        if assignment_type == 'pickup' or assignment_type == 'delivery':
            pass
        else:
            content = {
            'error':'assignment_type can only be either pickup or delivery'
            }    
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # ---------------------------------------------------------------
       
        is_orders_assigned = False       
        date = parse_datetime(date_string)
        dg = get_object_or_404(DeliveryGuy, id = dg_id)
        for delivery_id in delivery_ids:
            delivery_status = get_object_or_404(OrderDeliveryStatus, id = delivery_id)
            order = delivery_status.order            

            current_datetime = datetime.now()
            if current_datetime.date() > delivery_status.date.date():
                content = {
                'error': "Cant assign orders of previous dates"
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
            
            if order.is_recurring is True:
                # FETCHING ALL RECURRING ORDERS FOR ASSIGNMENT ------------------------
                today_datetime = current_datetime.replace(hour=0, minute=0, second=0)
                recurring_delivery_statuses = OrderDeliveryStatus.objects.filter(order = order, date__gte = today_datetime)
                for recurring_delivery_status in recurring_delivery_statuses:
                    if is_user_permitted_to_update_order(request.user, recurring_delivery_status.order) is False:
                        content = {
                        'error': "You don't have permissions to update this order."
                        }
                        return Response(content, status = status.HTTP_400_BAD_REQUEST)
                    
                    # Final Assignment -------------------------------------------
                    if assignment_type == 'pickup':
                        recurring_delivery_status.pickup_guy = dg
                    else:
                        recurring_delivery_status.delivery_guy = dg
                    recurring_delivery_status.save()
                    is_orders_assigned = True
            else:
                if is_user_permitted_to_update_order(request.user, delivery_status.order) is False:
                    content = {
                    'error': "You don't have permissions to update this order."
                    }
                    return Response(content, status = status.HTTP_400_BAD_REQUEST)
                
                # Final Assignment -------------------------------------------
                if assignment_type == 'pickup':
                    delivery_status.pickup_guy = dg
                else:
                    delivery_status.delivery_guy = dg
                delivery_status.save()
                is_orders_assigned = True
            # -------------------------------------------------------------
                        
        # INFORM DG THROUGH SMS AND NOTIF IF ITS ONLY TODAYS DELIVERY -----
        if is_orders_assigned is True:
            try:
                if is_today_date(date):
                    send_dg_notification(dg, delivery_ids)
                    if delivery_count == 1:
                        send_sms_to_dg_about_order(date, dg, delivery_status.order)
                    else:
                        send_sms_to_dg_about_mass_orders(dg, delivery_ids)
            except Exception, e:
                log_exception(e, 'assign_order_notify_dg')

            content = {
            'description': 'Order assigned'
            }
            return Response(content, status = status.HTTP_200_OK)          
        else:
            content = {
            'error':'Few orders arent updated'
            }    
            return Response(content, status = status.HTTP_400_BAD_REQUEST)