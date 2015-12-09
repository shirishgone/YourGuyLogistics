from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group
from django.utils.dateparse import parse_datetime

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from yourguy.models import Order, OrderDeliveryStatus, Consumer, Vendor, DeliveryGuy, Area, VendorAgent, Address, Product, OrderItem, User
from yourguy.models import ProofOfDelivery, Picture

from datetime import datetime, timedelta, time
from api.serializers import OrderSerializer
from api.views import user_role, is_userexists, is_vendorexists, is_consumerexists, is_dgexists, is_address_exists, days_in_int, send_sms, normalize_offset_awareness
from api.views import ist_day_start, ist_day_end, ist_datetime

import constants
from itertools import chain
import json
from api.push import send_push
from dateutil.rrule import rrule, WEEKLY
import pytz

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

def can_update_delivery_status(delivery_status):
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

def update_pending_count(dg):
    try:
        today = datetime.now()

        day_start = ist_day_start(today)
        day_end = ist_day_start(today)

        delivery_statuses = OrderDeliveryStatus.objects.filter(delivery_guy = dg, date__gte = day_start , date__lte = day_end)
        dg.current_load = len(delivery_statuses)
        dg.save()

    except Exception, e:
        print e
        pass

def is_pickup_time_acceptable(datetime):
    if time(0, 0) <= datetime.time() <= time(16, 30):
        return True
    else:
        return False

def delivery_status_of_the_day(order, date):
    delivery_item = None
    if order.is_recurring is False:
        delivery_item = order.delivery_status.latest('date')
    else:
        delivery_statuses = order.delivery_status.all()
        for delivery_status in delivery_statuses:
            if date.date() == delivery_status.date.date():
                delivery_item = delivery_status
                break

    return delivery_item    

def update_daily_status(order, date):
    delivery_status = delivery_status_of_the_day(order, date)
    if delivery_status is not None:    
        
        new_pickup_datetime = datetime.combine(date, order.pickup_datetime.time())
        new_pickup_datetime = pytz.utc.localize(new_pickup_datetime)

        new_delivery_datetime = datetime.combine(date, order.delivery_datetime.time())
        new_delivery_datetime = pytz.utc.localize(new_delivery_datetime)
        
        order.pickup_datetime = new_pickup_datetime
        order.delivery_datetime = new_delivery_datetime

        order.delivered_at = delivery_status.delivered_at
        order.pickedup_datetime = delivery_status.pickedup_datetime
        order.completed_datetime = delivery_status.completed_datetime
        order.order_status = delivery_status.order_status
        order.delivery_guy = delivery_status.delivery_guy
        order.is_cod_collected = delivery_status.is_cod_collected
        return order
    else:
        return None 

