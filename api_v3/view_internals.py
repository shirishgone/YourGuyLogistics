from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from yourguy.models import Address, Notification, Consumer
from django.db.models import Q, Count

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

@api_view(['GET'])
def mark_all_notifications_read(request):
    if request.user.is_staff is False:
        content = {
            'error': 'insufficient permissions',
            'description': 'Only admin can access this method'
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    else:        
        all_notifications = Notification.objects.filter(read = False)
        for notification in all_notifications:
            notification.read = True
            notification.save()
        return Response(status=status.HTTP_200_OK)

@api_view(['GET'])
def consumers_refill(request):
    if request.user.is_staff is False:
        content = {
            'error': 'insufficient permissions',
            'description': 'Only admin can access this method'
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    else:
        all_consumers = Consumer.objects.filter(Q(phone_number=None) | Q(full_name=None) | Q(user__date_joined=None))
        for consumer in all_consumers:
            consumer.created_date = consumer.user.date_joined
            consumer.phone_number = consumer.user.username
            consumer.full_name = consumer.user.first_name
            consumer.save()
        return Response(status=status.HTTP_200_OK)

@api_view(['GET'])
def consumers_with_zero_single_vendor_association(request):
    if request.user.is_staff is False:
        content = {
            'error': 'insufficient permissions',
            'description': 'Only admin can access this method'
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    else:
        consumers = Consumer.objects.filter(vendor__isnull=True)
        count = consumers.count()
        content = {
            'count': count
        }        
        return Response(content, status=status.HTTP_200_OK)

@api_view(['GET'])
def consumers_with_more_than_one_vendor(request):
    if request.user.is_staff is False:
        content = {
            'error': 'insufficient permissions',
            'description': 'Only admin can access this method'
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    else:
        consumers = Consumer.objects.annotate(vendor_count=Count('associated_vendor')).filter(vendor_count__gt=1)
        count = consumers.count()
        content = {
            'count': count
        }        
        return Response(content, status=status.HTTP_200_OK)

@api_view(['GET'])
def refill_consumers_with_one_vendor(request):
    if request.user.is_staff is False:
        content = {
            'error': 'insufficient permissions',
            'description': 'Only admin can access this method'
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    else:
        consumers = Consumer.objects.filter(vendor__isnull=True)
        for consumer in consumers:
            vendors = consumer.associated_vendor.all()
            count = len(vendors)
            if count == 1:
                single_vendor = vendors[0]
                consumer.vendor = single_vendor
                consumer.save()
        return Response(status=status.HTTP_200_OK)
