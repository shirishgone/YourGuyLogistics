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
	if role == constants.VENDOR:
		total_order_count = 0
		total_cod_amount = 0
		total_sales = 0
		orders_count_per_date = []

		vendor_agent = get_object_or_404(VendorAgent, user = request.user)
		vendor = vendor_agent.vendor

		# CREATE DATE RULE ==================
		rule = recurrence.Rule(recurrence.DAILY)
		pattern = recurrence.Recurrence(
			dtstart = start_date,
			dtend = end_date,
			rrules = [rule,]
			)
		alldates = pattern.occurrences()

		# QUERY SET ==================
		queryset = OrderDeliveryStatus.objects.filter(order__vendor__id = vendor.id, date__gte = start_date, date__lte = end_date)
		queryset = queryset.filter(Q(order_status='DELIVERED') | Q(order_status='ATTEMPTED'))
		
		total_order_count = queryset.count()

		# FOR ORDER COUNT FOR INDIVIDUAL DATES ==================
		for date in alldates:
			delivery_status_per_date = queryset.filter(date__year = date.year, 
				date__month = date.month, 
				date__day = date.day)

			count = delivery_status_per_date.count()
			result = {'count':count, 'date': date.date()}
			orders_count_per_date.append(result)
			
		content = { 'total_order_count':total_order_count, 'orders':orders_count_per_date }
		return Response(content, status = status.HTTP_200_OK)
	else:
		content = {'error':'Only vendors can access their analytics.'}
		return Response(content, status = status.HTTP_400_BAD_REQUEST)