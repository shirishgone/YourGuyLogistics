from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group
from django.utils.dateparse import parse_datetime

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from yourguy.models import Order, Consumer, Vendor, DeliveryGuy, Area, VendorAgent, Address, Product, OrderItem
from datetime import datetime, timedelta, time
from api.serializers import OrderSerializer
from api.views import user_role, is_vendorexists, is_consumerexists, is_dgexists
import constants

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
            day_start = datetime.combine(date, time())
            next_day = day_start + timedelta(1)
            day_end = datetime.combine(next_day, time())
            queryset = queryset.filter(delivery_datetime__lte=day_end, delivery_datetime__gte=day_start)
        else:
            date = datetime.today()
            day_start = datetime.combine(date, time())
            next_day = day_start + timedelta(1)
            day_end = datetime.combine(next_day, time())
            queryset = queryset.filter(delivery_datetime__lte=day_end, delivery_datetime__gte=day_start)
        
        return queryset

    
    def create(self, request):
        try:
            pickup_datetime = request.data['pickup_datetime']
            delivery_datetime = request.data['delivery_datetime']
            
            pickup_address_id = request.data['pickup_address_id']
            delivery_address_id = request.data['delivery_address_id']

            vendor_id = request.data['vendor_id']
            consumer_id = request.data['consumer_id']
           
            order_items = request.data['order_items']
            
            total_cost = request.data.get('total_cost')
            vendor_order_id = request.data.get('vendor_order_id')
        except Exception, e:
            print e
            content = {'error':'Incomplete params', 'description':'pickup_datetime, products, delivery_datetime, pickup_address_id, delivery_address_id , vendor_id, consumer_id, product_id, quantity, total_cost'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        try:
            vendor = get_object_or_404(Vendor, pk = vendor_id)
            consumer = get_object_or_404(Consumer, pk = consumer_id)

            pickup_address = get_object_or_404(Address, pk = pickup_address_id)
            delivery_address = get_object_or_404(Address, pk = delivery_address_id)
            
            pickup_datetime = parse_datetime(pickup_datetime)
            delivery_datetime = parse_datetime(delivery_datetime)

        except Exception, e:
            print e
            content = {'error':' Wrong object ids'}    
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        try:
            new_order = Order.objects.create(created_by_user = request.user, vendor = vendor, consumer = consumer, pickup_address = pickup_address, delivery_address = delivery_address, pickup_datetime = pickup_datetime, delivery_datetime = delivery_datetime)
            for item in order_items:
                product_id = item['product_id']
                quantity = item ['quantity']
                product = get_object_or_404(Product, pk = product_id)
                order_item = OrderItem.objects.create(product = product, quantity = quantity)
                new_order.order_items.add(order_item)

            if vendor_order_id is not None:
                new_order.vendor_order_id = vendor_order_id

            if total_cost is not None:
                new_order.total_cost = total_cost
            
            new_order.save()

            content = {'order_id':new_order.id}
            return Response(content, status = status.HTTP_201_CREATED)
            
        except Exception, e:
            content = {'error':'Unable to create order with the given details'}    
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

    #def update(self, request, pk=None):
        # import pdb
        # pdb.set_trace()
        # print 'update'

    @detail_route(methods=['post'])
    def picked_up(self, request, pk=None):
        dg = get_object_or_404(DeliveryGuy, user = request.user)
        order = get_object_or_404(Order, pk = pk)        

        order.order_status = 'INTRANSIT'
        order.delivery_guy = dg
        order.pickedup_datetime = datetime.now() 
        order.save()
        
        dg.status = 'BUSY'
        dg.save()

        content = {'description': 'Order updated'}
        return Response(content, status = status.HTTP_201_CREATED)

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
        dg.status = 'AVAILABLE'
        dg.save()
        content = {'description': 'Order updated'}
        return Response(content, status = status.HTTP_201_CREATED)

    @detail_route(methods=['post'])
    def assign_order(self, request, pk=None):
        dg_id = request.POST['dg_id']
        order_id = request.POST['order_id']
        order = get_object_or_404(Order, id = order_id)
        dg = get_object_or_404(DeliveryGuy, id = dg_id)
        dg.availability = 'BUSY'
        dg.save()

        order.assigned_to = dg.user
        order.save()
        
        content = {'description': 'Order assigned'}
        return Response(content, status = status.HTTP_201_CREATED)

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
    