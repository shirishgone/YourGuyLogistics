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
from api.views import user_role, is_userexists, is_vendorexists, is_consumerexists, is_dgexists, is_address_exists, days_in_int, send_sms, normalize_offset_awareness

import constants
import json

import recurrence
from datetime import datetime
from dateutil.rrule import rrule, DAILY

def calculate_customers(vendor):
	return 0

@api_view(['POST'])
def vendor_dashboard(request):
	authentication_classes = [authentication.TokenAuthentication]
	permission_classes = [IsAuthenticated]

	try:
		start_date_string = request.data['start_date']
		end_date_string = request.data['end_date']	
		
		start_date = parse_datetime(start_date_string)
		end_date = parse_datetime(end_date_string)
	except Exception, e:
		content = {'error':'Missing params. start_date and end_date'}
		return Response(content, status = status.HTTP_400_BAD_REQUEST)

	role = user_role(request.user)
	if (role == constants.VENDOR or role == constants.OPERATIONS):
		total_orders_placed = 0
		total_orders_delivered = 0
		total_orders_cancelled = 0

		total_cod_amount = 0
		total_sales = 0
		orders_graph = []

		# CREATE DATE RULE ==================
		rule_daily = rrule(DAILY, dtstart=start_date, until=end_date)
		alldates = list(rule_daily)
		
		# QUERY SET ==================
		if role == constants.VENDOR:
			vendor_agent = get_object_or_404(VendorAgent, user = request.user)
			vendor = vendor_agent.vendor
			queryset = OrderDeliveryStatus.objects.filter(order__vendor__id = vendor.id, date__gte = start_date, date__lte = end_date)
		elif role == constants.OPERATIONS:
			queryset = OrderDeliveryStatus.objects.filter(date__gte = start_date, date__lte = end_date)
		else:
			content = {'error':'You dont have permissions.'}
			return Response(content, status = status.HTTP_400_BAD_REQUEST)
		
		total_orders_placed = queryset.count()
		cancelled_queryset = queryset.filter(Q(order_status='CANCELLED') | Q(order_status='REJECTED'))
		total_orders_cancelled = cancelled_queryset.count()

		delivered_queryset = queryset.filter(Q(order_status='DELIVERED') | Q(order_status='ATTEMPTED'))
		total_orders_delivered = delivered_queryset.count()

		# FOR ORDER COUNT FOR INDIVIDUAL DATES ==================
		for date in alldates:
			delivery_status_per_date = queryset.filter(date__year = date.year, 
				date__month = date.month, 
				date__day = date.day)
			orders_placed_count = delivery_status_per_date.count()

			delivery_status_delivered_queryset = delivery_status_per_date.filter(Q(order_status = 'DELIVERED') | Q(order_status = 'ATTEMPTED'))
			orders_delivered_count = delivery_status_delivered_queryset.count()
			
			result = {
			'orders_placed_count':orders_placed_count, 
			'orders_delivered_count':orders_delivered_count,
			'date': date.date()
			}

			orders_graph.append(result)

			for delivery_status in delivery_status_delivered_queryset:
				try:
					order = Order.objects.filter(delivery_status = delivery_status).latest('pickup_datetime')	
				except Exception, e:
					continue
				
				total_cod_amount = total_cod_amount + order.cod_amount
				total_sales = total_sales + order.total_cost

		new_consumers_count = Consumer.objects.filter(associated_vendor = vendor, user__date_joined__gte = start_date, user__date_joined__lte = end_date).count()		
		content = {
		'new_customers': new_consumers_count,
		'total_orders_placed':total_orders_placed,
		'total_orders_delivered':total_orders_delivered,
		'total_orders_cancelled':total_orders_cancelled,
		'total_cod_amount':total_cod_amount,
		'total_sales':total_sales,
		'orders':orders_graph 
		}
		
		return Response(content, status = status.HTTP_200_OK)
	else:
		content = {'error':'Only vendors can access their analytics.'}
		return Response(content, status = status.HTTP_400_BAD_REQUEST)