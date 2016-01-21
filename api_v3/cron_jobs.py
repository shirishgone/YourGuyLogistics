from datetime import datetime

import dateutil.relativedelta
from django.db.models import Q, Count
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api_v3 import constants
from api_v3.utils import ist_day_start, ist_day_end, send_email, ops_managers_for_pincode
from yourguy.models import OrderDeliveryStatus, Notification

from datetime import time, datetime, timedelta
from api_v3.utils import notification_type_for_code


def assign_dg():
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
                 "\nUnassigned pickups: \n%s \n\nUnassigned deliveries: \n%s \n\nPlease assign manually. \n\n- Team YourGuy" \
                 % (unassigned_pickups_string, unassigned_deliveries_string)
    send_email(constants.EMAIL_UNASSIGNED_ORDERS, email_subject, email_body)

    # ------------------------------------------------------------------------------------------------

    # TODO
    # inform_dgs_about_orders_assigned()

def notify_unassigned_deliveries():
    date = datetime.today()
    day_start = ist_day_start(date)
    day_end = ist_day_end(date)

    delivery_status_queryset = OrderDeliveryStatus.objects.filter(date__gte=day_start, date__lte=day_end)
    delivery_status_queryset = delivery_status_queryset.filter(Q(delivery_guy=None))
    delivery_status_queryset = delivery_status_queryset.filter(
        Q(order_status=constants.ORDER_STATUS_PLACED) |
        Q(order_status=constants.ORDER_STATUS_QUEUED) |
        Q(order_status=constants.ORDER_STATUS_INTRANSIT))

    notif_datetime = datetime.now() + timedelta(hours=2, minutes=0)
    delivery_status_queryset = delivery_status_queryset.filter(order__delivery_datetime__lte=notif_datetime)

    pincodes = delivery_status_queryset.values_list('order__delivery_address__pin_code', flat = True).distinct()
    for pincode in pincodes:
        pincode_wise_delivery_ids = delivery_status_queryset.filter(order__delivery_address__pin_code= pincode).values_list('id', flat = True)
        delivery_ids = ','.join(str(delivery_id) for delivery_id in pincode_wise_delivery_ids)
        ops_managers = ops_managers_for_pincode(pincode)
        if ops_managers.count() > 0:
            notification_type = notification_type_for_code(constants.NOTIFICATION_CODE_UNASSIGNED)
            for ops_manager in ops_managers:
                notification_message = constants.NOTIFICATION_MESSAGE_UNASSIGNED%(ops_manager.user.first_name, delivery_ids)
                new_notification = Notification.objects.create(notification_type = notification_type, 
                    delivery_id = delivery_ids, message = notification_message)
                ops_manager.notifications.add(new_notification)
                ops_manager.save()
        else:
            # CANT FIND APPROPRIATE OPS_EXECUTIVE FOR THE ABOVE PINCODE
            pass 

def notify_delivery_delay():
    date = datetime.today()
    day_start = ist_day_start(date)
    day_end = ist_day_end(date)

    delivery_status_queryset = OrderDeliveryStatus.objects.filter(date__gte=day_start, date__lte=day_end)
    delivery_status_queryset = delivery_status_queryset.filter(
        Q(order_status=constants.ORDER_STATUS_PLACED) |
        Q(order_status=constants.ORDER_STATUS_QUEUED) |
        Q(order_status=constants.ORDER_STATUS_INTRANSIT))
    
    current_datetime = datetime.now()
    delivery_status_queryset = delivery_status_queryset.filter(order__delivery_datetime__lte=current_datetime)
    
    pincodes = delivery_status_queryset.values_list('order__delivery_address__pin_code', flat = True).distinct()
    for pincode in pincodes:
        pincode_wise_delivery_ids = delivery_status_queryset.filter(order__delivery_address__pin_code= pincode).values_list('id', flat = True)
        delivery_ids = ','.join(str(delivery_id) for delivery_id in pincode_wise_delivery_ids)
        ops_managers = ops_managers_for_pincode(pincode)
        if ops_managers.count() > 0:
            notification_type = notification_type_for_code(constants.NOTIFICATION_CODE_LATE_DELIVERY)
            for ops_manager in ops_managers:
                notification_message = constants.NOTIFICATION_MESSAGE_DELIVERY_DELAY%(ops_manager.user.first_name, delivery_ids)
                new_notification = Notification.objects.create(notification_type = notification_type, 
                    delivery_id = delivery_ids, message = notification_message)
                ops_manager.notifications.add(new_notification)
                ops_manager.save()
        else:
            # CANT FIND APPROPRIATE OPS_EXECUTIVE FOR THE ABOVE PINCODE
            pass 

def notify_pickup_delay():
    send_email(constants.EMAIL_UNASSIGNED_ORDERS, 'test pickup delay cron', 'test body')
    date = datetime.today()
    day_start = ist_day_start(date)
    day_end = ist_day_end(date)

    delivery_status_queryset = OrderDeliveryStatus.objects.filter(date__gte=day_start, date__lte=day_end)
    delivery_status_queryset = delivery_status_queryset.filter(
        Q(order_status=constants.ORDER_STATUS_PLACED) |
        Q(order_status=constants.ORDER_STATUS_QUEUED) )
    
    current_datetime = datetime.now()
    delivery_status_queryset = delivery_status_queryset.filter(order__pickup_datetime__lte=current_datetime)

    pincodes = delivery_status_queryset.values_list('order__pickup_address__pin_code', flat = True).distinct()
    for pincode in pincodes:
        pincode_wise_delivery_ids = delivery_status_queryset.filter(order__pickup_address__pin_code= pincode).values_list('id', flat = True)
        delivery_ids = ','.join(str(delivery_id) for delivery_id in pincode_wise_delivery_ids)
        ops_managers = ops_managers_for_pincode(pincode)
        if ops_managers.count() > 0:
            notification_type = notification_type_for_code(constants.NOTIFICATION_CODE_LATE_PICKUP)
            for ops_manager in ops_managers:
                notification_message = constants.NOTIFICATION_MESSAGE_PICKUP_DELAY%(ops_manager.user.first_name, delivery_ids)
                new_notification = Notification.objects.create(notification_type = notification_type, 
                    delivery_id = delivery_ids, message = notification_message)
                ops_manager.notifications.add(new_notification)
                ops_manager.save()
        else:
            # CANT FIND APPROPRIATE OPS_EXECUTIVE FOR THE ABOVE PINCODE
            pass 