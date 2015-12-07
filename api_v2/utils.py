from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from datetime import datetime, timedelta, time
from yourguy.models import Order, Address, Consumer, OrderDeliveryStatus
import json
from django.db.models import Q

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

@api_view(['GET'])
def is_recurring_var_setting(request):
	if request.user.is_staff is False:
		content = {
		'error':'insufficient permissions', 
		'description':'Only admin can access this method'
		}
		return Response(content, status = status.HTTP_400_BAD_REQUEST)
	else:
		all_orders = Order.objects.all()
		for order in all_orders:
			if len(order.delivery_status.all()) > 1:
				order.is_recurring = True
				order.save()
	
		content = {'data':'All done'}
		return Response(content, status = status.HTTP_200_OK)


@api_view(['GET'])
def delivery_status_update(request):
	if request.user.is_staff is False:
		content = {
		'error':'insufficient permissions', 
		'description':'Only admin can access this method'
		}
		return Response(content, status = status.HTTP_400_BAD_REQUEST)
	else:
		
		all_delivery_statuses = OrderDeliveryStatus.objects.filter(order_status = 'ATTEMPTED')
		not_updated_deliverys = []		
		for delivery_status in all_delivery_statuses:
			try:
				if delivery_status.order_status == 'ATTEMPTED':
					delivery_status.order_status = 'DELIVERYATTEMPTED'
					delivery_status.save()
			except Exception, e:
				not_updated_deliverys.append(delivery_status.id)
				pass		
		content = {
		'data':'All done',
		'not_updated_deliverys':json.dumps(not_updated_deliverys)
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
