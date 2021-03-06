from datetime import datetime

import dateutil.relativedelta
from django.db.models import Q, Count
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api_v3 import constants
from api_v3.utils import ist_day_start, ist_day_end, send_email, ops_managers_for_pincode, ops_executive_for_pincode, ops_manager_for_dg, ops_executive_for_dg
from yourguy.models import OrderDeliveryStatus, Notification, DeliveryGuy, Vendor

from datetime import time, datetime, timedelta
from api_v3.utils import notification_type_for_code
from django.shortcuts import get_object_or_404

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
    delivery_status_queryset = delivery_status_queryset.filter(
        Q(order_status=constants.ORDER_STATUS_PLACED) |
        Q(order_status=constants.ORDER_STATUS_QUEUED) |
        Q(order_status=constants.ORDER_STATUS_INTRANSIT))

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

def delivery_ids_string(pincode_wise_delivery_ids):
    if len(pincode_wise_delivery_ids) > 100:
        sub_array = pincode_wise_delivery_ids[0:100]
        delivery_ids_string = ','.join(str(delivery_id) for delivery_id in sub_array)
    else:
        delivery_ids_string = ','.join(str(delivery_id) for delivery_id in pincode_wise_delivery_ids)
    return delivery_ids_string

def delivery_ids_message_string(pincode_wise_delivery_ids):
    if len(pincode_wise_delivery_ids) > 5:
        sub_array = pincode_wise_delivery_ids[0:5]
        delivery_ids_string = ','.join(str(delivery_id) for delivery_id in sub_array)
        delivery_ids_string = delivery_ids_string+'& more ...'
    else:
        delivery_ids_string = ','.join(str(delivery_id) for delivery_id in pincode_wise_delivery_ids)
    return delivery_ids_string

def check_if_notification_already_exists(notification_type, ops_executive, delivery_ids):
    all_notifications = ops_executive.notifications.all()
    for notification in all_notifications:
        if notification.notification_type == notification_type and notification.delivery_id == delivery_ids and notification.read == False:
            return True
    return False

def create_notif_for_no_ops_exec_for_delivery_guy(delivery_guy):
    ops_managers = ops_manager_for_dg(delivery_guy)
    if len(ops_managers) > 0:
        notification_type = notification_type_for_code(constants.NOTIFICATION_CODE_NO_OPS_EXECUTIVE_FOR_DELIVERY_BOY)
        for ops_manager in ops_managers:
            if check_if_notification_already_exists(notification_type, ops_manager, None) is False:
                notification_message = constants.NOTIFICATION_MESSAGE_NO_OPS_EXEC_FOR_DELIVERY_GUY%(ops_manager.user.first_name, delivery_guy.user.first_name)
                new_notification = Notification.objects.create(notification_type = notification_type, message = notification_message)
                ops_manager.notifications.add(new_notification)
                ops_manager.save()

def create_notif_for_no_ops_exec_for_pincode(pincode):
    ops_managers = ops_managers_for_pincode(pincode)
    if len(ops_managers) > 0:
        notification_type = notification_type_for_code(constants.NOTIFICATION_CODE_NO_OPS_EXECUTIVE_FOR_PINCODE)
        for ops_manager in ops_managers:
            if check_if_notification_already_exists(notification_type, ops_manager, None) is False:
                notification_message = constants.NOTIFICATION_MESSAGE_NO_OPS_EXEC_FOR_PINCODE%(ops_manager.user.first_name, pincode)
                new_notification = Notification.objects.create(notification_type = notification_type, message = notification_message)
                ops_manager.notifications.add(new_notification)
                ops_manager.save()

def notify_unassigned_pickup():
    date = datetime.today()
    day_start = ist_day_start(date)
    day_end = ist_day_end(date)

    delivery_status_queryset = OrderDeliveryStatus.objects.filter(date__gte=day_start, date__lte=day_end)
    delivery_status_queryset = delivery_status_queryset.filter(Q(pickup_guy=None))
    delivery_status_queryset = delivery_status_queryset.filter(Q(order_status=constants.ORDER_STATUS_QUEUED))

    notif_datetime = datetime.now() + timedelta(hours=2, minutes=0)
    delivery_status_queryset = delivery_status_queryset.filter(order__pickup_datetime__lte=notif_datetime)
    
    vendors = delivery_status_queryset.values_list('order__vendor__id', flat = True).distinct()
    for vendor_id in vendors:
        vendor = get_object_or_404(Vendor, id = vendor_id)
        vendor_wise_delivery_queryset = delivery_status_queryset.filter(order__vendor= vendor)

        pincodes = vendor_wise_delivery_queryset.values_list('order__pickup_address__pin_code', flat = True).distinct()
        for pincode in pincodes:
            pincode_wise_delivery_ids = vendor_wise_delivery_queryset.filter(order__pickup_address__pin_code= pincode).values_list('id', flat = True)
            delivery_ids = delivery_ids_string(pincode_wise_delivery_ids)
            delivery_ids_msg_string = delivery_ids_message_string(pincode_wise_delivery_ids)
            ops_managers = ops_executive_for_pincode(pincode)
            if len(ops_managers) > 0:
                notification_type = notification_type_for_code(constants.NOTIFICATION_CODE_UNASSIGNED_PICKUP)
                for ops_manager in ops_managers:
                    if check_if_notification_already_exists(notification_type, ops_manager, delivery_ids) is False:
                        notification_message = constants.NOTIFICATION_MESSAGE_UNASSIGNED_PICKUP%(ops_manager.user.first_name, vendor.store_name, delivery_ids_msg_string, pincode)
                        new_notification = Notification.objects.create(notification_type = notification_type, 
                            delivery_id = delivery_ids, message = notification_message)
                        ops_manager.notifications.add(new_notification)
                        ops_manager.save()
            else:
                create_notif_for_no_ops_exec_for_pincode(pincode)

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
        delivery_ids = delivery_ids_string(pincode_wise_delivery_ids)
        delivery_ids_msg_string = delivery_ids_message_string(pincode_wise_delivery_ids)
        ops_managers = ops_executive_for_pincode(pincode)
        if len(ops_managers)  > 0:
            notification_type = notification_type_for_code(constants.NOTIFICATION_CODE_UNASSIGNED_DELIVERY)            
            for ops_manager in ops_managers:
                if check_if_notification_already_exists(notification_type, ops_manager, delivery_ids) is False:
                    notification_message = constants.NOTIFICATION_MESSAGE_UNASSIGNED_DELIVERY%(ops_manager.user.first_name, delivery_ids_msg_string, pincode)
                    new_notification = Notification.objects.create(notification_type = notification_type, 
                        delivery_id = delivery_ids, message = notification_message)
                    ops_manager.notifications.add(new_notification)
                    ops_manager.save()
        else:
            create_notif_for_no_ops_exec_for_pincode(pincode)

