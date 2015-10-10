from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from datetime import datetime, timedelta, time
from yourguy.models import Order, Address, Consumer, OrderDeliveryStatus

def is_correct_pincode(pincode):
	if pincode.isdigit() and len(pincode) == 6:
		return True
	else: 	
		return False

def is_pickup_time_acceptable(datetime):
    if time(0, 0) <= datetime.time() <= time(16, 30):
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
		all_delivery_statuses = OrderDeliveryStatus.objects.filter(delivery_at = 'NOT_DELIVERED')
		# all_delivery_statuses = OrderDeliveryStatus.objects.all()
		for delivery_status in all_delivery_statuses:

			try:
				delivery_status.delivered_at = 'NONE'
				delivery_status.save()

				# if delivery_status.delivered_at == 'ATTEMPTED':
				# 	delivery_status.delivered_at = 'DELIVERYATTEMPTED'
				# 	delivery_status.save()
				# elif delivery_status.delivered_at == 'DOOR_STEP' or delivery_status.delivered_at == 'SECURITY' or delivery_status.delivered_at == 'RECEPTION' or delivery_status.delivered_at == 'CUSTOMER':
				# 	print 'done with delivery_status '+ delivery_status.id
				# else:		
				# 	delivery_status.delivered_at = 'NONE'
				# 	delivery_status.save()
			except Exception, e:
				content = {
				'error':e,
				'delivery_status_id':delivery_status.id
				}
				return Response(content, status = status.HTTP_200_OK)
		
		content = {
		'data':'All done'
		}
		return Response(content, status = status.HTTP_200_OK)


@api_view(['GET'])
def fill_full_address(request):
	all_addresses = Address.objects.all()

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
