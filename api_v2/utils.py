from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from datetime import datetime, timedelta, time
from yourguy.models import Address, Consumer

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
