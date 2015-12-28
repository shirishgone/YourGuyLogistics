from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api_v3 import constants
from api_v3.utils import user_role
from yourguy.models import Address, VendorAgent


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
        content = {
            'error': 'Incomplete parameters', 'description': 'full_address, pin_code, landmark'
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    role = user_role(request.user)
    if role == constants.VENDOR:
        vendor_agent = get_object_or_404(VendorAgent, user=request.user)
        vendor = vendor_agent.vendor

        new_address = create_address(full_address, pin_code, landmark)
        vendor.addresses.add(new_address)
        content = {
            'description': 'Address added successfully'
        }
        return Response(content, status=status.HTTP_200_OK)
    else:
        content = {
            'description': 'You don\'t have permissions to add address.'
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def remove_address(request):
    try:
        address_id = request.data['address_id']
    except APIException:
        content = {
            'error': 'Incomplete params', 'description': 'address_id'
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    role = user_role(request.user)
    if role == constants.VENDOR:
        address = get_object_or_404(Address, pk=address_id)

        vendor_agent = get_object_or_404(VendorAgent, user=request.user)
        vendor = vendor_agent.vendor
        vendor.addresses.remove(address)

        content = {
            'description': 'Address removed successfully'
        }
        return Response(content, status=status.HTTP_200_OK)
    else:
        content = {
            'description': 'You don\'t have permissions to remove address.'
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
