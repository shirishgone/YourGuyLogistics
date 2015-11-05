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
from api.views import user_role, is_userexists, is_vendorexists, is_consumerexists, is_dgexists, is_address_exists, days_in_int, send_sms, normalize_offset_awareness, ist_day_start, ist_day_end

import constants
import json

import recurrence
from datetime import datetime
from dateutil.rrule import rrule, DAILY
from django.db.models import Sum
from django.db.models import Prefetch


@api_view(['POST'])
def excel_download(request):
	authentication_classes = [authentication.TokenAuthentication]
	permission_classes = [IsAuthenticated]

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

	# VENDOR FILTERING -----------------------------------------------------------
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

	if vendor is not None:
		delivery_status_queryset = OrderDeliveryStatus.objects.filter(order__vendor = vendor).select_related('delivery_guy__user')
	else:
		delivery_status_queryset = OrderDeliveryStatus.objects.all().select_related('delivery_guy__user')
	# # ------------------------------------------------------------------------------
	
	# DATE FILTERING ---------------------------------------------------------------
	delivery_status_queryset = delivery_status_queryset.filter(date__gte = start_date, date__lte = end_date).prefetch_related(
		Prefetch('order_set', queryset = Order.objects.select_related('consumer__user') , to_attr='orders'))
	# ------------------------------------------------------------------------------

	# CONSTRUCTING RESPONSE ---------------------------------------------------------------
	excel_order_details = []
	for delivery_status in delivery_status_queryset:
		try:
			order = delivery_status.orders.pop()
			excel_order = {
			'date':delivery_status.date,
			'order_id':order.id,
			'customer_name':order.consumer.user.first_name,
			'customer_phone_number':order.consumer.user.username,
			'cod_amount':order.cod_amount,
			'cod_collected':delivery_status.cod_collected_amount,
			'cod_reason':delivery_status.cod_remarks,
			'status':delivery_status.order_status
			}
			if role == constants.OPERATIONS:
				if delivery_status.delivery_guy is not None:
					excel_order['delivery_guy'] = delivery_status.delivery_guy.user.first_name
				else: 	
					excel_order['delivery_guy'] = None
			
			excel_order_details.append(excel_order)
		except Exception, e:
			pass
	# # ------------------------------------------------------------------------------
	content = {
	'orders':excel_order_details
	}
	return Response(content, status = status.HTTP_200_OK)

@api_view(['POST'])
def report(request):
	authentication_classes = [authentication.TokenAuthentication]
	permission_classes = [IsAuthenticated]

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
	
	# CREATE DATE RULE -----------------------------------------------------------
	rule_daily = rrule(DAILY, dtstart = start_date, until = end_date)
	alldates = list(rule_daily)
	# ----------------------------------------------------------------------------

	# VENDOR FILTERING -----------------------------------------------------------
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

	if vendor is not None:
		delivery_status_queryset = OrderDeliveryStatus.objects.filter(order__vendor = vendor)
	else:
		delivery_status_queryset = OrderDeliveryStatus.objects.all()
	# # ------------------------------------------------------------------------------

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
	total_orders_delivered = delivery_status_queryset.filter(Q(order_status = 'DELIVERED') | Q(order_status = 'DELIVERYATTEMPTED') | Q(order_status = 'PICKUPATTEMPTED')).count()
	# ------------------------------------------------------------------------------

	# FOR ORDER COUNT FOR INDIVIDUAL DATES -----------------------------------------
	orders_graph = []
	for date in alldates:
		day_start = ist_day_start(date)
		day_end = ist_day_end(date)
		delivery_status_per_date = delivery_status_queryset.filter(date__gte = day_start, date__lte = day_end)
		
		total_orders_per_day = delivery_status_per_date.count()
		orders_delivered_count = delivery_status_per_date.filter(Q(order_status = 'DELIVERED')).count()
		orders_delivered_attempted_count = delivery_status_per_date.filter(Q(order_status = 'DELIVERYATTEMPTED')).count()
		orders_pickup_attempted_count = delivery_status_per_date.filter(Q(order_status = 'PICKUPATTEMPTED')).count()
		orders_cancelled_count = delivery_status_per_date.filter(Q(order_status = 'CANCELLED')).count()
		orders_undelivered_count = delivery_status_per_date.filter(Q(order_status = 'ORDER_PLACED') | Q(order_status = 'QUEUED')).count()
		orders_intransit_count = delivery_status_per_date.filter(Q(order_status = 'INTRANSIT')).count()

		result = {
		'total_orders_count':total_orders_per_day, 
		'delivered_count':orders_delivered_count,
		'delivery_attempted_count':orders_delivered_attempted_count,
		'pickup_attempted_count':orders_pickup_attempted_count,
		'cancelled_count':orders_cancelled_count,
		'queued_count':orders_undelivered_count,
		'intransit_count':orders_intransit_count,
		'date': date.date()
		}
		orders_graph.append(result)
	# ------------------------------------------------------------------------------
	
	content = {
	'total_orders':total_orders,
	'total_orders_delivered':total_orders_delivered,
	'total_cod':total_cod,
	'cod_collected':cod_collected,
	'orders':orders_graph 
	}
	return Response(content, status = status.HTTP_200_OK)