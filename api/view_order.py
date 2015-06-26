from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group
from django.utils.dateparse import parse_datetime

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from yourguy.models import Order, OrderDeliveryStatus, Consumer, Vendor, DeliveryGuy, Area, VendorAgent, Address, Product, OrderItem
from datetime import datetime, timedelta, time
from api.serializers import OrderSerializer
from api.views import user_role, is_vendorexists, is_consumerexists, is_dgexists, days_in_int, send_sms, normalize_offset_awareness
import constants
import recurrence
from itertools import chain

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
        return get_object_or_404(Order, id = pk)

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `consumer_id` or 'vendor_id' query parameter in the URL.
        """ 
        queryset = Order.objects.all()
        vendor_id = self.request.QUERY_PARAMS.get('vendor_id', None)
        area_code = self.request.QUERY_PARAMS.get('area_code', None)
        consumer_phone_number = self.request.QUERY_PARAMS.get('consumer_phone_number', None)
        dg_phone_number = self.request.QUERY_PARAMS.get('dg_phone_number', None)
        date_string = self.request.QUERY_PARAMS.get('date', None)

        role = user_role(self.request.user)

        if role == constants.VENDOR:
            vendor_agent = get_object_or_404(VendorAgent, user = self.request.user)
            queryset = queryset.filter(vendor=vendor_agent.vendor)

        elif role == constants.CONSUMER:
            consumer = get_object_or_404(Consumer, user = self.request.user)
            queryset = queryset.filter(consumer=consumer)
        
        elif role == constants.DELIVERY_GUY:
            delivery_guy = get_object_or_404(DeliveryGuy, user = self.request.user)
            queryset = queryset.filter(delivery_guy = delivery_guy)
        
        else:
            # OPERATIONS FILTERING ----
            
            # 1. FILTERING BY vendor_id                
            if vendor_id is not None:
                if is_vendorexists(vendor_id):
                    vendor = get_object_or_404(Vendor, id = vendor_id)
                    queryset = queryset.filter(vendor=vendor)
                else:
                    pass
            else:
                pass
            
            #2. FILTERING BY consumer_phone_number
            if consumer_phone_number is not None:
                if is_consumerexists(consumer_phone_number):
                    user = get_object_or_404(User, username = consumer_phone_number)
                    consumer = get_object_or_404(consumer, user = user)
                    queryset = queryset.filter(consumer=consumer)
                else:
                    pass
            else:
                pass
        
            # FILTERING BY ASSIGNED DELIVERY GUY ----
            if dg_phone_number is not None:
                if is_dgexists:
                    user = get_object_or_404(User, username = dg_phone_number)
                    queryset = queryset.filter(assigned_deliveryGuy=user)
                else:
                    pass
            else:
                pass        

            # FILTERING BY  area_code ---
            area_code = self.request.QUERY_PARAMS.get('area_code', None)
            if area_code is not None:
                area = get_object_or_404(Area, area_code = area_code)
                queryset = queryset.filter(delivery_address__area=area)

        # FILTERING BY DATE -----
        if date_string is not None:
            date = parse_datetime(date_string)
        else:
            date = datetime.today()
        day_start = datetime.combine(date, time()).replace(hour=0, minute=0, second=0)
        day_end = datetime.combine(date, time()).replace(hour=23, minute=59, second=59)

        # FILTERING BY RECURRING ORDERS
        recurring_queryset = queryset.filter(is_recurring=True)
        recurring_orders = []
        for order in recurring_queryset:            
            dates = order.recurrences.between(day_start, day_end,inc=True)
            if len(list(dates)) > 0:
                recurring_orders.append(order)

        # FILTERING SINGLE ORDER
        non_recurring_queryset = queryset.filter(is_recurring=False, delivery_datetime__lte=day_end, delivery_datetime__gte=day_start)

        # COMBINING RECURRING + SINGLE ORDERS
        result = list(chain(non_recurring_queryset, recurring_orders))

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
                    new_order.order_status = 'QUEUED'

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
                    new_order.delivery_status.add(delivery_status)

                if vendor_order_id is not None:
                    new_order.vendor_order_id = vendor_order_id

                if total_cost is not None:
                    new_order.total_cost = total_cost

                new_order.save()

            # CONFIRMATION MESSAGE TO OPS
            message = 'A New order has been placed by {}, please assign a DG.'.format(vendor.store_name)
            send_sms(constants.OPS_PHONE_NUMBER, message)

            # CONFIRMATION MESSAGE TO CUSTOMER
            message = 'Your order has been placed and will be processed soon - Team YourGuy'
            send_sms(vendor.phone_number, message)

            content = {'status':'orders added'}
            return Response(content, status = status.HTTP_201_CREATED)
            
        except Exception, e:
            content = {'error':'Unable to create orders with the given details'}    
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

    #def update(self, request, pk=None):
        # import pdb
        # pdb.set_trace()
        # print 'update'
    
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
            print exclude_date

            all_deliveries = order.delivery_status.all()
            for delivery in all_deliveries:
                print delivery.date
                
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

        order.order_status = 'INTRANSIT'
        order.delivery_guy = dg

        # PICKEDUP DATE TIME
        pickedup_datetime = request.data.get('pickedup_datetime')
        if pickedup_datetime is not None:
            order.pickedup_datetime = parse_datetime(pickedup_datetime) 
        else:
            order.pickedup_datetime = datetime.now() 
        order.save()
        
        
        dg.status = 'BUSY'
        dg.save()

        content = {'description': 'Order updated'}
        return Response(content, status = status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def delivered(self, request, pk=None):
        dg = get_object_or_404(DeliveryGuy, user = request.user)
        order = get_object_or_404(Order, pk = pk)        

        order.order_status = 'DELIVERED'
        order.completed_datetime = datetime.now()

        try:
            delivered_at = request.data['delivered_at']
            order.delivered_at = delivered_at   
        except:
            content = {'error':' delivered_at value is missing or wrong. Options: DOOR_STEP, SECURITY, RECEPTION, CUSTOMER, ATTEMPTED'}    
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        order.save()
        
        # DELIVERED DATE TIME
        delivered_datetime = request.data.get('delivered_datetime')
        if delivered_datetime is not None:
            order.delivered_datetime = parse_datetime(delivered_datetime) 
        else:
            order.delivered_datetime = datetime.now() 


        dg.status = 'AVAILABLE'
        dg.save()

        # CONFIRMATION MESSAGE TO CUSTOMER
        message = 'Your order has been delivered to {} at {} - Team YourGuy'.format(order.consumer.user.first_name, delivered_at)
        send_sms(order.vendor.phone_number, message)

        content = {'description': 'Order updated'}
        return Response(content, status = status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def assign_order(self, request, pk=None):
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

            # UPDATING THE DELIVERY STATUS OF THE PARTICULAR DAY
            # delivery_statuses = order.delivery_status.all()
            # for delivery_status in delivery_statuses:
            #     date = normalize_offset_awareness(date, delivery_status.date)
            #     if delivery_status.date.replace(hour=0, minute=0, second=0, microsecond=0) == date.replace(hour=0, minute=0, second=0, microsecond=0):
            #         delivery_status.delivery_guy = dg
            #         delivery_status.save()
                                       
            order.delivery_guy = dg
            order.order_status = 'QUEUED'
            order.save()
        
        dg.status = 'BUSY'
        dg.save()

        # TODO: Need to revisit and understand whether we need to send 100 SMS if there are 100 orders.
        # CONFIRMATION MESSAGE TO CUSTOMER
        # message = 'A DeliveryGuy has been assigned for your order. He will be arriving soon - Team YourGuy'
        # send_sms(vendor.phone_number, message)

        content = {'description': 'Order assigned'}
        return Response(content, status = status.HTTP_200_OK)

    @list_route()
    def undelivered_orders():
        orders = Order.objects.filter(order_status='INTRANSIT')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)        

    @list_route()
    def unassigned_orders():
        orders = Order.objects.filter(assigned_deliveryGuy= None)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)        
    