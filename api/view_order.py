from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group
from django.utils.dateparse import parse_datetime

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from yourguy.models import Order, OrderDeliveryStatus, Consumer, Vendor, DeliveryGuy, Area, VendorAgent, Address, Product, OrderItem, User
from datetime import datetime, timedelta, time
from api.serializers import OrderSerializer
from api.views import user_role, is_vendorexists, is_consumerexists, is_dgexists, days_in_int, send_sms, normalize_offset_awareness
import constants
import recurrence
from itertools import chain
import json
from api.push import send_push

def update_pending_count(dg):
    try:
        today = datetime.now()
        delivery_statuses = OrderDeliveryStatus.objects.filter(delivery_guy = dg, date__year = today.year , date__month = today.month, date__day = today.day)
        dg.current_load = len(delivery_statuses)
        dg.save()
    except Exception, e:
        print e
        pass


def delivery_status_of_the_day(order, date):
    delivery_statuses = order.delivery_status.all()

    delivery_item = None
    for delivery_status in delivery_statuses:
        date_1 = datetime.combine(date, time()).replace(hour=0, minute=0, second=0)
        date_2 = datetime.combine(delivery_status.date, time()).replace(hour=0, minute=0, second=0)
        if date_1 == date_2:
            delivery_item = delivery_status
            break
    return delivery_item    

