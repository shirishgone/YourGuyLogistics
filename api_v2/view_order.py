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
from api.views import user_role, ist_day_start, ist_day_end, is_userexists, is_consumerexists, send_sms, days_in_int, time_delta

from api_v2.utils import is_pickup_time_acceptable, is_consumer_has_same_address_already, is_correct_pincode, is_vendor_has_same_address_already
from api_v2.views import paginate

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import constants
from datetime import datetime, timedelta, time
import math
import pytz
from django.db.models import Q
from itertools import chain
from dateutil.rrule import rrule, WEEKLY

def is_recurring_order(order):
    if len(order.delivery_status.all()) > 1:
        return True
    else:
        return False    

def can_deliver_delivery_status(delivery_status):
    if delivery_status.order_status == constants.ORDER_STATUS_INTRANSIT:
        return True
    else:
        return False  

def can_update_pickup_status(delivery_status):
    if delivery_status.order_status == constants.ORDER_STATUS_PLACED or delivery_status.order_status == constants.ORDER_STATUS_QUEUED:
        return True
    else:
        return False  

def can_user_update_this_order(order, user):
    can_update_order = False
    role = user_role(user)
    if (role == constants.VENDOR):
        vendor_agent = get_object_or_404(VendorAgent, user = user)
        vendor = vendor_agent.vendor
        if order.vendor == vendor:
            can_update_order = True
    elif (role == constants.OPERATIONS):
        can_update_order = True    
    return can_update_order

def delivery_status_of_the_day(order, date):
    delivery_item = None
    
    for delivery_status in order.delivery_status.all():
        if date.date() == delivery_status.date.date():
            delivery_item = delivery_status
            break            
    
    return delivery_item    


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
    
def order_details(order, delivery_status):
    if order.pickup_datetime is not None:
        new_pickup_datetime = datetime.combine(delivery_status.date, order.pickup_datetime.time())
        new_pickup_datetime = pytz.utc.localize(new_pickup_datetime)
    else:
        new_pickup_datetime = None

    if order.delivery_datetime is not None:
        new_delivery_datetime = datetime.combine(delivery_status.date, order.delivery_datetime.time())
        new_delivery_datetime = pytz.utc.localize(new_delivery_datetime)
    else:
        new_delivery_datetime = None
        
    res_order = {
            'id' : order.id,
            'pickup_datetime' : new_pickup_datetime,
            'delivery_datetime' : new_delivery_datetime,
            'pickup_address':address_string(order.pickup_address),
            'delivery_address':address_string(order.delivery_address),
            'status' : delivery_status.order_status,
            'is_recurring' : order.is_recurring,
            'cod_amount' : order.cod_amount,
            'customer_name' : order.consumer.user.first_name,
            'customer_phonenumber' : order.consumer.user.username,
            'vendor_name' : order.vendor.store_name,
            'delivered_at' : delivery_status.delivered_at,
            
            'order_placed_datetime': order.created_date_time,
            'pickedup_datetime' : delivery_status.pickedup_datetime,
            'completed_datetime' : delivery_status.completed_datetime,
            'notes':order.notes,
            'vendor_order_id':order.vendor_order_id,
            'vendor_phonenumber':order.vendor.phone_number,
            'total_cost':order.total_cost,
            'cod_collected_amount':delivery_status.cod_collected_amount,
            'cod_remarks':delivery_status.cod_remarks,
            'delivery_charges':order.delivery_charges
            }
        
    if delivery_status.delivery_guy is not None:
        res_order['deliveryguy_name'] = delivery_status.delivery_guy.user.first_name
        res_order['deliveryguy_phonenumber'] = delivery_status.delivery_guy.user.username
    else:
        res_order['deliveryguy_name'] = None
        res_order['deliveryguy_phonenumber'] = None

    order_items_array = []
    for order_item in order.order_items.all():
        order_item_obj = {}
        order_item_obj['product_name'] = order_item.product.name
        order_item_obj['quantity'] = order_item.quantity
        order_item_obj['cost'] = order_item.cost
        order_items_array.append(order_item_obj)

    res_order['order_items'] = order_items_array
    return res_order


