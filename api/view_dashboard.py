from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group
from django.utils.dateparse import parse_datetime
from django.db.models import Q

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.decorators import api_view

from yourguy.models import Order, OrderDeliveryStatus, Consumer, Vendor, DeliveryGuy, Area, VendorAgent, Address, Product, OrderItem, User
from datetime import datetime, timedelta, time
from api.views import user_role, is_userexists, is_vendorexists, is_dgexists, is_address_exists, days_in_int, send_sms, normalize_offset_awareness, ist_day_start, ist_day_end
from api.views import ist_datetime

import constants
import json

import recurrence
from datetime import datetime
from dateutil.rrule import rrule, DAILY
from django.db.models import Sum

def calculate_customers(vendor):
	return 0

@api_view(['POST'])
def vendor_dashboard(request):

	authentication_classes = [authentication.TokenAuthentication]
	permission_classes = [IsAuthenticated]

	# INPUT PARAMETERS ---------------------------------------------
	try:
		start_date_string = request.data['start_date']
		end_date_string = request.data['end_date']	
		
		start_date = parse_datetime(start_date_string)
		start_date = ist_day_start(start_date)
		
		end_date = parse_datetime(end_date_string)
		end_date = ist_day_end(end_date)
	
	except Exception, e:
		content = {'error':'Error in params: start_date, end_date'}
		return Response(content, status = status.HTTP_400_BAD_REQUEST)
	# ---------------------------------------------------------------	

	# VENDOR INPUTS ---------------------------------------------------
	vendor = None
	role = user_role(request.user)
	if role == constants.VENDOR:
		vendor_agent = get_object_or_404(VendorAgent, user = request.user)
		vendor = vendor_agent.vendor
	else:
		vendor_id = request.data.get('vendor_id')
		if vendor_id is not None:
			vendor = get_object_or_404(Vendor, pk = vendor_id)
		else:
			pass	
	# --------------------------------------------------------------------

	# VENDOR FILTERING ---------------------------------------------------
	if vendor is not None:
		delivery_status_queryset = OrderDeliveryStatus.objects.filter(order__vendor = vendor)
	else:
		delivery_status_queryset = OrderDeliveryStatus.objects.all()
	# --------------------------------------------------------------------

	# TOTAL COD COLLECTED ------------------------------------------------------------
	cod_collected_dict = delivery_status_queryset.filter(date__gte = start_date, date__lte = end_date).aggregate(cod_collected = Sum('cod_collected_amount'))
	cod_collected = cod_collected_dict['cod_collected']
	# ------------------------------------------------------------------------------

	# DATE FILTERING ---------------------------------------------------------------
	delivery_status_queryset = delivery_status_queryset.filter(date__gte = start_date, date__lte = end_date)
	# ------------------------------------------------------------------------------
	
	# TOTAL COD TO BE COLLECTED -----------------------------
	total_cod_dict = Order.objects.filter(delivery_status = delivery_status_queryset).aggregate(total_cod = Sum('cod_amount'))
	total_cod = total_cod_dict['total_cod']
    # ------------------------------------------------------------------------------

	# ORDER STATUS FILTERING -------------------------------------------------------
	total_orders = delivery_status_queryset.count()
	total_orders_executed = delivery_status_queryset.filter(Q(order_status = 'DELIVERED') | Q(order_status = 'DELIVERYATTEMPTED') | Q(order_status = 'PICKUPATTEMPTED')).count()
	# ------------------------------------------------------------------------------

	# CREATE DATE RULE -----------------------------------------------------------
	rule_daily = rrule(DAILY, dtstart = start_date, until = end_date)
	alldates = list(rule_daily)
	# ----------------------------------------------------------------------------

	# FOR ORDER COUNT FOR INDIVIDUAL DATES -----------------------------------------
	fullday_timedelta = timedelta(hours=23, minutes=59)
	orders_graph = []
	for date in alldates:
		day_start = date
		day_end = day_start + fullday_timedelta

		delivery_status_per_date = delivery_status_queryset.filter(date__gte = day_start, date__lte = day_end)
		
		total_orders_per_day = delivery_status_per_date.count()
		orders_delivered_count = delivery_status_per_date.filter(Q(order_status = 'DELIVERED')).count()
		orders_delivered_attempted_count = delivery_status_per_date.filter(Q(order_status = 'DELIVERYATTEMPTED')).count()
		orders_pickup_attempted_count = delivery_status_per_date.filter(Q(order_status = 'PICKUPATTEMPTED')).count()
		orders_cancelled_count = delivery_status_per_date.filter(Q(order_status = 'CANCELLED')).count()
		orders_undelivered_count = delivery_status_per_date.filter(Q(order_status = 'ORDER_PLACED') | Q(order_status = 'QUEUED')).count()
		orders_intransit_count = delivery_status_per_date.filter(Q(order_status = 'INTRANSIT')).count()

		result = {
		'date': ist_datetime(date).date(),
		'orders_placed_count':total_orders_per_day, 
		'orders_delivered_count':orders_delivered_count,
		'delivery_attempted_count':orders_delivered_attempted_count,
		'pickup_attempted_count':orders_pickup_attempted_count,
		'cancelled_count':orders_cancelled_count,
		'queued_count':orders_undelivered_count,
		'intransit_count':orders_intransit_count
		}
		orders_graph.append(result)
	# ------------------------------------------------------------------------------

	# CUSTOMERS FOR VENDOR ---------------------------------------------------------
	queryset_consumers = Consumer.objects.filter(created_date__gte = start_date, created_date__lte = end_date)
	if vendor is not None:
		queryset_consumers = queryset_consumers.filter(associated_vendor = vendor)
	
	new_customers_count = queryset_consumers.count()
	# ------------------------------------------------------------------------------
	
	content = {
	'orders':orders_graph,
	'total_orders_placed':total_orders,
	'total_orders_delivered':total_orders_executed,
	'total_cod_amount':total_cod,
	'total_cod_collected':cod_collected,
	'new_customers': new_customers_count,
	'total_orders_cancelled':0,
	'total_sales':0,
	}
	return Response(content, status = status.HTTP_200_OK)