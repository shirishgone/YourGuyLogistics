from datetime import datetime

import dateutil.relativedelta
from django.db.models import Q, Count
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api_v3 import constants
from api_v3.utils import ist_day_start, ist_day_end, send_email
from yourguy.models import OrderDeliveryStatus


@api_view(['GET'])
def assign_dg(request):
    # FETCH ALL TODAY ORDERS --------------------------------------------

    date = datetime.today()
    day_start = ist_day_start(date)
    day_end = ist_day_end(date)

    # FILTER TO BE ASSIGNED ORDERS -------------------------------------------------------------------------
    delivery_status_queryset = OrderDeliveryStatus.objects.filter(date__gte=day_start, date__lte=day_end)
    delivery_status_queryset = delivery_status_queryset.filter(Q(delivery_guy=None) | Q(pickup_guy=None))
    delivery_status_queryset = delivery_status_queryset.filter(
        Q(order_status=constants.ORDER_STATUS_PLACED) |
        Q(order_status=constants.ORDER_STATUS_QUEUED) |
        Q(order_status=constants.ORDER_STATUS_INTRANSIT))
    # --------------------------------------------------------------------------------------------------------

    # --------------------------------------------------------------------
    for delivery_status in delivery_status_queryset.all():
        try:
            order = delivery_status.order

            # CUSTOMER AND VENDOR FILTERING -----------------------------------------------------------------
            vendor = order.vendor
            consumer = order.consumer

            previous_delivery_statuses = OrderDeliveryStatus.objects.filter(
                delivery_guy__isnull=False, order__consumer=consumer, order__vendor=vendor)
            # ------------------------------------------------------------------------------------------------

            # FILTER LAST 1 MONTHS ORDERS --------------------------------------------------------------------
            two_months_previous_date = day_start - dateutil.relativedelta.relativedelta(months=1)
            previous_delivery_statuses = previous_delivery_statuses.filter(
                date__gte=two_months_previous_date, date__lte=day_start)
            # ------------------------------------------------------------------------------------------------

            # FILTERING BY PICKUP TIME RANGE -----------------------------------------------------------------
            pickup_hour = int(order.pickup_datetime.hour)
            previous_delivery_statuses = previous_delivery_statuses.filter(
                Q(order__pickup_datetime__hour=pickup_hour - 1) |
                Q(order__pickup_datetime__hour=pickup_hour) |
                Q(order__pickup_datetime__hour=pickup_hour + 1))
            # ------------------------------------------------------------------------------------------------

            # PICK LATEST PICKUP ASSIGNED PREVIOUSLY AND ASSIGN FOR TODAY ---------------------------------------
            try:
                if delivery_status.pickup_guy is None:
                    latest_assigned_pickup = previous_delivery_statuses.exclude(pickup_guy=None).latest('date')
                    if latest_assigned_pickup is not None:
                        delivery_status.pickup_guy = latest_assigned_pickup.pickup_guy
                        delivery_status.save()
            except Exception as e:
                pass
            # ------------------------------------------------------------------------------------------------
            
            # PICK LATEST DELIVERY ASSIGNED AND ASSIGN FOR TODAY ------------------------------------------------
            try:
                if delivery_status.delivery_guy is None:
                    latest_assigned_delivery = previous_delivery_statuses.exclude(delivery_guy=None).latest('date')
                    if latest_assigned_delivery is not None:
                        delivery_status.delivery_guy = latest_assigned_delivery.delivery_guy
                        delivery_status.save()
            except Exception as e:
                pass
                # ------------------------------------------------------------------------------------------------
        except Exception as e:
            pass
    
    delivery_status_queryset = OrderDeliveryStatus.objects.filter(date__gte=day_start, date__lte=day_end)
    unassigned_pickups_queryset = delivery_status_queryset.filter(Q(pickup_guy=None)).values('order__vendor__store_name').annotate(the_count=Count('order__vendor__store_name'))
    unassigned_pickups_string = ''
    for unassigned_pickups in unassigned_pickups_queryset:
        unassigned_pickups_string = unassigned_pickups_string + '%s - %s\n'%(unassigned_pickups['order__vendor__store_name'],unassigned_pickups['the_count'])

    unassigned_deliveries_queryset = delivery_status_queryset.filter(Q(delivery_guy=None)).values('order__vendor__store_name').annotate(the_count=Count('order__vendor__store_name'))
    unassigned_deliveries_string = ''    
    for unassigned_deliveries in unassigned_deliveries_queryset:
        unassigned_deliveries_string = unassigned_deliveries_string + '%s - %s\n'%(unassigned_deliveries['order__vendor__store_name'],unassigned_deliveries['the_count'])

    # SEND AN EMAIL SAYING CANT FIND APPROPRAITE DELIVERY GUY FOR THIS ORDER. PLEASE ASSIGN MANUALLY
    today_string = datetime.now().strftime("%Y %b %d")
    email_subject = 'Unassigned orders for %s' % (today_string)

    email_body = "Hello, \nPlease find the unassigned orders for the day. " \
                 "\nUnassigned pickups: \n%s \n\nUnassigned deliveries: \n%s \n\nPlease assign manually. \n\n- Team YourGuy" \s
                 % (unassigned_pickups_string, unassigned_deliveries_string)
    send_email(constants.EMAIL_UNASSIGNED_ORDERS, email_subject, email_body)

    # ------------------------------------------------------------------------------------------------

    # TODO
    # inform_dgs_about_orders_assigned()
    return Response(status=status.HTTP_200_OK)
