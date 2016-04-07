from datetime import timedelta
from dateutil.rrule import rrule, DAILY
from django.db.models import Sum, Q
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated

from api_v3 import constants
from api_v3.utils import user_role, ist_day_start, ist_day_end, ist_datetime
from yourguy.models import OrderDeliveryStatus, Vendor, VendorAgent

from api_v3.utils import response_access_denied, response_with_payload, response_error_with_message, response_success_with_message, response_invalid_pagenumber, response_incomplete_parameters

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def excel_download(request):
    try:
        start_date_string = request.QUERY_PARAMS.get('start_date', None)
        end_date_string = request.QUERY_PARAMS.get('end_date', None)

        start_date = parse_datetime(start_date_string)
        start_date = ist_day_start(start_date)

        end_date = parse_datetime(end_date_string)
        end_date = ist_day_end(end_date)        
    except Exception as e:
        params = ['start_date', 'end_date']
        return response_incomplete_parameters(params)
        
    # VENDOR FILTERING -----------------------------------------------------------
    vendor = None
    role = user_role(request.user)
    if role == constants.VENDOR:
        vendor_agent = get_object_or_404(VendorAgent, user=request.user)
        vendor = vendor_agent.vendor
    else:
        vendor_id = request.QUERY_PARAMS.get('vendor_id', None)
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
        error_message = 'Too many records. Max of 5000 deliveries can be downloaded at a time.'
        return response_error_with_message(error_message)

    # CONSTRUCTING RESPONSE ---------------------------------------------------------------
    ist_timedelta = timedelta(hours=5, minutes=30)
    excel_order_details = []
    for delivery_status in delivery_status_queryset:
        try:
            date = delivery_status.date + ist_timedelta
            order = delivery_status.order
            excel_order = {
                'date': date.strftime('%d-%m-%Y'),
                'order_id': delivery_status.id,
                'customer_name': order.consumer.full_name,
                'customer_phone_number': order.consumer.phone_number,
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
    return response_with_payload(excel_order_details, None)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def dashboard_stats(request):
    try:
        start_date_string = request.QUERY_PARAMS.get('start_date', None)
        end_date_string = request.QUERY_PARAMS.get('end_date', None)
        
        start_date = parse_datetime(start_date_string)
        start_date = ist_datetime(start_date)

        end_date = parse_datetime(end_date_string)
        end_date = ist_datetime(end_date)        
    except Exception as e:
        params = ['start_date', 'end_date']
        return response_incomplete_parameters(params)

    # CREATE DATE RULE -----------------------------------------------------------
    rule_daily = rrule(DAILY, dtstart=start_date, until=end_date)
    alldates = list(rule_daily)

    # VENDOR FILTERING -----------------------------------------------------------
    vendor = None
    role = user_role(request.user)
    if role == constants.VENDOR:
        vendor_agent = get_object_or_404(VendorAgent, user=request.user)
        vendor = vendor_agent.vendor
    else:
        vendor_id = request.QUERY_PARAMS.get('vendor_id', None)        
        if vendor_id is not None:
            vendor = get_object_or_404(Vendor, pk=vendor_id)
        else:
            pass

    if vendor is not None:
        delivery_status_queryset = OrderDeliveryStatus.objects.filter(order__vendor=vendor)
    else:
        delivery_status_queryset = OrderDeliveryStatus.objects.all()

    # DATE FILTERING ---------------------------------------------------------------
    delivery_status_queryset = delivery_status_queryset.filter(date__gte=start_date, date__lte=end_date)
    total_orders = delivery_status_queryset.filter(
        Q(order_status=constants.ORDER_STATUS_QUEUED) | 
        Q(order_status=constants.ORDER_STATUS_INTRANSIT) |
        Q(order_status=constants.ORDER_STATUS_OUTFORDELIVERY) |
        Q(order_status=constants.ORDER_STATUS_DELIVERED) | 
        Q(order_status=constants.ORDER_STATUS_DELIVERY_ATTEMPTED)).count()

    # ORDER STATUS FILTERING -------------------------------------------------------
    total_orders_executed = delivery_status_queryset.filter(
        Q(order_status=constants.ORDER_STATUS_DELIVERED) | 
        Q(order_status=constants.ORDER_STATUS_DELIVERY_ATTEMPTED)).count()
    
    # TOTAL COD TO BE COLLECTED -----------------------------
    executable_deliveries = delivery_status_queryset.filter(
        Q(order_status=constants.ORDER_STATUS_QUEUED) | 
        Q(order_status=constants.ORDER_STATUS_INTRANSIT) |
        Q(order_status=constants.ORDER_STATUS_OUTFORDELIVERY) |
        Q(order_status=constants.ORDER_STATUS_DELIVERY_ATTEMPTED) |
        Q(order_status=constants.ORDER_STATUS_DELIVERED))
    total_cod_dict = executable_deliveries.aggregate(total_cod=Sum('order__cod_amount'))
    total_cod = total_cod_dict['total_cod']
    
    # TOTAL COD COLLECTED ------------------------------------
    executed_deliveries = delivery_status_queryset.filter(Q(order_status=constants.ORDER_STATUS_DELIVERY_ATTEMPTED) |
                                                          Q(order_status=constants.ORDER_STATUS_DELIVERED))
    total_cod_dict = executed_deliveries.aggregate(total_cod=Sum('order__cod_amount'))
    cod_collected = total_cod_dict['total_cod']

    # FOR ORDER COUNT FOR INDIVIDUAL DATES -----------------------------------------
    fullday_timedelta = timedelta(hours=23, minutes=59)
    orders_graph = []
    for date in alldates:
        day_start = date
        day_end = day_start + fullday_timedelta
        delivery_status_per_date = delivery_status_queryset.filter(date__gte=day_start, date__lte=day_end)

        total_orders_per_day = delivery_status_per_date.count()
        orders_delivered_count = delivery_status_per_date.filter(Q(order_status=constants.ORDER_STATUS_DELIVERED)).count()
        orders_delivered_attempted_count = delivery_status_per_date.filter(Q(order_status=constants.ORDER_STATUS_DELIVERY_ATTEMPTED)).count()
        orders_pickup_attempted_count = delivery_status_per_date.filter(Q(order_status=constants.ORDER_STATUS_PICKUP_ATTEMPTED)).count()
        orders_cancelled_count = delivery_status_per_date.filter(Q(order_status=constants.ORDER_STATUS_CANCELLED)).count()
        orders_undelivered_count = delivery_status_per_date.filter(Q(order_status=constants.ORDER_STATUS_PLACED) |
                                                                   Q(order_status=constants.ORDER_STATUS_QUEUED)).count()
        orders_intransit_count = delivery_status_per_date.filter(Q(order_status=constants.ORDER_STATUS_OUTFORDELIVERY) |
                                                                 Q(order_status=constants.ORDER_STATUS_INTRANSIT)).count()

        ist_timedelta = timedelta(hours=5, minutes=30)
        display_date = date + ist_timedelta

        result = {
            'total_orders_count': total_orders_per_day,
            'delivered_count': orders_delivered_count,
            'delivery_attempted_count': orders_delivered_attempted_count,
            'pickup_attempted_count': orders_pickup_attempted_count,
            'cancelled_count': orders_cancelled_count,
            'queued_count': orders_undelivered_count,
            'intransit_count': orders_intransit_count,
            'date': display_date.date()
        }
        orders_graph.append(result)

    content = {
        'total_orders': total_orders,
        'total_orders_executed': total_orders_executed,
        'total_cod': total_cod,
        'cod_collected': cod_collected,
        'orders': orders_graph
    }
    return response_with_payload(content, None)