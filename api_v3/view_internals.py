from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from yourguy.models import Address

@api_view(['GET'])
def fill_full_address(request):
    all_addresses = Address.objects.filter(Q(full_address='-') | Q(full_address='') | Q(full_address=None))
    if request.user.is_staff is False:
        content = {
            'error': 'insufficient permissions',
            'description': 'Only admin can access this method'
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

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

    content = {'data': 'Done saving addresses'}
    return Response(content, status=status.HTTP_200_OK)

@api_view(['PUT'])
def old_order_id_for_new_order_id(request):
    if request.user.is_staff is False:
        content = {
            'error': 'insufficient permissions',
            'description': 'Only admin can access this method'
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    else:
        delivery_status_id = request.data['new_order_id']
        delivery_status = get_object_or_404(OrderDeliveryStatus, pk=delivery_status_id)
        old_id = delivery_status.order.id
        content = {
            'old_id': old_id
        }
        return Response(content, status=status.HTTP_200_OK)


@api_view(['PUT'])
def new_order_id_for_old_order_id(request):
    if request.user.is_staff is False:
        content = {
            'error': 'insufficient permissions',
            'description': 'Only admin can access this method'
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    else:
        old_order_id = request.data['old_order_id']
        order = get_object_or_404(Order, pk=old_order_id)
        delivery_status = get_object_or_404(OrderDeliveryStatus, order=order)
        new_id = delivery_status.id
        content = {
            'new_id': new_id
        }
        return Response(content, status=status.HTTP_200_OK)
