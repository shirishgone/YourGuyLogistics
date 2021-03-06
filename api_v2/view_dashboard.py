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
from api.views import user_role, is_userexists, is_vendorexists, is_dgexists, is_address_exists, days_in_int, send_sms, normalize_offset_awareness, ist_day_start, ist_day_end, ist_datetime

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
	delivery_status_queryset = delivery_status_queryset.filter(date__gte = start_date, date__lte = end_date).select_related('order')
	# ------------------------------------------------------------------------------
	
	if len(delivery_status_queryset) > 5000:
		content = {'error':'Too many records. Please check lesser dates'}
		return Response(content, status = status.HTTP_400_BAD_REQUEST)

	# CONSTRUCTING RESPONSE ---------------------------------------------------------------
	ist_timedelta = timedelta(hours=5, minutes=30)
	excel_order_details = []
	for delivery_status in delivery_status_queryset:
		try:
			date = delivery_status.date + ist_timedelta
			order = delivery_status.order
			excel_order = {
			'date':date.strftime('%d-%m-%Y'),
			'order_id':delivery_status.id,
			'customer_name':order.consumer.full_name,
			'customer_phone_number':order.consumer.phone_number,
			'cod_amount':order.cod_amount,
			'cod_collected':delivery_status.cod_collected_amount,
			'cod_reason':delivery_status.cod_remarks,
			'status':delivery_status.order_status,
			'vendor_notes':order.notes,
			'vendor_order_id':order.vendor_order_id
			}
			if role == constants.OPERATIONS:
				excel_order['vendor_name'] = order.vendor.store_name
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

	# DATE FILTERING ---------------------------------------------------------------
	delivery_status_queryset = delivery_status_queryset.filter(date__gte = start_date, date__lte = end_date)
	total_orders = delivery_status_queryset.filter(Q(order_status = 'QUEUED') | Q(order_status = 'INTRANSIT') | Q(order_status = 'DELIVERED') |  Q(order_status = 'DELIVERYATTEMPTED')).count()
	total_orders_executed = delivery_status_queryset.filter(Q(order_status = 'DELIVERED') | Q(order_status = 'DELIVERYATTEMPTED')).count()
	# ------------------------------------------------------------------------------

	# TOTAL COD TO BE COLLECTED -----------------------------
	executable_deliveries = delivery_status_queryset.filter(Q(order_status = 'QUEUED') | Q(order_status = 'INTRANSIT') | Q(order_status = 'DELIVERED'))
	total_cod_dict = executable_deliveries.aggregate(total_cod = Sum('order__cod_amount'))
	total_cod = total_cod_dict['total_cod']
    # ------------------------------------------------------------------------------

	# TOTAL COD COLLECTED ------------------------------------------------------------
	cod_collected_dict = delivery_status_queryset.filter(date__gte = start_date, date__lte = end_date).aggregate(cod_collected = Sum('cod_collected_amount'))
	cod_collected = cod_collected_dict['cod_collected']
	# ------------------------------------------------------------------------------
		
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

		ist_timedelta = timedelta(hours=5, minutes=30)
		display_date = date + ist_timedelta

		result = {
		'total_orders_count':total_orders_per_day, 
		'delivered_count':orders_delivered_count,
		'delivery_attempted_count':orders_delivered_attempted_count,
		'pickup_attempted_count':orders_pickup_attempted_count,
		'cancelled_count':orders_cancelled_count,
		'queued_count':orders_undelivered_count,
		'intransit_count':orders_intransit_count,
		'date': display_date.date()
		}
		orders_graph.append(result)
	# ------------------------------------------------------------------------------
	
	content = {
	'total_orders':total_orders,
	'total_orders_executed':total_orders_executed,
	'total_cod':total_cod,
	'cod_collected':cod_collected,
	'orders':orders_graph 
	}
	return Response(content, status = status.HTTP_200_OK)