def update_daily_status(order, date):
    delivery_status = delivery_status_of_the_day(order, date)
    if delivery_status is not None:
        
        if order.pickup_datetime is not None:
            new_pickup_datetime = datetime.combine(date, order.pickup_datetime.time())
            new_pickup_datetime = pytz.utc.localize(new_pickup_datetime)
        else:
            new_pickup_datetime = None

        if order.delivery_datetime is not None:
            new_delivery_datetime = datetime.combine(date, order.delivery_datetime.time())
            new_delivery_datetime = pytz.utc.localize(new_delivery_datetime)
        else:
            new_delivery_datetime = None

        res_order = {
            'id' : order.id,
            'pickup_datetime' : new_pickup_datetime,
            'delivery_datetime' : new_delivery_datetime,
            'pickup_address':address_string(order.pickup_address),
            'delivery_address':address_string(order.delivery_address),
            'status' : delivery_status.order_status,
            'is_recurring' : order.is_recurring,
            'cod_amount' : order.cod_amount,
            'customer_name' : order.consumer.user.first_name,
            'vendor_name' : order.vendor.store_name,
            'delivered_at' : delivery_status.delivered_at,
            'is_reverse_pickup':order.is_reverse_pickup
        }

        if delivery_status.delivery_guy is not None:
            res_order['deliveryguy_name'] = delivery_status.delivery_guy.user.first_name
            res_order['deliveryguy_phonenumber'] = delivery_status.delivery_guy.user.username
        else:
            res_order['deliveryguy_name'] = None
            res_order['deliveryguy_phonenumber'] = None
        
        order_items_array = []
        for order_item in order.order_items.all():
            order_item_obj = {}
            order_item_obj['product_name'] = order_item.product.name
            order_item_obj['quantity'] = order_item.quantity
            order_item_obj['cost'] = order_item.cost
            order_items_array.append(order_item_obj)

        res_order['order_items'] = order_items_array

        return res_order
    else:
        return None 

def deliveryguy_list(order, date):
    delivery_status = delivery_status_of_the_day(order, date)
    if delivery_status is not None:
        
        if order.pickup_datetime is not None:
            new_pickup_datetime = datetime.combine(date, order.pickup_datetime.time())
            new_pickup_datetime = pytz.utc.localize(new_pickup_datetime)
        else:
            new_pickup_datetime = None

        if order.delivery_datetime is not None:
            new_delivery_datetime = datetime.combine(date, order.delivery_datetime.time())
            new_delivery_datetime = pytz.utc.localize(new_delivery_datetime)
        else:
            new_delivery_datetime = None

        res_order = {
            'id' : order.id,
            'pickup_datetime' : new_pickup_datetime,
            'delivery_datetime' : new_delivery_datetime,
            'pickup_address':address_string(order.pickup_address),
            'delivery_address':address_string(order.delivery_address),
            'status' : delivery_status.order_status,
            'customer_name' : order.consumer.user.first_name,
            'vendor_name' : order.vendor.store_name,
            'vendor_order_id':order.vendor_order_id
        }

        if order.pickup_address.area is not None:
            res_order['pickup_area_code'] = order.pickup_address.area.area_code
        else:
            res_order['pickup_area_code'] = None

        if order.delivery_address.area is not None:
            res_order['delivery_area_code'] = order.delivery_address.area.area_code
        else:
            res_order['delivery_area_code'] = None

        return res_order
    else:
        return None 


