from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from datetime import datetime, timedelta, time
from yourguy.models import Order, Address, Consumer, OrderDeliveryStatus
import json
from django.db.models import Q
from django.shortcuts import get_object_or_404
from yourguy.models import NotificationType, ServiceablePincode
from django.shortcuts import get_object_or_404
from yourguy.models import Employee

def ops_executive_for_pincode(pincode):
    serving_pincode = get_object_or_404(ServiceablePincode, pincode = pincode)
    employees = Employee.objects.filter(serving_pincodes__in = [serving_pincode])
    return employees

def ops_manager_for_dg(dg):
	employees = Employee.objects.filter(associate_delivery_guys__in = [dg])
	return employees

def notification_type_for_code(code):
	return get_object_or_404(NotificationType, code = code)

def is_correct_pincode(pincode):
	if pincode.isdigit() and len(pincode) == 6:
		return True
	else: 	
		return False

def is_pickup_time_acceptable(pickup_datetime):		
	current_datetime = datetime.now()
	if time(0, 0) <= pickup_datetime.time() <= time(16, 30) and pickup_datetime.date() >= current_datetime.date():
		return True
	else:
		return False

def is_vendor_has_same_address_already(vendor, pincode):
	try:
		addresses = vendor.addresses.all()
		for address in addresses:
			if address.pin_code == pincode:
				return address
		return None
	except:
		return None

def is_consumer_has_same_address_already(consumer, pincode):
	try:
		addresses = consumer.addresses.all()
		for address in addresses:
			if address.pin_code == pincode:
				return address
		return None
	except:
		return None


@api_view(['POST'])
def old_order_id_for_new_order_id(request):
	if request.user.is_staff is False:
		content = {
		'error':'insufficient permissions', 
		'description':'Only admin can access this method'
		}
		return Response(content, status = status.HTTP_400_BAD_REQUEST)
	else:
		delivery_status_id = request.data['new_order_id']
		delivery_status = get_object_or_404(OrderDeliveryStatus, pk = delivery_status_id)
		old_id = delivery_status.order.id
		content = {
		'old_id':old_id
		}
		return Response(content, status = status.HTTP_200_OK)

@api_view(['POST'])
def new_order_id_for_old_order_id(request):
	if request.user.is_staff is False:
		content = {
		'error':'insufficient permissions', 
		'description':'Only admin can access this method'
		}
		return Response(content, status = status.HTTP_400_BAD_REQUEST)
	else:
		old_order_id = request.data['old_order_id']
		order = get_object_or_404(Order, pk = old_order_id)
		delivery_status = get_object_or_404(OrderDeliveryStatus, order = order)
		new_id = delivery_status.id
		content = {
		'new_id':new_id
		}
		return Response(content, status = status.HTTP_200_OK)

@api_view(['GET'])
def fill_full_address(request):
	all_addresses = Address.objects.filter(Q(full_address = '-') | Q(full_address = '')| Q(full_address = None))
	
	if request.user.is_staff is False:
		content = {
		'error':'insufficient permissions', 
		'description':'Only admin can access this method'
		}
		return Response(content, status = status.HTTP_400_BAD_REQUEST)

	for address in all_addresses:
		total_address = ''
		if address.flat_number is not None:
			total_address = total_address + address.flat_number 

		if address.building is not None:
			total_address = total_address + ', ' + address.building

		if address.street is not None:
			total_address = total_address + ', ' + address.street

		address.full_address = total_address
		address.save()

	content = {'data':'Done saving addresses'}
	return Response(content, status = status.HTTP_200_OK)
