from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api_v3 import constants
from api_v3.utils import user_role, ist_day_start, ist_day_end
from yourguy.models import OrderDeliveryStatus, Vendor, VendorAgent


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def excel_download(request):
    try:
        start_date_string = request.data['start_date']
        end_date_string = request.data['end_date']

        start_date = parse_datetime(start_date_string)
        start_date = ist_day_start(start_date)

        end_date = parse_datetime(end_date_string)
        end_date = ist_day_end(end_date)

    except APIException as e:
        content = {
            'error': 'Error in params: start_date, end_date'
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    # VENDOR FILTERING -----------------------------------------------------------
    vendor = None
    role = user_role(request.user)
    if role == constants.VENDOR:
        vendor_agent = get_object_or_404(VendorAgent, user=request.user)
        vendor = vendor_agent.vendor
    else:
        vendor_id = request.data.get('vendor_id')
        if vendor_id is not None:
            vendor = get_object_or_404(Vendor, pk=vendor_id)
        else:
            pass

    if vendor is not None:
        delivery_status_queryset = OrderDeliveryStatus.objects.filter(order__vendor=vendor).select_related(
            'delivery_guy__user')
    else:
        delivery_status_queryset = OrderDeliveryStatus.objects.all().select_related('delivery_guy__user')

    # DATE FILTERING ---------------------------------------------------------------
    delivery_status_queryset = delivery_status_queryset.filter(date__gte=start_date, date__lte=end_date).select_related(
        'order')
    # ------------------------------------------------------------------------------

    if len(delivery_status_queryset) > 5000:
        content = {
            'error': 'Too many records. Please check lesser dates'
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    # CONSTRUCTING RESPONSE ---------------------------------------------------------------
    ist_timedelta = timedelta(hours=5, minutes=30)
    excel_order_details = []
    for delivery_status in delivery_status_queryset:
        try:
            date = delivery_status.date + ist_timedelta
            order = delivery_status.order
            excel_order = {
                'date': date.strftime('%d-%m-%Y'),
                'order_id': order.id,
                'customer_name': order.consumer.user.first_name,
                'customer_phone_number': order.consumer.user.username,
                'cod_amount': order.cod_amount,
                'cod_collected': delivery_status.cod_collected_amount,
                'cod_reason': delivery_status.cod_remarks,
                'status': delivery_status.order_status,
                'vendor_notes': order.notes,
                'vendor_order_id': order.vendor_order_id
            }
            if role == constants.OPERATIONS:
                excel_order['vendor_name'] = order.vendor.store_name
                if delivery_status.delivery_guy is not None:
                    excel_order['delivery_guy'] = delivery_status.delivery_guy.user.first_name
                else:
                    excel_order['delivery_guy'] = None

            excel_order_details.append(excel_order)
        except Exception as e:
            pass

    content = {
        'orders': excel_order_details
    }
    return Response(content, status=status.HTTP_200_OK)