class OrderViewSet(viewsets.ViewSet):
    """
    Order viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def destroy(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, pk=None):
        order = get_object_or_404(Order, id = pk)

        # VENDOR PERMISSION CHECK ==============
        role = user_role(request.user)
        if role == 'vendor':
            vendor_agent = get_object_or_404(VendorAgent, user = request.user)
            vendor = vendor_agent.vendor
            if order.vendor.id != vendor.id:
                content = {'error':'Access privileges', 'description':'You cant access other vendor orders'}
                return Response(content, status = status.HTTP_400_BAD_REQUEST)

        # FETCH DATE PARAM FROM URL PARAMS, IF ITS RECURRING -------
        date_string = self.request.QUERY_PARAMS.get('date', None)
        if is_recurring_order(order):
            if date_string is None:
                content = {'error':'Insufficient params', 'description':'For recurring orders, date parameter in URL is compulsory'}
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
            else:
                date = parse_datetime(date_string)    
        # -----------------------------------------------------------    
        
        # PICK THE APPROPRIATE DELIVERY STATUS OBJECT ---------------
        final_delivery_status = None
        if is_recurring_order(order):
            delivery_statuses = order.delivery_status.all()
            for delivery_status in delivery_statuses:
                if delivery_status.date.date() == date.date():
                    final_delivery_status = delivery_status
                    break
        else:
            final_delivery_status = order.delivery_status.all().latest('date')
        # -----------------------------------------------------------
        
        if final_delivery_status is None:
            content = {
            'error':'Insufficient date for recurring order', 
            'description':'The date you have passed doesnt match with the recurring order'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        else:
            result  = order_details(order, final_delivery_status)
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
            delivery_status_queryset = delivery_status_queryset.filter(delivery_guy = delivery_guy)
        else:
            if dg_phone_number is not None:
                if dg_phone_number.isdigit():
                    user = get_object_or_404(User, username = dg_phone_number)
                    delivery_guy = get_object_or_404(DeliveryGuy, user = user)
                    delivery_status_queryset = delivery_status_queryset.filter(delivery_guy = delivery_guy)
                elif dg_phone_number == 'UNASSIGNED':
                    delivery_status_queryset = delivery_status_queryset.filter(delivery_guy = None)
        # --------------------------------------------------------------------------

        # ORDER STATUS FILTERING ---------------------------------------------------
        if len(order_statuses) > 0:
            order_filter_queryset = []
            for order_status in order_statuses:
                order_filter_queryset.append(delivery_status_queryset.filter(order_status = order_status))
            
            delivery_status_queryset = list(chain(*order_filter_queryset))
        # --------------------------------------------------------------------------

        order_queryset = Order.objects.filter(delivery_status__in = delivery_status_queryset)

        # VENDOR FILTERING ---------------------------------------------------------
        vendor = None
        if role == constants.VENDOR:
            vendor_agent = get_object_or_404(VendorAgent, user = request.user)
            vendor = vendor_agent.vendor
        else:
            if vendor_id is not None:
                vendor = get_object_or_404(Vendor, pk = vendor_id)

        if vendor is not None:
            order_queryset = order_queryset.filter(vendor = vendor)
        # ----------------------------------------------------------------------------

        # TIME SLOT FILTERING --------------------------------------------------------
        if filter_time_end is not None and filter_time_start is not None:
            filter_time_start = parse_datetime(filter_time_start) - time_delta()
            filter_time_end = parse_datetime(filter_time_end) - time_delta()
            order_queryset = order_queryset.filter(pickup_datetime__gte = filter_time_start, pickup_datetime__lte = filter_time_end)
        # ----------------------------------------------------------------------------

        # SEARCH KEYWORD FILTERING ---------------------------------------------------
        if search_query is not None:
            if search_query.isdigit():
                order_queryset = order_queryset.filter(Q(id=search_query) | 
                    Q(vendor_order_id=search_query) |
                    Q(consumer__user__username=search_query))
            else:
                order_queryset = order_queryset.filter(Q(consumer__user__first_name__icontains=search_query))
        # ---------------------------------------------------------------------------- 
        
        # PAGINATION  ----------------------------------------------------------------
        if page is not None:
            page = int(page)
        else:
            page = 1    

        total_orders_count = len(order_queryset)
        total_pages =  int(total_orders_count/constants.PAGINATION_PAGE_SIZE) + 1
        
        if page > total_pages or page<=0:
            response_content = {
            "error": "Invalid page number"
            }
            return Response(response_content, status = status.HTTP_400_BAD_REQUEST)
        else:
            orders = paginate(order_queryset, page)
        # ----------------------------------------------------------------------------
        
        # UPDATING DELIVERY STATUS OF THE DAY  ---------------------------------------
        result = []
        for single_order in orders:
            if role == constants.DELIVERY_GUY:
                order = deliveryguy_list(single_order, date)
            else:
                order = update_daily_status(single_order, date)
            
            if order is not None:
                result.append(order)        
        
        response_content = { "data": result, "total_pages": total_pages, "total_orders" : total_orders_count}
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
        
        # VENDOR ORDER ID Duplication check removed.
        # for order in orders:
        #     try:
        #         existing_order = get_object_or_404(Order, vendor_order_id = order['vendor_order_id'])
        #         error_message = 'An order with vendor_order_id:{} already exists'.format(order['vendor_order_id'])
        #         content = {'error':error_message}
        #         return Response(content, status = status.HTTP_400_BAD_REQUEST)
        #     except Exception, e:
        #         pass
                
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
                    'error':'Pickup time not acceptable', 
                    'description':'Pickup time can only be between 5.30AM to 10.00PM'
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

                delivery_status = OrderDeliveryStatus.objects.create(date = pickup_datetime)
                if vendor.is_retail is False:
                    delivery_status.order_status = 'QUEUED'
                    delivery_status.save()
                new_order.delivery_status.add(delivery_status)
                new_order.save()
            except Exception, e:
                content = {
                'error':'Unable to create orders with the given details'
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
        
        content = {
        'message':'Your Orders has been placed.'
        }
        return Response(content, status = status.HTTP_201_CREATED)
    
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
                'error':'Pickup time not acceptable', 
                'description':'Pickup time can only be between 5.30AM to 10.00PM'
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
                'error':' Insufficient or incorrect parameters',
                'description':'pickup_full_address, pickup_pin_code, pickup_landmark(optional), delivery_full_address, delivery_pin_code, delivery_landmark(optional)'
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

            for date in delivery_dates:
                delivery_status = OrderDeliveryStatus.objects.create(date = date)
                if vendor.is_retail is False:
                    delivery_status.order_status = 'QUEUED'
                    delivery_status.save()
                
                new_order.delivery_status.add(delivery_status)

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
            'order_id':new_order.id
            }, 
            'message':'Your Order has been placed.'
            }
            return Response(content, status = status.HTTP_201_CREATED)
            
        except Exception, e:
            content = {'error':'Unable to create orders with the given details'}    
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def cancel(self, request, pk):        
        order = get_object_or_404(Order, id = pk)
        if can_user_update_this_order(order, request.user) is False:
            content = {
            'error': "You don't have permissions to cancel this order."
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        
        # DATA FILTERING FOR RECURRING ORDERS -----------------------
        date_string = request.data.get('date')
        if is_recurring_order(order) and date_string is None:
            content = {
            'error':'Incomplete parameters', 
            'description':'date parameter is mandatory for recurring orders'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        elif is_recurring_order(order) and date_string is not None:
            try:
                date = parse_datetime(date_string)
            except Exception, e:
                content = {
                'error':'Incorrect date', 
                'description':'date format is not appropriate'
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # -----------------------------------------------------------

        final_delivery_status = None
        is_cancelled = False

        # PICK THE APPROPRIATE DELIVERY STATUS OBJECT ----------------
        if is_recurring_order(order):
            delivery_statuses = order.delivery_status.all()
            for delivery_status in delivery_statuses:
                if delivery_status.date.date() == date.date():
                    final_delivery_status = delivery_status
        else:
            final_delivery_status = order.delivery_status.all().latest('date')
        # -----------------------------------------------------------

        # UPDATE THE DELIVERY STATUS OBJECT -------------------------
        if final_delivery_status is not None and can_update_pickup_status(final_delivery_status):
            final_delivery_status.order_status = constants.ORDER_STATUS_CANCELLED
            final_delivery_status.save()
            is_cancelled = True
        else:
            content = {
            'error': "The order has already been processed, now you cant update the status."
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # ------------------------------------------------------------       
        
        if is_cancelled:
            # message = constants.ORDER_CANCELLED_MESSAGE_CLIENT.format(order.consumer.user.first_name, order.id)
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

    @detail_route(methods=['post'])
    def multiple_pickups(self, request, pk=None):        
        try:
            order_ids   = request.data['order_ids']
            date_string = request.data['date']
            order_date  = parse_datetime(date_string)
        except Exception, e:
            content = {
            'error':'order_ids, date are mandatory parameters'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        
        # PICKEDUP DATE TIME --------------------------------------------------------
        pickedup_datetime_string = request.data.get('pickedup_datetime')
        if pickedup_datetime_string is not None:
            pickedup_datetime = parse_datetime(pickedup_datetime_string) 
        else:
            pickedup_datetime = datetime.now() 
        # ----------------------------------------------------------------------------
        updated_orders = []
        not_updated_orders = []
        
        # UPDATE EACH ORDER --------------------------------------------------------
        for order_id in order_ids:
            try:
                order = get_object_or_404(Order, pk = order_id)
                
                # PICK THE APPROPRIATE DELIVERY STATUS OBJECT ----------------
                if is_recurring_order(order):
                    delivery_statuses = order.delivery_status.all()
                    for delivery_status in delivery_statuses:
                        if delivery_status.date.date() == order_date.date():
                            final_delivery_status = delivery_status
                else:
                    final_delivery_status = order.delivery_status.all().latest('date')
                # -----------------------------------------------------------

                # UPDATING THE DELIVERY STATUS OF THE PARTICULAR DAY -------------------------
                if final_delivery_status is not None and can_update_pickup_status(final_delivery_status): 
                    final_delivery_status.order_status = constants.ORDER_STATUS_INTRANSIT
                    final_delivery_status.pickedup_datetime = pickedup_datetime
                    final_delivery_status.save()
                    updated_orders.append(order_id)
                else:
                    not_updated_orders.append(order_id)
            except Exception, e:
                not_updated_orders.append(order_id)
                pass
        # -------------------------------------------------------------------------------

        content = {
        "updated_orders": updated_orders,
        "un_updated_orders": not_updated_orders
        }
        return Response(content, status = status.HTTP_200_OK)
        

    @detail_route(methods=['post'])
    def picked_up(self, request, pk=None):
        order = get_object_or_404(Order, pk = pk)
        pop = request.data.get('pop')
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
        date_string = request.data.get('date')
        if is_recurring_order(order) and date_string is None:
            content = {
            'error':'Incomplete parameters', 
            'description':'date parameter is mandatory for recurring orders'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        elif is_recurring_order(order) and date_string is not None:
            try:
                order_date = parse_datetime(date_string)
            except Exception, e:
                content = {
                'error':'Incorrect date', 
                'description':'date format is not appropriate'
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # -----------------------------------------------------------
        
        # POP ------------------------------------------------------------------------
        new_pop = None
        try:
            if pop is not None:
                receiver_name = pop['receiver_name']
                signature_name = pop['signature']
                pictures = pop['image_names']
                
                signature = Picture.objects.create(name = signature_name)
                new_pop = ProofOfDelivery.objects.create(receiver_name = receiver_name, signature = signature)
                for picture in pictures:
                    new_pop.pictures.add(Picture.objects.create(name = picture))                       
        except:
            content = {
            'error':'An error with pop parameter'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # ----------------------------------------------------------------------------
        
        # PICK THE APPROPRIATE DELIVERY STATUS OBJECT ----------------
        if is_recurring_order(order):
            delivery_statuses = order.delivery_status.all()
            for delivery_status in delivery_statuses:
                if delivery_status.date.date() == order_date.date():
                    final_delivery_status = delivery_status
        else:
            final_delivery_status = order.delivery_status.all().latest('date')
        # -----------------------------------------------------------

        # UPDATING THE DELIVERY STATUS OF THE PARTICULAR DAY -------------------------
        is_order_updated = False
        if final_delivery_status is not None and can_update_pickup_status(final_delivery_status):
            if pickup_attempted is not None and pickup_attempted == True:
                final_delivery_status.order_status = constants.ORDER_STATUS_PICKUP_ATTEMPTED
                if delivery_remarks is not None:
                    final_delivery_status.cod_remarks = delivery_remarks
            else:
                final_delivery_status.order_status = constants.ORDER_STATUS_INTRANSIT
            
            final_delivery_status.pickedup_datetime = pickedup_datetime
            if new_pop is not None:
                final_delivery_status.pickup_proof = new_pop
            final_delivery_status.save()
            is_order_updated = True
        else:
            content = {
            'error': "The order has already been processed, now you cant update the status."
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # ------------------------------------------------------------       
        
        if is_order_updated:
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

        order = get_object_or_404(Order, pk = pk)        
        
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        # REQUEST PARAMETERS ---------------------------------------------
        is_cod_collected = request.data.get('cod_collected')        
        cod_collected_amount = request.data.get('cod_collected_amount')
        cod_remarks = request.data.get('cod_remarks')
        # ----------------------------------------------------------------
        
        # DELIVERED DATE TIME ---------------------------------------------
        delivered_datetime_string = request.data.get('delivered_datetime')
        if delivered_datetime_string is not None:
            delivered_datetime = parse_datetime(delivered_datetime_string) 
        else:
            delivered_datetime = datetime.now()
        # ----------------------------------------------------------------
                
        # DELIVERY ATTEMPTED CASE HANDLED --------------------------------
        cod_remarks = request.data.get('delivery_remarks')
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
        
        # POD -------------------------------------------------------------
        pod = request.data.get('pod')
        new_pod = None
        try:
            if pod is not None:
                receiver_name = pod['receiver_name']
                signature_name = pod['signature']
                pictures = pod['image_names']
                
                signature = Picture.objects.create(name = signature_name)
                new_pod = ProofOfDelivery.objects.create(receiver_name = receiver_name, signature = signature)
                for picture in pictures:
                    new_pod.pictures.add(Picture.objects.create(name = picture))                       
        except:
            content = {
            'error':'An error with pod parameters'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # ----------------------------------------------------------------
        
        # UPDATE THE DELIVERY STATUS OF THE PARTICULAR DAY ----------------------
        date_string = request.data.get('date')
        if is_recurring_order(order) and date_string is None:
            content = {
            'error':'Incomplete parameters', 
            'description':'date parameter is mandatory for recurring orders'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        elif is_recurring_order(order) and date_string is not None:
            try:
                order_date = parse_datetime(date_string)
            except Exception, e:
                content = {
                'error':'Incorrect date', 
                'description':'date format is not appropriate'
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
        else:
             order_date = None
        # ------------------------------------------------------------------------

        # PICK THE APPROPRIATE DELIVERY STATUS OBJECT -----------------------------
        if is_recurring_order(order):
            delivery_statuses = order.delivery_status.all()
            for delivery_status in delivery_statuses:
                if delivery_status.date.date() == order_date.date():
                    final_delivery_status = delivery_status
        else:
            final_delivery_status = order.delivery_status.all().latest('date')
        # -------------------------------------------------------------------------
       
        # UPDATING THE DELIVERY STATUS OF THE PARTICULAR DAY -----------------------
        is_order_updated = False
        if final_delivery_status is not None and can_deliver_delivery_status(final_delivery_status):
            final_delivery_status.order_status = order_status
            final_delivery_status.delivered_at = delivered_at
            final_delivery_status.completed_datetime = delivered_datetime
            if is_cod_collected is not None:
                final_delivery_status.is_cod_collected = is_cod_collected
            if new_pod is not None:
                final_delivery_status.delivery_proof = new_pod                    
            if cod_remarks is not None:
                final_delivery_status.cod_remarks = cod_remarks
            if cod_collected_amount is not None:
                final_delivery_status.cod_collected_amount = cod_collected_amount
            final_delivery_status.save()
            is_order_updated = True
        else:
            content = {
            'error': "The order has already been processed, now you cant update the status."
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # -----------------------------------------------------------------------       
        
        # Final Response ---------------------------------------------------------
        if is_order_updated:
            
            # CONFIRMATION MESSAGE TO CUSTOMER --------------------------------------
            # message = constants.ORDER_DELIVERED_MESSAGE_CLIENT.format(order_status, order.consumer.user.first_name, delivered_at)
            # send_sms(order.vendor.phone_number, message)
            # -----------------------------------------------------------------------
            
            # UPDATE CUSTOMER LOCATION ----------------------------------------------
            if order_status == constants.ORDER_STATUS_DELIVERED and latitude is not None and longitude is not None:            
                address_id = order.delivery_address.id
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