class OrderViewSet(viewsets.ModelViewSet):
    """
    Order viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_object(self):
        pk = self.kwargs['pk']
        order = get_object_or_404(Order, id = pk)

        # Access check for vendors
        role = user_role(self.request.user)
        if role == constants.VENDOR:
            vendor_agent = get_object_or_404(VendorAgent, user = self.request.user)
            vendor = vendor_agent.vendor
            if order.vendor.id != vendor.id:
                content = {
                'error':'Access privileges', 
                'description':'You cant access other vendor orders'
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)

        #TODO: Filter objects according to the permissions e.g VendorA shouldn't see orders of VendorB
        date_string = self.request.QUERY_PARAMS.get('date', None)
        if order.is_recurring is True:
            if date_string is None:
                content = {
                'error':'Insufficient params', 
                'description':'For recurring orders, date param in url is compulsory'
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
            else:
                date = parse_datetime(date_string)   
        else:
            date = order.pickup_datetime
        return update_daily_status(order, date)

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `consumer_id` or 'vendor_id' query parameter in the URL.
        """ 
        vendor_id = self.request.QUERY_PARAMS.get('vendor_id', None)
        area_code = self.request.QUERY_PARAMS.get('area_code', None)
        dg_phone_number = self.request.QUERY_PARAMS.get('dg_username', None)
        
        date_string = self.request.QUERY_PARAMS.get('date', None)
        if date_string is not None:
            date = parse_datetime(date_string)
        else:
            date = datetime.today()

        day_start = ist_day_start(date)
        day_end = ist_day_end(date)

        role = user_role(self.request.user)
        if role == constants.VENDOR:
            vendor_agent = get_object_or_404(VendorAgent, user = self.request.user)
            vendor = vendor_agent.vendor
            
            queryset = Order.objects.filter(vendor = vendor, 
                delivery_status__date__gte = day_start,
                delivery_status__date__lte = day_end)
        
        elif role == constants.DELIVERY_GUY:
            delivery_guy = get_object_or_404(DeliveryGuy, user = self.request.user)
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

        # UPDATING DELIVERY STATUS OF THE DAY
        result = []
        for single_order in queryset:
            order = update_daily_status(single_order, date)
            if order is not None:
                result.append(order)        
        
        return result
    
    def create(self, request):
        try:
            pickup_datetime = request.data['pickup_datetime']
            delivery_datetime = request.data['delivery_datetime']
            
            vendor_id = request.data['vendor_id']
            pickup_address_id = request.data['pickup_address_id']
            
            consumers = request.data['consumers']
            if len(consumers) > 20:
                content = {
                'error':'Placing orders for more than 20 customers at once, is not allowed.'
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
            order_items = request.data['order_items']

            total_cost = request.data.get('total_cost')
            vendor_order_id = request.data.get('vendor_order_id')
            is_recurring = request.data['is_recurring']
            
            cod_amount = request.data.get('cod_amount')
            notes = request.data.get('notes')
            
            try:
                if is_recurring is True:
                    start_date_string = request.data['start_date']
                    start_date = parse_datetime(start_date_string)
                    
                    end_date_string = request.data['end_date']
                    end_date = parse_datetime(end_date_string)
                    
                    by_day = request.data['by_day']  
                else:
                    pass
            except Exception, e:
                content = {
                'error':'Incomplete params', 
                'description':'start_date, end_date, by_day should be mentioned for recurring events'
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
            

        except Exception, e:
            content = {
            'error':'Incomplete params', 
            'description':'pickup_datetime, delivery_datetime, order_items, pickup_address_id, delivery_address_id , vendor_id, consumer_id, product_id, quantity, total_cost'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        
        try:
            vendor = get_object_or_404(Vendor, pk = vendor_id)
            pickup_address = get_object_or_404(Address, pk = pickup_address_id)

            pickup_datetime = parse_datetime(pickup_datetime)
            
            if is_pickup_time_acceptable(pickup_datetime) is False:
                content = {
                'error':'Pickup time not acceptable', 
                'description':'Pickup time can only be between 5.30AM to 10.00PM'
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)

            delivery_datetime = parse_datetime(delivery_datetime)

        except Exception, e:
            content = {'error':' Wrong object ids'}    
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        new_order_ids = []
        try:
            for consumer_obj in consumers:
                consumer_id = consumer_obj['consumer_id']
                address_id = consumer_obj['address_id']

                consumer = get_object_or_404(Consumer, pk = consumer_id)
                address = get_object_or_404(Address, pk = address_id)

                new_order = Order.objects.create(created_by_user = request.user, 
                                            vendor = vendor, 
                                            consumer = consumer, 
                                            pickup_address = pickup_address, 
                                            delivery_address = address, 
                                            pickup_datetime = pickup_datetime, 
                                            delivery_datetime = delivery_datetime)

                if vendor.is_retail is False:
                    new_order.order_status = constants.ORDER_STATUS_QUEUED

                if notes is not None:
                    new_order.notes = notes

                if cod_amount is not None and float(cod_amount) > 0:
                    new_order.is_cod = True
                    new_order.cod_amount = float(cod_amount)                    

                for item in order_items:
                    product_id = item['product_id']
                    quantity = item ['quantity']
                    product = get_object_or_404(Product, pk = product_id)
                    order_item = OrderItem.objects.create(product = product, quantity = quantity)
                    new_order.order_items.add(order_item)

                
                if is_recurring is True:
                    new_order.is_recurring = True
                    int_days = days_in_int(by_day)
                    rule_week = rrule(WEEKLY, dtstart=start_date, until=end_date, byweekday=int_days)
                    recurring_dates = list(rule_week)

                    for date in recurring_dates:
                        delivery_status = OrderDeliveryStatus.objects.create(date = date, order = new_order)
                        new_order_ids.append(delivery_status.id)
                else:
                    new_order.is_recurring = False
                    delivery_status = OrderDeliveryStatus.objects.create(date = pickup_datetime, order = new_order)
                    new_order_ids.append(delivery_status.id)
                    if vendor.is_retail is False:
                        delivery_status.order_status = constants.ORDER_STATUS_QUEUED

                if vendor_order_id is not None:
                    new_order.vendor_order_id = vendor_order_id

                if total_cost is not None:
                    new_order.total_cost = total_cost

                new_order.save()

            # CONFIRMATION MESSAGE TO OPS
            # message = constants.ORDER_PLACED_MESSAGE_OPS.format(new_order.id, vendor.store_name)
            # send_sms(constants.OPS_PHONE_NUMBER, message)

            # CONFIRMATION MESSAGE TO CUSTOMER
            message_client = constants.ORDER_PLACED_MESSAGE_CLIENT.format(new_order.id)
            send_sms(vendor.phone_number, message_client)

            content = {
            'status':'orders added',
            'order_ids':new_order_ids
            }

            return Response(content, status = status.HTTP_201_CREATED)
            
        except Exception, e:
            content = {
            'error':'Unable to create orders with the given details'
            }    
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):  
        content = {
        'description': "Deleting an order is not allowed."
        }
        return Response(content, status = status.HTTP_400_BAD_REQUEST)
               
    @detail_route(methods=['post'])
    def place_order(self, request, pk):        
        
        try:            
            pickup_datetime = request.data['pickup_datetime']
            delivery_datetime = request.data['delivery_datetime']
            
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
            'error':'Incomplete params', 
            'description':'pickup_datetime, delivery_datetime, customer_name, customer_phone_number, pickup_address, delivery_address , product_id, quantity, total_cost, is_reverse_pickup'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        try:
            role = user_role(self.request.user)
            if role == constants.VENDOR:
                vendor_agent = get_object_or_404(VendorAgent, user = self.request.user)
                vendor = vendor_agent.vendor
            else:
                content = {
                'error':'API Access limited.', 
                'description':'You cant access this api'
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)

            pickup_datetime = parse_datetime(pickup_datetime)
            if is_pickup_time_acceptable(pickup_datetime) is False:
                content = {
                'error':'Pickup time not acceptable', 
                'description':'Pickup time can only be between 5.30AM to 10.00PM'
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)

            delivery_datetime = parse_datetime(delivery_datetime)

        except Exception, e:
            content = {
            'error':'Error parsing dates'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        try:
            pickup_flat_number = pickup_address['flat_number']
            pickup_building = pickup_address['building']
            pickup_street = pickup_address['street']
            pickup_landmark = pickup_address['landmark']
            pickup_pin_code = pickup_address['pincode']

            pickup_address = is_address_exists(pickup_flat_number, pickup_building, pickup_street, pickup_landmark, pickup_pin_code)
            if pickup_address is None:
                pickup_address = Address.objects.create(flat_number = pickup_flat_number, 
                    building = pickup_building, 
                    street = pickup_street, 
                    landmark = pickup_landmark, 
                    pin_code = pickup_pin_code)
            
            delivery_flat_number = delivery_address['flat_number']
            delivery_building = delivery_address['building']
            delivery_street = delivery_address['street']
            delivery_landmark = delivery_address['landmark']
            delivery_pin_code = delivery_address['pincode']

            delivery_address = is_address_exists(delivery_flat_number, delivery_building, delivery_street, delivery_landmark, delivery_pin_code)
            if delivery_address is None:
                delivery_address = Address.objects.create(flat_number = delivery_flat_number, 
                    building = delivery_building, 
                    street = delivery_street, 
                    landmark = delivery_landmark, 
                    pin_code = delivery_pin_code)

        except:
            content = {'error':' Error parsing addresses'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

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

                # ACCEPTING ADDITIONAL DATES PARAM IN RECURRING =====
                additional_dates = recurring.get('additional_dates')
                for additional_date in additional_dates:
                    delivery_dates.append(parse_datetime(additional_date))

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

            if is_reverse_pickup is True:
                consumer.addresses.add(pickup_address)
                vendor.addresses.add(delivery_address)
            else:
                consumer.addresses.add(delivery_address)
                vendor.addresses.add(pickup_address)
                
            new_order = Order.objects.create(created_by_user = request.user, 
                                            vendor = vendor, 
                                            consumer = consumer, 
                                            pickup_address = pickup_address, 
                                            delivery_address = delivery_address, 
                                            pickup_datetime = pickup_datetime, 
                                            delivery_datetime = delivery_datetime,
                                            is_reverse_pickup = is_reverse_pickup)
            
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
                delivery_status = OrderDeliveryStatus.objects.create(date = date, order = new_order)
                delivery_ids.append(delivery_status.id)

            # ORDER ITEMS =====
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

            # CONFIRMATION MESSAGE TO OPS
            # message = constants.ORDER_PLACED_MESSAGE_OPS.format(new_order.id, vendor.store_name)
            # send_sms(constants.OPS_PHONE_NUMBER, message)

            # CONFIRMATION MESSAGE TO CUSTOMER
            message_client = constants.ORDER_PLACED_MESSAGE_CLIENT.format(new_order.id)
            send_sms(vendor.phone_number, message_client)

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
    def upload_excel(self, request, pk):
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

                consumer_name = single_order['customer_name']
                consumer_phone_number = single_order['customer_phone_number']
                vendor_order_id = single_order['vendor_order_id']
                
                # delivery address ======= 
                delivery_flat_number = single_order['delivery_flat_number']
                delivery_building = single_order['delivery_building']
                delivery_street = single_order['delivery_street']
                delivery_landmark = single_order['delivery_landmark']
                delivery_pin_code = single_order['delivery_pincode']

                # Optional =======
                cod_amount = single_order.get('cod_amount')
            
            except Exception, e:
                content = {'error':'Incomplete parameters', 
                'description':'pickup_datetime, delivery_datetime, customer_name, customer_phone_number, pickup address, delivery address , product_id, quantity, total_cost'
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)

            try:
                role = user_role(self.request.user)
                if role == constants.VENDOR:
                    vendor_agent = get_object_or_404(VendorAgent, user = self.request.user)
                    vendor = vendor_agent.vendor
                else:
                    content = {'error':'API Access limited.', 'description':'You cant access this API'}
                    return Response(content, status = status.HTTP_400_BAD_REQUEST)

                pickup_datetime = parse_datetime(pickup_datetime)
                if is_pickup_time_acceptable(pickup_datetime) is False:
                    content = {'error':'Pickup time not acceptable', 'description':'Pickup time can only be between 5.30AM to 10.00PM'}
                    return Response(content, status = status.HTTP_400_BAD_REQUEST)

                delivery_timedelta = timedelta(hours = 3, minutes = 0)
                delivery_datetime = pickup_datetime + delivery_timedelta

            except Exception, e:
                content = {'error':'Error parsing dates'}
                return Response(content, status = status.HTTP_400_BAD_REQUEST)

            try:
                pickup_address = get_object_or_404(Address, pk = pickup_address_id)

                delivery_address = is_address_exists(delivery_flat_number, delivery_building, delivery_street, delivery_landmark, delivery_pin_code)
                if delivery_address is None:
                    delivery_address = Address.objects.create(flat_number = delivery_flat_number, 
                        building = delivery_building, 
                        street = delivery_street, 
                        landmark = delivery_landmark, 
                        pin_code = delivery_pin_code)

            except:
                content = {'error':' Error parsing addresses'}
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
            
            try:
                existing_order = get_object_or_404(Order, vendor_order_id = vendor_order_id)
                continue
            except Exception, e:
                pass
            
            # CREATE A NEW ORDER ONLY IF VENDOR_ORDER_ID IS UNIQUE
            try:
                if is_userexists(consumer_phone_number) is True:
                    user = get_object_or_404(User, username = consumer_phone_number)
                    if is_consumerexists(user) is True:
                        consumer = get_object_or_404(Consumer, user = user)
                    else:
                        consumer = Consumer.objects.create(user = user)
                        consumer.associated_vendor.add(vendor)
                        consumer.addresses.add(delivery_address)
                else:
                    user = User.objects.create(username = consumer_phone_number, first_name = consumer_name, password = '')
                    consumer = Consumer.objects.create(user = user)
                    consumer.associated_vendor.add(vendor)
                    consumer.addresses.add(delivery_address)
                
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
                
                delivery_status = OrderDeliveryStatus.objects.create(date = pickup_datetime, order = new_order)
                new_order.save()
            except Exception, e:
                content = {'error':'Unable to create orders with the given details'}    
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
        
        content = {'message':'Your Orders has been placed.'}
        return Response(content, status = status.HTTP_201_CREATED)
    
    @detail_route(methods=['post'])
    def exclude_dates(self, request, pk):
        role = user_role(request.user)
        order = get_object_or_404(Order, pk = pk)
          
        if can_user_update_this_order(order, request.user) is False:
            content = {'description': "You don't have permissions to cancel this order."}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        try:
            exclude_dates = request.data['exclude_dates']    
        except Exception, e:
            content = {'error': 'exclude_dates is an array of dates, is missing'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        today = datetime.now()

        is_canceled = False
        for exclude_date_string in exclude_dates:
            exclude_date = parse_datetime(exclude_date_string)

            all_deliveries = order.delivery_status.all()
            for delivery in all_deliveries:
                if delivery.date.date() == exclude_date.date() and exclude_date.date() >= today.date():
                    if can_update_delivery_status(delivery):
                        delivery.order_status = constants.ORDER_STATUS_CANCELLED
                        delivery.save()
                        is_canceled = True
                        break
                    else:
                        content = {'description': "The order has already been processed, cant update now."}
                        return Response(content, status = status.HTTP_400_BAD_REQUEST)
        
        if is_canceled is True:
            content = {'description': 'Order canceled successfully'}
            return Response(content, status = status.HTTP_200_OK)
        else:
            content = {'error': 'Date not found or past date cant be canceled'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def picked_up(self, request, pk=None):
        order = get_object_or_404(Order, pk = pk)
        pop = request.data.get('pop')

        # PICKEDUP DATE TIME =============
        pickedup_datetime_string = request.data.get('pickedup_datetime')
        if pickedup_datetime_string is not None:
            pickedup_datetime = parse_datetime(pickedup_datetime_string) 
        else:
            pickedup_datetime = datetime.now() 
        
        # POP ===================
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
            content = {'error':'An error with pod params'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        #UPDATING THE DELIVERY STATUS OF THE PARTICULAR DAY
        delivery_statuses = order.delivery_status.all()
        for delivery_status in delivery_statuses:            
            if delivery_status.date.date() == pickedup_datetime.date():
                if can_update_delivery_status(delivery_status):

                    delivery_status.order_status = constants.ORDER_STATUS_INTRANSIT
                    delivery_status.pickedup_datetime = pickedup_datetime
                    if new_pop is not None:
                        delivery_status.pickup_proof = new_pop
                    delivery_status.save()
                
                    # UPDATE DG STATUS ==========
                    try:
                        dg = delivery_status.delivery_guy
                        if dg is not None:
                            dg.status = constants.DG_STATUS_BUSY
                            dg.save()
                            # TODO: update_pending_count(dg)
                    except Exception, e:
                        pass
                    break
                else:
                    content = {'description': "The order has already been processed, cant update now."}
                    return Response(content, status = status.HTTP_400_BAD_REQUEST)
        
        content = {'description': 'Order updated'}
        return Response(content, status = status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def delivered(self, request, pk=None):        
        
        order = get_object_or_404(Order, pk = pk)        
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        is_cod_collected = request.data.get('cod_collected')        
        pod = request.data.get('pod')
        
        cod_collected_amount = request.data.get('cod_collected_amount')
        cod_remarks = request.data.get('cod_remarks')
            
        # DELIVERED DATE TIME ----------------------------------------------
        delivered_datetime_string = request.data.get('delivered_datetime')
        if delivered_datetime_string is not None:
            delivered_datetime = parse_datetime(delivered_datetime_string) 
        else:
            delivered_datetime = datetime.now()
        # -------------------------------------------------------------------

        # DELIVERY ATTEMPTED ------------------------------------------------
        try:
            delivered_at = request.data['delivered_at'] 
        except:
            content = {'error':' delivered_at value is missing or wrong. Options: DOOR_STEP, SECURITY, RECEPTION, CUSTOMER, ATTEMPTED'}    
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        if delivered_at == constants.ORDER_STATUS_ATTEMPTED:
            order_status = constants.ORDER_STATUS_DELIVERY_ATTEMPTED
            delivered_at = constants.DELIVERED_AT_NONE
        else:
            order_status = constants.ORDER_STATUS_DELIVERED
        # -------------------------------------------------------------------
        
        # POD -----------------------------------------------------------------
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
            content = {'error':'An error with pod params'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # -------------------------------------------------------------------------
                
        # PICK THE APPROPRIATE DELIVERY STATUS OBJECT -----------------------------
        if is_recurring_order(order):
            delivery_statuses = order.delivery_status.all()
            for delivery_status in delivery_statuses:
                if delivery_status.date.date() == delivered_datetime.date():
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
            if cod_collected_amount is not None and float(cod_collected_amount) > 0:
                end_consumer_phone_number = order.consumer.user.username
                message = 'Dear %s, we have received the payment of %srs behalf of %s - Team YourGuy' % (order.consumer.user.first_name, cod_collected_amount, order.vendor.store_name)
                send_sms(end_consumer_phone_number, message)
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


    @detail_route(methods=['post'])
    def assign_order(self, request, pk = None):
        try:
            dg_id = request.data['dg_id']
            order_ids = request.data['order_ids']    
            
            date_string = request.data.get('date')
            if date_string is None:
                date = datetime.today()
            else:
                date = parse_datetime(date_string)    

        except Exception, e:
            content = {
            'error':'dg_id and order_ids list are Mandatory'
            }    
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        
        dg = get_object_or_404(DeliveryGuy, id = dg_id)
        try:
            dg.status = constants.DG_STATUS_BUSY
            dg.save()
            #TODO: update_pending_count(dg)
        except Exception, e:
            pass

        order_count = len(order_ids)
        if order_count > 50:
            content = {
            'error':'Cant assign more than 50 orders at a time.'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)


        for order_id in order_ids:
            order = get_object_or_404(Order, id = order_id)

            #UPDATING THE DELIVERY STATUS OF THE PARTICULAR DAY
            delivery_statuses = order.delivery_status.all()
            for delivery_status in delivery_statuses: 
                if delivery_status.date.date() >= date.date():
                    delivery_status.delivery_guy = dg
                    if delivery_status.order_status == constants.ORDER_STATUS_PLACED:
                        delivery_status.order_status = constants.ORDER_STATUS_QUEUED
                    delivery_status.save()
                                       
            # SMS to Delivery Guy =======
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
                print 'Order assigned to DG error.'
                pass

        
        # SEND PUSH NOTIFICATION TO DELIVERYGUY
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
            print 'push notification not sent in order assignment'
            pass
        
        # CONFIRMATION MESSAGE TO VENDOR =======
        # try:
        #     message = 'A DeliveryGuy has been assigned for your orders {} . Please get your products ready, he will be there soon - Team YourGuy'.format(order_ids)
        #     send_sms(order.vendor.phone_number, message)
        # except Exception, e:
        #     print 'assignment message not sent to vendor'
        #     pass

        content = {
        'description': 'Order assigned'
        }
        return Response(content, status = status.HTTP_200_OK)
    
    @detail_route(methods=['post'])
    def approve(self, request, pk ):
        try:
            date_string = request.data['date']
            date = parse_datetime(date_string)
        except Exception, e:
            content = {
            'error':'Incomplete params', 
            'description':'date'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        order = get_object_or_404(Order, id = pk)

        #UPDATING THE DELIVERY STATUS OF THE PARTICULAR DAY
        delivery_statuses = order.delivery_status.all()        
        for delivery_status in delivery_statuses:
            if date.date() == delivery_status.date.date():
                if can_update_delivery_status(delivery_status):
                    delivery_status.order_status = constants.ORDER_STATUS_QUEUED
                    delivery_status.save()
                    break
                else:
                    content = {
                    'error': "The order has already been processed, now you cant update the status."
                    }
                    return Response(content, status = status.HTTP_400_BAD_REQUEST)
        
        message = constants.ORDER_APPROVED_MESSAGE_CLIENT.format(order.consumer.user.first_name)
        send_sms(order.vendor.phone_number, message)

        return Response(status = status.HTTP_200_OK)

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

    @detail_route(methods=['post'])
    def reschedule(self, request, pk):
        try:
            new_date_string = request.data['new_date']
            new_date = parse_datetime(new_date_string)
        except Exception, e:
            content = {
            'error':'Incomplete params', 
            'description':'new_date'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        
        is_rescheduled = False
        delivery_status = get_object_or_404(OrderDeliveryStatus, id = pk)
        if can_update_delivery_status(delivery_status):
            delivery_status.date = new_date            
            delivery_status.save()
            is_rescheduled = True
        else:
            content = {
            'error': "The order has already been processed, now you cant update the status."
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        if is_rescheduled:
            readable_date = new_date.strftime("%B %d, %Y")
            message = constants.ORDER_RESCHEDULED_MESSAGE_CLIENT.format(delivery_status.order.consumer.user.first_name, delivery_status.id, readable_date)
            send_sms(delivery_status.order.vendor.phone_number, message)

            content = {
            'description':'Reschedule successful'
            }
            return Response(content, status = status.HTTP_200_OK)
        else:
            content = {
            'error':'Reschedule unsuccessful'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def reject(self, request, pk ):
        try:
            reason_message = request.data['rejection_reason']
        except Exception, e:
            content = {
            'error':'Incomplete params', 
            'description':'rejection_reason'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        delivery_status = get_object_or_404(OrderDeliveryStatus, id = pk)
        if can_update_delivery_status(delivery_status):
            delivery_status.order_status = constants.ORDER_STATUS_REJECTED
            delivery_status.rejection_reason = reason_message
            delivery_status.save()
        else:
            content = {
            'error': "The order has already been processed, now you cant update the status."
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        
        message = constants.ORDER_REJECTED_MESSAGE_CLIENT.format(delivery_status.order.consumer.user.first_name, reason_message)
        send_sms(order.vendor.phone_number, message)
        return Response(status = status.HTTP_200_OK)

    @list_route()
    def undelivered_orders():
        orders = Order.objects.filter(order_status=constants.ORDER_STATUS_INTRANSIT)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)        

    @list_route()
    def unassigned_orders():
        orders = Order.objects.filter(assigned_deliveryGuy= None)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)