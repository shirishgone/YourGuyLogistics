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

from yourguy.models import Order, Vendor, VendorAgent, OrderDeliveryStatus, Area, User, DeliveryGuy
from api.views import user_role, ist_day_start, ist_day_end
from api_v2.views import paginate

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import constants
from datetime import datetime, timedelta, time


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

def address_string(address):
    try:
        address_string = address.flat_number + ',' + address.building + ',' +  address.street + ',' 
        if address.area is not None:
            address_string = address_string +  address.area.area_name
    
        return address_string
    except Exception, e:
        print e
        return ''
    

def update_daily_status(order, date):
    delivery_status = delivery_status_of_the_day(order, date)
    if delivery_status is not None:

        res_order = {
            'id' : order.id,
            'pickup_datetime' : order.pickup_datetime,
            'delivery_datetime' : order.delivery_datetime,
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
            res_order['dg_name'] = delivery_status.delivery_guy.user.first_name

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

        # Access check for vendors
        role = user_role(request.user)
        if role == 'vendor':
            vendor_agent = get_object_or_404(VendorAgent, user = request.user)
            vendor = vendor_agent.vendor
            if order.vendor.id != vendor.id:
                content = {'error':'Access privileges', 'description':'You cant access other vendor orders'}
                return Response(content, status = status.HTTP_400_BAD_REQUEST)

        #TODO: Filter objects according to the permissions e.g VendorA shouldn't see orders of VendorB
        date_string = self.request.QUERY_PARAMS.get('date', None)
        if order.is_recurring is True:
            if date_string is None:
                content = {'error':'Insufficient params', 'description':'For recurring orders, date param in url is compulsory'}
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
            else:
                date = parse_datetime(date_string)   
        else:
            date = order.pickup_datetime
        
        result  = update_daily_status(order, date)
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

        orders = paginate(queryset, page)
        
        # UPDATING DELIVERY STATUS OF THE DAY
        result = []
        for single_order in orders:
            order = update_daily_status(single_order, date)
            if order is not None:
                result.append(order)        
        
        return Response(result, status = status.HTTP_200_OK)        