def update_daily_status(order, date):
    delivery_status = delivery_status_of_the_day(order, date)
    if delivery_status is not None:
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
        #TODO: Filter objects according to the permissions e.g VendorA shouldn't see orders of VendorB

        date_string = self.request.QUERY_PARAMS.get('date', None)
        if date_string is not None:
            date = parse_datetime(date_string)
        else:
            date = datetime.today()
        
        order = get_object_or_404(Order, id = pk)
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

        role = user_role(self.request.user)
        if role == constants.VENDOR:
            vendor_agent = get_object_or_404(VendorAgent, user = self.request.user)
            vendor = vendor_agent.vendor
            
            queryset = Order.objects.filter(vendor = vendor, 
                delivery_status__date__year = date.year , 
                delivery_status__date__month = date.month, 
                delivery_status__date__day = date.day)
        
        elif role == constants.DELIVERY_GUY:

            delivery_guy = get_object_or_404(DeliveryGuy, user = self.request.user)
            delivery_statuses = OrderDeliveryStatus.objects.filter(delivery_guy = delivery_guy, 
                date__year = date.year, 
                date__month = date.month, 
                date__day = date.day)

            queryset = Order.objects.filter(delivery_status__in = delivery_statuses)

        else:

            queryset = Order.objects.filter(delivery_status__date__year = date.year, 
                    delivery_status__date__month = date.month, 
                    delivery_status__date__day = date.day)

            if vendor_id is not None:
                vendor = get_object_or_404(Vendor, pk = vendor_id)
                queryset = queryset.filter(vendor = vendor)

            if dg_phone_number is not None:
                user = get_object_or_404(User, username = dg_phone_number)
                dg = get_object_or_404(DeliveryGuy, user = user)
                queryset = queryset.filter(delivery_guy=dg)

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
            order_items = request.data['order_items']

            total_cost = request.data.get('total_cost')
            vendor_order_id = request.data.get('vendor_order_id')
            is_recurring = request.data['is_recurring']
            
            is_cod = request.data.get('is_cod')
            cod_amount = request.data.get('cod_amount')
            notes = request.data.get('notes')
            
            try:
                if is_recurring is True:
                    start_date_string = request.data['start_date']
                    start_date = parse_datetime(start_date_string)
                    start_date = datetime.combine(start_date, time()).replace(hour=0, minute=0, second=0)

                    end_date_string = request.data['end_date']
                    end_date = parse_datetime(end_date_string)
                    end_date = datetime.combine(end_date, time()).replace(hour=0, minute=0, second=0)
                    
                    by_day = request.data['by_day']  
                else:
                    pass
            except Exception, e:
                content = {'error':'Incomplete params', 'description':'start_date, end_date, by_day should be mentioned for recurring events'}
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
            

        except Exception, e:
            content = {'error':'Incomplete params', 'description':'pickup_datetime, delivery_datetime, order_items, pickup_address_id, delivery_address_id , vendor_id, consumer_id, product_id, quantity, total_cost'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        try:
            vendor = get_object_or_404(Vendor, pk = vendor_id)
            pickup_address = get_object_or_404(Address, pk = pickup_address_id)

            pickup_datetime = parse_datetime(pickup_datetime)
            delivery_datetime = parse_datetime(delivery_datetime)
            # delivery_datetime = delivery_datetime.replace(tzinfo=utc)
            # delivery_datetime = timezone.make_aware(delivery_datetime, timezone.get_current_timezone())

        except Exception, e:
            content = {'error':' Wrong object ids'}    
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

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

                if is_cod is True:
                    new_order.is_cod = is_cod
                    new_order.cod_amount = cod_amount

                for item in order_items:
                    product_id = item['product_id']
                    quantity = item ['quantity']
                    product = get_object_or_404(Product, pk = product_id)
                    order_item = OrderItem.objects.create(product = product, quantity = quantity)
                    new_order.order_items.add(order_item)

                if is_recurring is True:
                    new_order.is_recurring = True                                        
                    int_days = days_in_int(by_day)
                    
                    rule = recurrence.Rule(byday = int_days, freq = recurrence.WEEKLY)
                    recurrences = recurrence.Recurrence(
                                    dtstart = start_date,
                                    dtend = end_date,
                                    rrules = [rule]
                                    )
                    new_order.recurrences = recurrences
                    
                    recurring_dates = list(recurrences.occurrences())
                    for date in recurring_dates:
                        delivery_status = OrderDeliveryStatus.objects.create(date = date)
                        new_order.delivery_status.add(delivery_status)

                else:
                    new_order.is_recurring = False
                    delivery_status = OrderDeliveryStatus.objects.create(date = delivery_datetime)
                    if vendor.is_retail is False:
                        delivery_status.order_status = constants.ORDER_STATUS_QUEUED

                    new_order.delivery_status.add(delivery_status)

                if vendor_order_id is not None:
                    new_order.vendor_order_id = vendor_order_id

                if total_cost is not None:
                    new_order.total_cost = total_cost

                new_order.save()

            # CONFIRMATION MESSAGE TO OPS
            message = constants.ORDER_PLACED_MESSAGE_OPS.format(vendor.store_name)
            send_sms(constants.OPS_PHONE_NUMBER, message)

            # CONFIRMATION MESSAGE TO CUSTOMER
            send_sms(vendor.phone_number, constants.ORDER_PLACED_MESSAGE_CLIENT)

            content = {'status':'orders added'}
            return Response(content, status = status.HTTP_201_CREATED)
            
        except Exception, e:
            content = {'error':'Unable to create orders with the given details'}    
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

    
    @list_route(methods = ['get'])
    def pause_for_the_day(self, request):
        try:
            order_ids_string = self.request.QUERY_PARAMS['order_ids']
            order_ids = order_ids_string.split(',')
        except Exception, e:
            content = {'error': 'Order_ids is an array of order ids, is missing'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        
        today = datetime.now()

        delete_orders = []
        for order_id in order_ids:
            order = get_object_or_404(Order, pk = order_id)
            all_statuses = order.delivery_status.all()
            for delivery_status in all_statuses:
                if delivery_status.date.year == today.year and delivery_status.date.month == today.month and delivery_status.date.day == today.day:
                    delete_orders.append(delivery_status)
                
        for delivery_status in delete_orders:
            delivery_status.delete()
        content = {'description': 'Deleted Successfully'}
        return Response(content, status = status.HTTP_200_OK)
    
    @detail_route(methods=['post'])
    def exclude_dates(self, request, pk):
        order = get_object_or_404(Order, pk = pk)
        try:
            exclude_dates = request.data['exclude_dates']    
        except Exception, e:
            content = {'error': 'exclude_dates is an array of dates, is missing'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        is_deleted = False
        for exclude_date_string in exclude_dates:
            exclude_date = parse_datetime(exclude_date_string)

            all_deliveries = order.delivery_status.all()
            for delivery in all_deliveries:
                
                if delivery.date.date() == exclude_date.date():
                    delivery.delete()
                    is_deleted = True
                    break
        
        if is_deleted is True:
            content = {'description': 'Deleted Successfully'}
            return Response(content, status = status.HTTP_200_OK)
        else:
            content = {'error': 'Date not found'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def picked_up(self, request, pk=None):
        dg = get_object_or_404(DeliveryGuy, user = request.user)
        order = get_object_or_404(Order, pk = pk)        

        order.order_status = constants.ORDER_STATUS_INTRANSIT
        order.delivery_guy = dg

        # PICKEDUP DATE TIME
        pickedup_datetime_string = request.data.get('pickedup_datetime')
        if pickedup_datetime_string is not None:
            pickedup_datetime = parse_datetime(pickedup_datetime_string) 
        else:
            pickedup_datetime = datetime.now() 

        order.pickedup_datetime = pickedup_datetime    
        order.save()
        
        #UPDATING THE DELIVERY STATUS OF THE PARTICULAR DAY
        delivery_statuses = order.delivery_status.all()
        for delivery_status in delivery_statuses:

            date_1 = datetime.combine(pickedup_datetime, time()).replace(hour=0, minute=0, second=0)
            date_2 = datetime.combine(delivery_status.date, time()).replace(hour=0, minute=0, second=0)

            if date_1 == date_2:
                delivery_status.order_status = constants.ORDER_STATUS_INTRANSIT
                delivery_status.pickedup_datetime = pickedup_datetime
                delivery_status.save()
                break

        # UPDATE DG STATUS
        dg.status = constants.DG_STATUS_BUSY
        dg.save()
        update_pending_count(dg)

        content = {'description': 'Order updated'}
        return Response(content, status = status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def delivered(self, request, pk=None):

        dg = get_object_or_404(DeliveryGuy, user = request.user)
        order = get_object_or_404(Order, pk = pk)        

        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        is_cod_collected = request.data.get('cod_collected')

        # DELIVERED DATE TIME
        delivered_datetime_string = request.data.get('delivered_datetime')
        if delivered_datetime_string is not None:
            delivered_datetime = parse_datetime(delivered_datetime_string) 
        else:
            delivered_datetime = datetime.now()

        try:
            delivered_at = request.data['delivered_at'] 
        except:
            content = {'error':' delivered_at value is missing or wrong. Options: DOOR_STEP, SECURITY, RECEPTION, CUSTOMER, ATTEMPTED'}    
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        if delivered_at == constants.ORDER_STATUS_ATTEMPTED:
            order_status = constants.ORDER_STATUS_ATTEMPTED
            delivered_at = constants.ORDER_STATUS_NOT_DELIVERED
        else:
            order_status = constants.ORDER_STATUS_DELIVERED

        order.order_status = order_status
        order.delivered_at = delivered_at
        order.completed_datetime = delivered_datetime
        order.save()
        
        # UPDATE THE DELIVERY STATUS OF THE PARTICULAR DAY
        delivery_statuses = order.delivery_status.all()
        for delivery_status in delivery_statuses:
            date_1 = datetime.combine(delivered_datetime, time()).replace(hour=0, minute=0, second=0)
            date_2 = datetime.combine(delivery_status.date, time()).replace(hour=0, minute=0, second=0)

            if date_1 == date_2:
                delivery_status.order_status = order_status
                delivery_status.delivered_at = delivered_at
                delivery_status.completed_datetime = delivered_datetime
                if is_cod_collected is not None:
                    delivery_status.is_cod_collected = is_cod_collected
                delivery_status.save()
                break
                                       
        # UPDATE DG STATUS
        dg.status = constants.DG_STATUS_AVAILABLE
        dg.save()
        update_pending_count(dg)

        # CONFIRMATION MESSAGE TO CUSTOMER
        message = constants.ORDER_DELIVERED_MESSAGE_CLIENT.format(order_status, order.consumer.user.first_name, delivered_at)
        send_sms(order.vendor.phone_number, message)

        # UPDATE CUSTOMER LOCATION
        if order_status == constants.ORDER_STATUS_DELIVERED and latitude is not None and longitude is not None:            
            address_id = order.delivery_address.id
            address = get_object_or_404(Address, pk = address_id)        
            address.latitude = latitude
            address.longitude = longitude
            address.save()

        content = {'description': 'Order updated'}
        return Response(content, status = status.HTTP_200_OK)

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
            content = {'error':'dg_id and order_ids list are Mandatory'}    
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        
        dg = get_object_or_404(DeliveryGuy, id = dg_id)
        
        for order_id in order_ids:
            order = get_object_or_404(Order, id = order_id)

            #UPDATING THE DELIVERY STATUS OF THE PARTICULAR DAY
            delivery_statuses = order.delivery_status.all()
            for delivery_status in delivery_statuses:

                assign_date = datetime.combine(date, time()).replace(hour = 0, minute = 0, second = 0)
                delivery_date = datetime.combine(delivery_status.date, time()).replace(hour = 0, minute = 0, second = 0)
                
                if delivery_date >= assign_date:
                    delivery_status.delivery_guy = dg
                    if delivery_status.order_status == constants.ORDER_STATUS_PLACED:
                        delivery_status.order_status = constants.ORDER_STATUS_QUEUED
                    delivery_status.save()
                                       
            order.delivery_guy = dg
            order.save()
        
        dg.status = constants.DG_STATUS_BUSY
        dg.save()
        update_pending_count(dg)

        # SEND PUSH NOTIFICATION TO DELIVERYGUY
        data = {
                'message':'A new order has been assigned to you.', 
                'type': 'order_assigned',
                'data':{
                    'order_id': order.id 
                    }
                }
        send_push(dg.device_token, data)
        
        # TODO: Need to revisit and understand whether we need to send 100 SMS if there are 100 orders.
        # CONFIRMATION MESSAGE TO CUSTOMER
        # message = 'A DeliveryGuy has been assigned for your order. He will be arriving soon - Team YourGuy'
        # send_sms(vendor.phone_number, message)

        content = {'description': 'Order assigned'}
        return Response(content, status = status.HTTP_200_OK)
    
    @detail_route(methods=['post'])
    def approve(self, request, pk ):
        try:
            date_string = request.data['date']
            date = parse_datetime(date_string)
        except Exception, e:
            content = {'error':'Incomplete params', 'description':'date'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        order = get_object_or_404(Order, id = pk)

        #UPDATING THE DELIVERY STATUS OF THE PARTICULAR DAY
        delivery_statuses = order.delivery_status.all()
        for delivery_status in delivery_statuses:

            date_1 = datetime.combine(date, time()).replace(hour=0, minute=0, second=0)
            date_2 = datetime.combine(delivery_status.date, time()).replace(hour=0, minute=0, second=0)

            if date_1 == date_2:
                delivery_status.order_status = constants.ORDER_STATUS_QUEUED
                delivery_status.save()
                break
        

        message = constants.ORDER_APPROVED_MESSAGE_CLIENT.format(order.consumer.user.first_name)
        send_sms(order.vendor.phone_number, message)

        return Response(status = status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def reject(self, request, pk ):
        try:
            reason_message = request.data['rejection_reason']
            date_string = request.data['date']
            date = parse_datetime(date_string)

        except Exception, e:
            content = {'error':'Incomplete params', 'description':'rejection_reason, date'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        order = get_object_or_404(Order, id = pk)

        #UPDATING THE DELIVERY STATUS OF THE PARTICULAR DAY
        delivery_statuses = order.delivery_status.all()
        for delivery_status in delivery_statuses:

            date_1 = datetime.combine(date, time()).replace(hour=0, minute=0, second=0)
            date_2 = datetime.combine(delivery_status.date, time()).replace(hour=0, minute=0, second=0)

            if date_1 == date_2:
                delivery_status.order_status = constants.ORDER_STATUS_REJECTED
                delivery_status.rejection_reason = reason_message
                delivery_status.save()
                break
        
        message = constants.ORDER_REJECTED_MESSAGE_CLIENT.format(order.consumer.user.first_name, reason_message)
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
    