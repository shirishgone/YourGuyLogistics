from yourguy.models import Order, Consumer, Vendor, DeliveryGuy, Area

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets

from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from datetime import datetime, timedelta, time
from api.serializers import OrderSerializer

from django.utils.dateparse import parse_datetime

from api.views import user_role

import constants

class OrderViewSet(viewsets.ModelViewSet):
    """
    Order viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = OrderSerializer

    def get_order(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except:
            raise Http404

    def get_vendor(self, pk):
        try:
            return Vendor.objects.get(pk=pk)
        except:
            raise Http404

    def get_consumer(self, pk):
        try:
            return Consumer.objects.get(pk=pk)
        except:
            raise Http404

    def get_deliveryguy(self, pk):
        try:
            return DeliveryGuy.objects.get(pk=pk)
        except:
            raise Http404

    def get_area(self, area_code):
        try:
            return Area.objects.get(area_code=area_code)
        except:
            raise Http404

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `consumer_id` or 'vendor_id' query parameter in the URL.
        """        
        queryset = Order.objects.all()
        vendor_id = self.request.QUERY_PARAMS.get('vendor_id', None)
        consumer_id = self.request.QUERY_PARAMS.get('consumer_id', None)
        dg_id = self.request.QUERY_PARAMS.get('dg_id', None)
        date_string = self.request.QUERY_PARAMS.get('date', None)

        role = user_role(self.request.user)

        if role == constants.VENDOR:
            vendor = Vendor.objects.get(user = self.request.user)
            vendor_id = vendor.id
        elif role == constants.CONSUMER:
            consumer = Consumer.objects.get(user = self.request.user)
            consumer_id = consumer.id
            vendor_id = None
        else:
            pass


        # filtering through vendor_id                
        if vendor_id is not None:
            vendor = self.get_vendor(vendor_id)
            queryset = queryset.filter(vendor=vendor)

        # filtering through consumer_id
        if consumer_id is not None:
            consumer = self.get_consumer(consumer_id)
            queryset = queryset.filter(consumer=consumer)

        # filtering through dg_id
        if dg_id is not None:
            dg = self.get_deliveryguy(dg_id)
            queryset = queryset.filter(assigned_to=dg.user)

        # filtering by date
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


        # filtering through area_code
        area_code = self.request.QUERY_PARAMS.get('area_code', None)
        if area_code is not None:
            area = self.get_area(area_code)
            queryset = queryset.filter(delivery_address__area=area)

        return queryset
    
    @detail_route(methods=['post'])
    def assign_order(self, request, pk=None):
        dg_id = request.POST['dg_id']
        order_id = request.POST['order_id']

        order = self.get_order(order_id)
        dg = self.get_deliveryguy(dg_id)
        
        dg.availability = 'BS'
        dg.save()

        order.assigned_to = dg.user
        order.save()
        
        content = {'description': 'Order assigned'}
        return Response(content, status = status.HTTP_201_CREATED)

    @list_route()
    def undelivered_orders():
        orders = Order.objects.filter(order_status='AS')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)        

    @list_route()
    def unassigned_orders():
        orders = Order.objects.filter(order_status='UN')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)        

    # @list_route()
    # def today_orders():    
    #     date = datetime.today
    #     day_start = datetime.combine(date, time())
    #     next_day = day_start + timedelta(1)
    #     day_end = datetime.combine(next_day, time())

    #     orders = Order.objects.filter(delivery_datetime__lte=day_end, delivery_datetime__gte=day_start)
    #     serializer = OrderSerializer(orders, many=True)
    #     return Response(serializer.data)        
