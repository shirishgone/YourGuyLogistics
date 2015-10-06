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

from yourguy.models import Order, Vendor, VendorAgent, OrderDeliveryStatus, Area, User, DeliveryGuy, Consumer, Address
from api.views import user_role, ist_day_start, ist_day_end, is_userexists, is_consumerexists
from api_v2.utils import is_pickup_time_acceptable, is_consumer_has_same_address_already, is_correct_pincode
from api_v2.views import paginate

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import constants
from datetime import datetime, timedelta, time
import math
import pytz
from django.db.models import Q


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
    
def order_details(order, date):
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
        
        if order.pickup_address.area is not None:
            res_order['pickup_area_code'] = order.pickup_address.area.area_code
        else:
            res_order['pickup_area_code'] = None

        if order.delivery_address.area is not None:
            res_order['delivery_area_code'] = order.delivery_address.area.area_code
        else:
            res_order['delivery_area_code'] = None

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
            'delivered_at' : delivery_status.delivered_at
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
            'vendor_name' : order.vendor.store_name
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

        date_string = self.request.QUERY_PARAMS.get('date', None)
        if date_string is None:
            content = {'error':'Insufficient params', 'description':'For recurring orders, date param in url is compulsory'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        else:
            date = parse_datetime(date_string)   
        
        result  = order_details(order, date)
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

        if date_string is not None:
            date = parse_datetime(date_string)
        else:
            date = datetime.today()

        day_start = ist_day_start(date)
        day_end = ist_day_end(date)

        role = user_role(request.user)
        if role == 'vendor':
            vendor_agent = get_object_or_404(VendorAgent, user = request.user)
            vendor = vendor_agent.vendor
            
            queryset = Order.objects.filter(vendor = vendor, 
                delivery_status__date__gte = day_start,
                delivery_status__date__lte = day_end)

            if search_query is not None:
                if search_query.isdigit():
                    queryset = queryset.filter(Q(id=search_query) | 
                        Q(vendor_order_id=search_query) |
                        Q(consumer__user__username=search_query))
                else:
                    queryset = queryset.filter(Q(consumer__user__first_name__icontains=search_query))
        
        elif role == 'deliveryguy':
            delivery_guy = get_object_or_404(DeliveryGuy, user = request.user)
            delivery_statuses = OrderDeliveryStatus.objects.filter(delivery_guy = delivery_guy, 
                date__gte = day_start,
                date__lte = day_end)

            queryset = Order.objects.filter(delivery_status__in = delivery_statuses).order_by('pickup_datetime')                
        
        else:
            queryset = Order.objects.filter(delivery_status__date__gte = day_start,
                delivery_status__date__lte = day_end)

            if vendor_id is not None:
                vendor = get_object_or_404(Vendor, pk = vendor_id)
                queryset = queryset.filter(vendor = vendor)

            if dg_phone_number is not None:
                user = get_object_or_404(User, username = dg_phone_number)
                dg = get_object_or_404(DeliveryGuy, user = user)
                queryset = queryset.filter(delivery_status__delivery_guy = dg)

            if area_code is not None:
                area = get_object_or_404(Area, area_code = area_code)
                queryset = queryset.filter(delivery_address__area=area)
            
            if order_id is not None:
                queryset = queryset.filter(id = order_id)

            if search_query is not None:
                if search_query.isdigit():
                    queryset = queryset.filter(Q(id=search_query) | 
                        Q(vendor_order_id=search_query) |
                        Q(consumer__user__username=search_query))
                else:
                    queryset = queryset.filter(Q(consumer__user__first_name__icontains=search_query))


        total_orders_count = len(queryset)
        total_pages =  int(total_orders_count/constants.PAGINATION_PAGE_SIZE) + 1
        orders = paginate(queryset, page)
        
        # UPDATING DELIVERY STATUS OF THE DAY
        result = []
        for single_order in orders:
            if role == 'deliveryguy':
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
        
        for order in orders:
            try:
                existing_order = get_object_or_404(Order, vendor_order_id = order['vendor_order_id'])
                error_message = 'An order with vendor_order_id:{} already exists'.format(order['vendor_order_id'])
                content = {'error':error_message}
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
            except Exception, e:
                pass
                
        for single_order in orders:
            try:
                pickup_datetime = single_order['pickup_datetime']
                vendor_order_id = single_order['vendor_order_id']

                # Optional =======
                cod_amount = single_order.get('cod_amount')
                
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

                delivery_timedelta = timedelta(hours = 3, minutes = 0)
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
                    content = {'error':' Error parsing addresses'}
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
                
                delivery_status = OrderDeliveryStatus.objects.create(date = pickup_datetime)
                new_order.delivery_status.add(delivery_status)
                new_order.save()
            except Exception, e:
                content = {'error':'Unable to create orders with the given details'}    
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
        
        content = {'message':'Your Orders has been placed.'}
        return Response(content, status = status.HTTP_201_CREATED)
    