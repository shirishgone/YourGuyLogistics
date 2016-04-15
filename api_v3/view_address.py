from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated

from api_v3 import constants
from api_v3.utils import user_role
from yourguy.models import Address, VendorAgent, ServiceablePincode
from api_v3.utils import response_access_denied, response_with_payload, response_error_with_message, response_success_with_message, response_invalid_pagenumber, response_incomplete_parameters

def create_address(full_address, pin_code, landmark):
    new_address = Address.objects.create(full_address=full_address, pin_code=pin_code)
    if landmark is not None:
        new_address.landmark = landmark
        new_address.save()
    return new_address

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def add_address(request):
    try:
        full_address = request.data['full_address']
        pin_code = request.data['pin_code']
        landmark = request.data.get('landmark')
    except APIException:
        parameters = ['full_address', 'pin_code', 'landmark']
        return response_incomplete_parameters(parameters)

    role = user_role(request.user)
    if role == constants.VENDOR:
        vendor_agent = get_object_or_404(VendorAgent, user=request.user)
        vendor = vendor_agent.vendor

        new_address = create_address(full_address, pin_code, landmark)
        vendor.addresses.add(new_address)
        success_message = 'Address added successfully'
        return response_success_with_message(success_message)
    else:
        return response_access_denied()


@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def remove_address(request):
    try:
        address_id = request.data['address_id']
    except APIException:
        parameters = ['description', 'address_id']
        return response_incomplete_parameters(parameters)

    role = user_role(request.user)
    if role == constants.VENDOR:
        address = get_object_or_404(Address, pk=address_id)

        vendor_agent = get_object_or_404(VendorAgent, user=request.user)
        vendor = vendor_agent.vendor
        vendor.addresses.remove(address)
        success_message = 'Address removed successfully'
        return response_success_with_message(success_message)
    else:
        return response_access_denied()

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def servicible_pincodes(request):
    role = user_role(request.user)
    if role == constants.VENDOR or \
                    role == constants.OPERATIONS or \
                    role == constants.OPERATIONS_MANAGER or \
                    role == constants.HR or \
                    role == constants.SALES or \
                    role == constants.SALES_MANAGER:
        all_pincodes = ServiceablePincode.objects.all()
        result = []
        for pincode in all_pincodes:
            pincode_dict = {
                'pincode':pincode.pincode,
                'city':pincode.city.city_name
            }
            result.append(pincode_dict)
        return response_with_payload(result, None)
    else:
        return response_access_denied()