def notify_delivery_delay():
    date = datetime.today()
    day_start = ist_day_start(date)
    day_end = ist_day_end(date)

    delivery_status_queryset = OrderDeliveryStatus.objects.filter(date__gte=day_start, date__lte=day_end)
    delivery_status_queryset = delivery_status_queryset.filter(Q(order_status=constants.ORDER_STATUS_INTRANSIT))    
    
    current_datetime = datetime.now()
    delivery_status_queryset = delivery_status_queryset.filter(order__delivery_datetime__lte=current_datetime)

    delivery_guys = delivery_status_queryset.values_list('delivery_guy', flat = True).exclude(delivery_guy=None).distinct()
    for delivery_guy_id in delivery_guys:
        try:
            delivery_guy = get_object_or_404(DeliveryGuy, id = delivery_guy_id)
            delivery_guy_wise_delivery_ids = delivery_status_queryset.filter(delivery_guy= delivery_guy).values_list('id', flat = True)
            delivery_ids = delivery_ids_string(delivery_guy_wise_delivery_ids)
            delivery_ids_msg_string = delivery_ids_message_string(delivery_guy_wise_delivery_ids)
            ops_managers = ops_executive_for_dg(delivery_guy)
            if len(ops_managers)  > 0:
                notification_type = notification_type_for_code(constants.NOTIFICATION_CODE_LATE_DELIVERY)
                for ops_manager in ops_managers:
                    if check_if_notification_already_exists(notification_type, ops_manager, delivery_ids) is False:
                        notification_message = constants.NOTIFICATION_MESSAGE_DELIVERY_DELAY%(ops_manager.user.first_name, delivery_guy.user.first_name, delivery_ids_msg_string, delivery_guy.user.first_name, delivery_guy.user.username)
                        new_notification = Notification.objects.create(notification_type = notification_type, 
                            delivery_id = delivery_ids, message = notification_message)
                        ops_manager.notifications.add(new_notification)
                        ops_manager.save()
            else:
                create_notif_for_no_ops_exec_for_delivery_guy(delivery_guy)
        except Exception, e:
            pass

def notify_pickup_delay():
    date = datetime.today()
    day_start = ist_day_start(date)
    day_end = ist_day_end(date)

    delivery_status_queryset = OrderDeliveryStatus.objects.filter(date__gte=day_start, date__lte=day_end)
    delivery_status_queryset = delivery_status_queryset.filter(
        Q(order_status=constants.ORDER_STATUS_PLACED) |
        Q(order_status=constants.ORDER_STATUS_QUEUED) )
    
    current_datetime = datetime.now()
    delivery_status_queryset = delivery_status_queryset.filter(order__pickup_datetime__lte=current_datetime)

    pickup_guys = delivery_status_queryset.values_list('pickup_guy', flat = True).exclude(pickup_guy=None).distinct()
    for pickup_guy_id in pickup_guys:
        try:
            pickup_guy = get_object_or_404(DeliveryGuy, id = pickup_guy_id)
            pickupguy_wise_delivery_ids = delivery_status_queryset.filter(pickup_guy= pickup_guy).values_list('id', flat = True)
            delivery_ids = delivery_ids_string(pickupguy_wise_delivery_ids)
            delivery_ids_msg_string = delivery_ids_message_string(pickupguy_wise_delivery_ids)
            ops_managers = ops_executive_for_dg(pickup_guy)
            if len(ops_managers)  > 0:
                notification_type = notification_type_for_code(constants.NOTIFICATION_CODE_LATE_PICKUP)
                for ops_manager in ops_managers:
                    if check_if_notification_already_exists(notification_type, ops_manager, delivery_ids) is False:
                        notification_message = constants.NOTIFICATION_MESSAGE_PICKUP_DELAY%(ops_manager.user.first_name, pickup_guy.user.first_name, delivery_ids_msg_string, pickup_guy.user.first_name, pickup_guy.user.username)
                        new_notification = Notification.objects.create(notification_type = notification_type, 
                            delivery_id = delivery_ids, message = notification_message)
                        ops_manager.notifications.add(new_notification)
                        ops_manager.save()
            else:
                create_notif_for_no_ops_exec_for_delivery_guy(pickup_guy)
        except Exception, e:
            pass