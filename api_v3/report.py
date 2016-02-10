from datetime import datetime

from django.db.models import Sum, Q, F, Count
from rest_framework import status
from rest_framework.response import Response
from api_v3 import constants
from api_v3.utils import send_email, ist_day_start, ist_day_end
from yourguy.models import DeliveryGuy, OrderDeliveryStatus, DGAttendance, Vendor, Employee
from rest_framework.decorators import api_view


def daily_report():
    date = datetime.today()
    day_start = ist_day_start(date)
    day_end = ist_day_end(date)

    # TOTAL ORDERS ----------------------------------------------------------------------
    delivery_statuses_today = OrderDeliveryStatus.objects.filter(date__gte=day_start, date__lte=day_end)
    orders_total_count = len(delivery_statuses_today)
    # -----------------------------------------------------------------------------------

    if orders_total_count == 0:
        today_string = datetime.now().strftime("%Y %b %d")
        email_subject = 'Daily Report : %s' % (today_string)

        email_body = "Good Evening Guys,"
        email_body = email_body + "\n\n No orders on the app."
        email_body = email_body + "\n\n Chill out!"
        email_body = email_body + "\n\n- YourGuy BOT"

        send_email(constants.EMAIL_IDS_EVERYBODY, email_subject, email_body)
    else:
        # TOTAL ORDERS ASSIGNED vs UNASSIGNED ORDERS ----------------------------------------
        orders_unassigned_count = delivery_statuses_today.filter(delivery_guy=None).count()
        orders_assigned_count = orders_total_count - orders_unassigned_count

        orders_unassigned_percentage = "{0:.0f}%".format(
            float(orders_unassigned_count) / float(orders_total_count) * 100)
        orders_assigned_percentage = "{0:.0f}%".format(float(orders_assigned_count) / float(orders_total_count) * 100)
        # -----------------------------------------------------------------------------------

        # ORDERS ACC TO ORDER_STATUS --------------------------------------------------------
        orders_placed_count = delivery_statuses_today.filter(order_status=constants.ORDER_STATUS_PLACED).count()

        orders_queued_count = delivery_statuses_today.filter(order_status=constants.ORDER_STATUS_QUEUED).count()
        orders_queued_percentage = "{0:.0f}%".format(float(orders_queued_count) / float(orders_total_count) * 100)

        orders_intransit_count = delivery_statuses_today.filter(order_status=constants.ORDER_STATUS_INTRANSIT).count()
        orders_intransit_percentage = "{0:.0f}%".format(float(orders_intransit_count) / float(orders_total_count) * 100)

        orders_delivered_count = delivery_statuses_today.filter(order_status=constants.ORDER_STATUS_DELIVERED).count()
        orders_delivered_percentage = "{0:.0f}%".format(float(orders_delivered_count) / float(orders_total_count) * 100)

        orders_pickup_attempted_count = delivery_statuses_today.filter(
            order_status=constants.ORDER_STATUS_PICKUP_ATTEMPTED).count()
        orders_pickup_attempted_percentage = "{0:.0f}%".format(
            float(orders_pickup_attempted_count) / float(orders_total_count) * 100)

        orders_delivery_attempted_count = delivery_statuses_today.filter(
            order_status=constants.ORDER_STATUS_DELIVERY_ATTEMPTED).count()
        orders_delivery_attempted_percentage = "{0:.0f}%".format(
            float(orders_delivery_attempted_count) / float(orders_total_count) * 100)

        orders_rejected_count = delivery_statuses_today.filter(order_status=constants.ORDER_STATUS_REJECTED).count()
        orders_rejected_percentage = "{0:.0f}%".format(float(orders_rejected_count) / float(orders_total_count) * 100)

        orders_canceled_count = delivery_statuses_today.filter(order_status=constants.ORDER_STATUS_CANCELLED).count()
        orders_canceled_percentage = "{0:.0f}%".format(float(orders_canceled_count) / float(orders_total_count) * 100)

        pending_orders_count = orders_queued_count + orders_placed_count + orders_intransit_count
        pending_orders_percentage = "{0:.0f}%".format(float(pending_orders_count) / float(orders_total_count) * 100)

        completed_orders_count = orders_delivered_count + orders_pickup_attempted_count + \
                                 orders_delivery_attempted_count + orders_rejected_count + orders_canceled_count
        completed_orders_percentage = "{0:.0f}%".format(float(completed_orders_count) / float(orders_total_count) * 100)
        # -----------------------------------------------------------------------------------

        # DG ATTENDANCE DETAILS -------------------------------------------------------------
        total_dg_count = DeliveryGuy.objects.all().count()
        total_dg_checked_in_count = DGAttendance.objects.filter(date__year=date.year, date__month=date.month,
                                                                date__day=date.day).count()
        dg_checkin_percentage = "{0:.0f}%".format(float(total_dg_checked_in_count) / float(total_dg_count) * 100)
        # -----------------------------------------------------------------------------------

        # TOTAL COD COLLECTED Vs SUPPOSSED TO BE COLLECTED ----------------------------------
        total_cod_collected = delivery_statuses_today.aggregate(Sum('cod_collected_amount'))
        total_cod_collected = total_cod_collected['cod_collected_amount__sum']
        if total_cod_collected is None:
            total_cod_collected = 0

        executable_deliveries = delivery_statuses_today.filter(
            Q(order_status=constants.ORDER_STATUS_QUEUED) |
            Q(order_status=constants.ORDER_STATUS_INTRANSIT) |
            Q(order_status=constants.ORDER_STATUS_DELIVERED) |
            Q(order_status=constants.ORDER_STATUS_DELIVERY_ATTEMPTED) |
            Q(order_status=constants.ORDER_STATUS_PICKUP_ATTEMPTED))
        total_cod_dict = executable_deliveries.aggregate(total_cod=Sum('order__cod_amount'))
        total_cod_to_be_collected = total_cod_dict['total_cod']
        if total_cod_to_be_collected is None:
            total_cod_to_be_collected = 0

        if total_cod_to_be_collected > 0:
            cod_collected_percentage = "{0:.0f}%".format(
                float(total_cod_collected) / float(total_cod_to_be_collected) * 100)
        else:
            cod_collected_percentage = "100%"
        # -----------------------------------------------------------------------------------

        # DELIVERY BOY WHO HAVE COD --------------------------------------------------------
        cod_deliveries = delivery_statuses_today.filter(cod_collected_amount__gt=0)
        cod_with_delivery_boys = cod_deliveries.values('delivery_guy__user__first_name').annotate(
            total=Sum('cod_collected_amount'))

        cod_with_dg_string = ''
        for item in cod_with_delivery_boys:
            delivery_guy = item['delivery_guy__user__first_name']
            total = item['total']
            if total is None:
                total = 0
            cod_with_dg_string = cod_with_dg_string + "\n%s = %s" % (delivery_guy, total)
        # -----------------------------------------------------------------------------------
        today_string = datetime.now().strftime("%Y %b %d")
        email_subject = 'Daily Report : %s' % (today_string)

        email_body = "Good Evening Guys, \n\nPlease find the report of the day."
        email_body = email_body + "\n\nTotal orders = %s" % (orders_total_count)

        email_body = email_body + "\nPending orders     = %s [%s percent]" % (
            pending_orders_count, pending_orders_percentage)
        email_body = email_body + "\nExecuted orders    = %s [%s percent]" % (
            completed_orders_count, completed_orders_percentage)

        email_body = email_body + "\n\nSTATUS WISE BIFURGATION ------------"
        email_body = email_body + "\nOrders assigned    = %s [%s percent]" % (
            orders_assigned_count, orders_assigned_percentage)
        email_body = email_body + "\nOrders unassigned  = %s [%s percent]" % (
            orders_unassigned_count, orders_unassigned_percentage)
        email_body = email_body + "\nQueued         = %s [%s percent]" % (orders_queued_count, orders_queued_percentage)
        email_body = email_body + "\nInTransit      = %s [%s percent]" % (
            orders_intransit_count, orders_intransit_percentage)
        email_body = email_body + "\ndelivered      = %s [%s percent]" % (
            orders_delivered_count, orders_delivered_percentage)
        email_body = email_body + "\nPickup Attempted   = %s [%s percent]" % (
            orders_pickup_attempted_count, orders_pickup_attempted_percentage)
        email_body = email_body + "\nDelivery Attempted = %s [%s percent]" % (
            orders_delivery_attempted_count, orders_delivery_attempted_percentage)
        email_body = email_body + "\nRejected       = %s [%s percent]" % (
            orders_rejected_count, orders_rejected_percentage)
        email_body = email_body + "\nCanceled       = %s [%s percent]" % (
            orders_canceled_count, orders_canceled_percentage)
        email_body = email_body + "\n------------------------------------"

        email_body = email_body + "\n\nDELIVERY BOY ATTENDANCE -------"
        email_body = email_body + "\nTotal DGs on app   = %s" % total_dg_count
        email_body = email_body + "\nTotal DGs CheckIn  = %s [%s percent]" % (
            total_dg_checked_in_count, dg_checkin_percentage)
        email_body = email_body + "\n-----------------------------------"

        email_body = email_body + "\n\nCOD DETAILS ------------------"
        email_body = email_body + "\nTotal COD to be collected  = %s" % total_cod_to_be_collected
        email_body = email_body + "\nTotal COD collected        = %s [%s percent]" % (
            total_cod_collected, cod_collected_percentage)

        email_body = email_body + "\n-----------------------------------"

        email_body = email_body + "\n\nCOD WITH EACH DG ------------------"
        email_body = email_body + cod_with_dg_string
        email_body = email_body + "\n-----------------------------------"
        email_body = email_body + "\n\n- YourGuy BOT"

        send_email(constants.EMAIL_DAILY_REPORT, email_subject, email_body)
        # ------------------------------------------------------------------------------------------------

def cod_report():
    date = datetime.today()
    day_start = ist_day_start(date)
    day_end = ist_day_end(date)

    # TOTAL ORDERS ----------------------------------------------------------------------
    delivery_statuses_today = OrderDeliveryStatus.objects.filter(date__gte=day_start, date__lte=day_end,
                                                                 order__cod_amount__gt=0)
    orders_total_count = len(delivery_statuses_today)
    # -----------------------------------------------------------------------------------

    if orders_total_count == 0:
        today_string = datetime.now().strftime("%Y %b %d")
        email_subject = 'COD Report : %s' % (today_string)

        email_body = "Good Evening Guys,"
        email_body = email_body + "\n\n No COD today on the app."
        email_body = email_body + "\n\n- YourGuy BOT"

        send_email(constants.EMAIL_COD_REPORT, email_subject, email_body)
    else:
        # COD as per ORDER_STATUS --------------------------------------------------------
        orders_pending_queryset = delivery_statuses_today.filter(Q(order_status=constants.ORDER_STATUS_QUEUED) |
                                                                 Q(order_status=constants.ORDER_STATUS_INTRANSIT))
        orders_pending = orders_pending_queryset.aggregate(sum_of_cod_amount=Sum('order__cod_amount'))
        pending_cod_amount = orders_pending['sum_of_cod_amount']
        if pending_cod_amount is None:
            pending_cod_amount = 0

        orders_attempted_queryset = delivery_statuses_today.filter(
            Q(order_status=constants.ORDER_STATUS_PICKUP_ATTEMPTED) |
            Q(order_status=constants.ORDER_STATUS_DELIVERY_ATTEMPTED))
        orders_attempted = orders_attempted_queryset.aggregate(sum_of_cod_amount=Sum('order__cod_amount'))
        attempted_cod_amount = orders_attempted['sum_of_cod_amount']
        if attempted_cod_amount is None:
            attempted_cod_amount = 0

        orders_cancelled_queryset = delivery_statuses_today.filter(order_status=constants.ORDER_STATUS_CANCELLED)
        orders_cancelled = orders_cancelled_queryset.aggregate(sum_of_cod_amount=Sum('order__cod_amount'))
        cancelled_cod_amount = orders_cancelled['sum_of_cod_amount']
        if cancelled_cod_amount is None:
            cancelled_cod_amount = 0

        orders_executed_queryset = delivery_statuses_today.filter(Q(order_status=constants.ORDER_STATUS_DELIVERED) &
                                                                  Q(cod_collected_amount__lt=F('order__cod_amount')))
        orders_executed = orders_executed_queryset.aggregate(sum_of_cod_collected=Sum('cod_collected_amount'),
                                                             sum_of_cod_amount=Sum('order__cod_amount'))
        delivered_cod_collected = orders_executed['sum_of_cod_collected']
        if delivered_cod_collected is None:
            delivered_cod_collected = 0

        delivered_cod_amount = orders_executed['sum_of_cod_amount']
        if delivered_cod_amount is None:
            delivered_cod_amount = 0

        pending_cod = delivered_cod_amount - delivered_cod_collected
        pending_cod_amount = pending_cod_amount + pending_cod
        if pending_cod_amount is None:
            pending_cod_amount = 0

        orders_executed_queryset = delivery_statuses_today.filter(order_status=constants.ORDER_STATUS_DELIVERED)
        orders_executed = orders_executed_queryset.aggregate(sum_of_cod_collected=Sum('cod_collected_amount'),
                                                             sum_of_cod_amount=Sum('order__cod_amount'))
        delivered_cod_collected = orders_executed['sum_of_cod_collected']
        if delivered_cod_collected is None:
            delivered_cod_collected = 0

        delivered_cod_amount = orders_executed['sum_of_cod_amount']
        if delivered_cod_amount is None:
            delivered_cod_amount = 0

        pending_cod = delivered_cod_amount - delivered_cod_collected
        pending_cod_amount = pending_cod_amount + pending_cod

        delivery_statuses_tracked_queryset = delivery_statuses_today.filter(
            Q(order_status=constants.ORDER_STATUS_QUEUED) |
            Q(order_status=constants.ORDER_STATUS_INTRANSIT) |
            Q(order_status=constants.ORDER_STATUS_DELIVERED) |
            Q(order_status=constants.ORDER_STATUS_CANCELLED) |
            Q(order_status=constants.ORDER_STATUS_PICKUP_ATTEMPTED) |
            Q(order_status=constants.ORDER_STATUS_DELIVERY_ATTEMPTED)
        )

        collected = delivery_statuses_today.aggregate(Sum('cod_collected_amount'))
        total_cod_collected = collected['cod_collected_amount__sum']

        total_cod = delivery_statuses_tracked_queryset.aggregate(total_cod=Sum('order__cod_amount'))
        total_cod_amount = total_cod['total_cod']

        # -------------------------------------------------------------------------------

        today_string = datetime.now().strftime("%Y %b %d")
        email_subject = "COD Report : %s" % (today_string)

        email_body = "Good Evening Guys, \nPlease find the COD report of the day."
        email_body = email_body + "\n-----------------------\n"

        email_body = email_body + "\nDELIVERY STATUS wise COD"
        email_body = email_body + "\n-----------------------"
        email_body = email_body + "\nPENDING Orders amount: %0.0f" % (pending_cod_amount)

        email_body = email_body + "\nATTEMPTED Orders amount: %0.0f" % (attempted_cod_amount)

        email_body = email_body + "\nCANCELLED Orders amount: %0.0f" % (cancelled_cod_amount)

        email_body = email_body + "\nTOTAL COD amount: %0.0f" % (total_cod_amount)

        email_body = email_body + "\nCOLLECTED COD amount: %0.0f" % (total_cod_collected)
        email_body = email_body + "\n-----------------------\n"

        # COD as per VENDOR --------------------------------------------------------
        # all tracked orders
        delivery_statuses_tracked_queryset = delivery_statuses_today.filter(
            Q(order_status=constants.ORDER_STATUS_QUEUED) |
            Q(order_status=constants.ORDER_STATUS_INTRANSIT) |
            Q(order_status=constants.ORDER_STATUS_DELIVERED))
        delivery_statuses_tracked_queryset = delivery_statuses_tracked_queryset.filter(order__cod_amount__gt=0)
        vendors_tracked = delivery_statuses_tracked_queryset.values('order__vendor__store_name'). \
            annotate(sum_of_cod_collected=Sum('cod_collected_amount'), sum_of_cod_amount=Sum('order__cod_amount'))

        cod_with_vendor = ''
        for item in vendors_tracked:
            vendor = item['order__vendor__store_name']
            sum_of_cod_collected = item['sum_of_cod_collected']
            if sum_of_cod_collected is None:
                sum_of_cod_collected = 0

            sum_of_cod_amount = item['sum_of_cod_amount']
            if sum_of_cod_amount is None:
                sum_of_cod_amount = 0

            cod_with_vendor = cod_with_vendor + \
                              "\n%s - COD: %s/%s" % \
                              (vendor, sum_of_cod_collected, sum_of_cod_amount)
        # -----------------------------------------------------------------------------------
        email_body = email_body + "\n-----------------------\n"
        email_body = email_body + "\nVENDOR wise COD: \n* COD of pending and attempted orders are not considered."
        email_body = email_body + "\n\n" + cod_with_vendor

        # COD as per DG
        # dict of all DGs for tracked orders
        email_body = email_body + "\n-----------------------"
        email_body = email_body + "\nDG wise COD: \n* COD of pending and attempted orders are not considered."

        dg_tracked = delivery_statuses_tracked_queryset.values('delivery_guy__user__username'). \
            annotate(sum_of_cod_collected=Sum('cod_collected_amount'), sum_of_cod_amount=Sum('order__cod_amount'))
        cod_with_dg = ''
        # for each DG, display his total collection and amount supposed to be collected
        for single_dg in dg_tracked:
            dg_ph_number = single_dg['delivery_guy__user__username']
            sum_of_cod_collected = single_dg['sum_of_cod_collected']
            if sum_of_cod_collected is None:
                sum_of_cod_collected = 0

            sum_of_cod_amount = single_dg['sum_of_cod_amount']
            if sum_of_cod_amount is None:
                sum_of_cod_amount = 0

            if dg_ph_number is not None:
                dg = DeliveryGuy.objects.get(user__username=dg_ph_number)
                dg_full_name = dg.user.first_name + dg.user.last_name
            else:
                dg_full_name = 'Unassigned'

            cod_with_dg = "\n%s - COD: %s/%s" % \
                          (dg_full_name, sum_of_cod_collected, sum_of_cod_amount)
            email_body = email_body + "\n\n" + cod_with_dg
            # ===============================================================
            # For the same DG, specify vendor wise collection bifurcation,
            # For doing this, vendor and dg is being associated using order & filter by dg name and then by vendor name
            orders_tracked = OrderDeliveryStatus.objects.filter(
                delivery_guy__user__username=single_dg['delivery_guy__user__username'], date__gte=day_start,
                date__lte=day_end)
            orders_tracked = orders_tracked.filter(Q(order_status=constants.ORDER_STATUS_QUEUED) |
                                                   Q(order_status=constants.ORDER_STATUS_INTRANSIT) |
                                                   Q(order_status=constants.ORDER_STATUS_DELIVERED))
            orders_tracked = orders_tracked.filter(order__cod_amount__gt=0)
            vendor_tracked_per_order = orders_tracked.values('order__vendor__store_name').annotate(
                sum_of_cod_collected=Sum('cod_collected_amount'), sum_of_cod_amount=Sum('order__cod_amount'))
            for item in vendor_tracked_per_order:
                vendor_name = item['order__vendor__store_name']
                sum_of_cod_collected = item['sum_of_cod_collected']
                if sum_of_cod_collected is None:
                    sum_of_cod_collected = 0

                sum_of_cod_amount = item['sum_of_cod_amount']
                if sum_of_cod_amount is None:
                    sum_of_cod_amount = 0

                cod_with_vendor = ''
                cod_with_vendor = "\n  %s- COD: %s/%s" % (vendor_name, sum_of_cod_collected, sum_of_cod_amount)
                email_body = email_body + "\n" + cod_with_vendor

        # ---------------------------------------------------------------------------
        email_body = email_body + "\n----------------------------"
        email_body = email_body + "\n\n- YourGuy BOT"

        send_email(constants.EMAIL_COD_REPORT, email_subject, email_body)
        # ------------------------------------------------------------------------------------------------

def dg_report():
    date = datetime.today()
    day_start = ist_day_start(date)
    day_end = ist_day_end(date)

    # Number of dgs working today ----------------------------------------------------------------------
    dg_working_today_count = DGAttendance.objects.filter(date__gte=day_start, date__lte=day_end).count()

    # --------------------------------------------
    delivery_statuses_today = OrderDeliveryStatus.objects.filter(date__gte=day_start, date__lte=day_end)
    delivery_statuses_today = delivery_statuses_today.filter(
        Q(order_status=constants.ORDER_STATUS_QUEUED) |
        Q(order_status=constants.ORDER_STATUS_INTRANSIT) |
        Q(order_status=constants.ORDER_STATUS_PICKUP_ATTEMPTED) |
        Q(order_status=constants.ORDER_STATUS_DELIVERY_ATTEMPTED) |
        Q(order_status=constants.ORDER_STATUS_OUTFORDELIVERY) |
        Q(order_status=constants.ORDER_STATUS_DELIVERED)
    )
    all_dgs = delivery_statuses_today.values('delivery_guy__user__username'). \
        annotate(sum_of_cod_collected=Sum('cod_collected_amount'), sum_of_cod_amount=Sum('order__cod_amount'))

    delivery_statuses_without_attempted = delivery_statuses_today.exclude(order_status=constants.ORDER_STATUS_DELIVERY_ATTEMPTED)
    delivery_statuses_without_attempted = delivery_statuses_without_attempted.exclude(order_status=constants.ORDER_STATUS_PICKUP_ATTEMPTED)
    all_dgs_2 = delivery_statuses_without_attempted.values('delivery_guy__user__username'). \
        annotate(sum_of_cod_collected_without_attempted=Sum('cod_collected_amount'),
                 sum_of_cod_amount_without_attempted=Sum('order__cod_amount'))

    # This is for handling delivery attempted and pickup attempted case in COD
    # In both these cases, COD is not considered, but the order is still considered to be executed order
    for dg in all_dgs:
        dg_phone_number = dg['delivery_guy__user__username']
        filtered_dgs = all_dgs_2.filter(delivery_guy__user__username=dg_phone_number)
        if len(filtered_dgs) ==1:
            single = filtered_dgs[0]
            # for single in filtered_dgs:
            dg['sum_of_cod_collected'] = single['sum_of_cod_collected_without_attempted']
            dg['sum_of_cod_amount'] = single['sum_of_cod_amount_without_attempted']
        else:
            dg['sum_of_cod_collected'] = 0
            dg['sum_of_cod_amount'] = 0

    all_pgs = delivery_statuses_today.values('pickup_guy__user__username').annotate(
        sum_of_cod_amount=Sum('order__cod_amount'))

    all_ops_execs = Employee.objects.filter(department=constants.OPERATIONS)

    # -----------------------------------------------------------------------------------

    if dg_working_today_count == 0:
        today_string = datetime.now().strftime("%Y %b %d")
        email_subject = 'DG Report : %s' % (today_string)

        email_body = "Good Evening Guys,"
        email_body = email_body + "\n\n No DG working today."
        email_body = email_body + "\n\n- YourGuy BOT"

        send_email(constants.EMAIL_DG_REPORT, email_subject, email_body)
        return Response(status=status.HTTP_200_OK)
    else:
        # DG details for today
        today_string = datetime.now().strftime("%Y %b %d")
        email_subject = 'DG Report : %s' % (today_string)

        email_body = "Good Evening Guys, \nPlease find the dg report of the day."
        email_body = email_body + "\nTotal dgs working today = %s" % (dg_working_today_count)

        orders_executed_dg = delivery_statuses_today.filter(Q(order_status=constants.ORDER_STATUS_DELIVERY_ATTEMPTED) |
                                                            Q(order_status=constants.ORDER_STATUS_DELIVERED))

        orders_executed_pg = delivery_statuses_today.filter(Q(order_status=constants.ORDER_STATUS_PICKUP_ATTEMPTED) |
                                                            Q(order_status=constants.ORDER_STATUS_DELIVERY_ATTEMPTED) |
                                                            Q(order_status=constants.ORDER_STATUS_DELIVERED) |
                                                            Q(order_status=constants.ORDER_STATUS_OUTFORDELIVERY))

        for single_ops_exec in all_ops_execs:
            associated_guys = single_ops_exec.associate_delivery_guys.all()
            orders_count = 0
            executed_orders_count = 0
            assigned_orders_count = 0
            ops_cod_to_be_collected = 0
            ops_cod_collected = 0
            pgs_data = []
            dgs_data = []

            for single_pg in all_pgs:
                pg_ph_number = single_pg['pickup_guy__user__username']
                if pg_ph_number is not None:
                    pickup_guy = DeliveryGuy.objects.get(user__username=pg_ph_number)
                    if pickup_guy in associated_guys:
                        pickup_guy_full_name = pickup_guy.user.first_name + pickup_guy.user.last_name

                        no_of_assigned_orders = delivery_statuses_today.filter(pickup_guy__user__username=pg_ph_number).count()
                        assigned_orders_count = assigned_orders_count + no_of_assigned_orders

                        no_of_executed_orders = orders_executed_pg.filter(pickup_guy__user__username=pg_ph_number).count()
                        executed_orders_count = executed_orders_count + no_of_executed_orders
                        pgs_data.append("%s - Orders: %s/%s" % (pickup_guy_full_name, no_of_executed_orders,
                                                                              no_of_assigned_orders))
                else:
                    # Handle case when pg is not assigned to an order but dg is assigned to the same order
                    pass

            for single_dg in all_dgs:
                dg_ph_number = single_dg['delivery_guy__user__username']
                if dg_ph_number is not None:
                    dg = DeliveryGuy.objects.get(user__username=dg_ph_number)
                    if dg in associated_guys:
                        cod_collected = single_dg['sum_of_cod_collected']
                        if cod_collected is None:
                            cod_collected = 0

                        cod_to_be_collected = single_dg['sum_of_cod_amount']
                        if cod_to_be_collected is None:
                            cod_to_be_collected = 0

                        dg_full_name = dg.user.first_name + dg.user.last_name

                        no_of_assigned_orders = delivery_statuses_today.filter(delivery_guy__user__username=dg_ph_number).count()
                        assigned_orders_count = assigned_orders_count + no_of_assigned_orders

                        no_of_executed_orders = orders_executed_dg.filter(delivery_guy__user__username=dg_ph_number).count()
                        executed_orders_count = executed_orders_count + no_of_executed_orders
                        dgs_data.append("%s - Orders: %s/%s, COD: %s/%s" % (dg_full_name, no_of_executed_orders,
                                                                                          no_of_assigned_orders, cod_collected,
                                                                                          cod_to_be_collected))
                        ops_cod_to_be_collected = ops_cod_to_be_collected + cod_to_be_collected
                        ops_cod_collected = ops_cod_collected + cod_collected

                        orders_count = "%s/%s" %(executed_orders_count, assigned_orders_count)
                else:
                    # Handle Case when dg is not assigned to an order but pg is assigned to same order
                    pass

            email_body = email_body + "\n\nOPS EXECUTIVE %s - Orders: %s, COD: %s/%s"%(single_ops_exec.user.first_name,
                                                                                       orders_count, ops_cod_collected,
                                                                                       ops_cod_to_be_collected)
            email_body = email_body + "\nPickup boys:\n"
            for single in pgs_data:
                email_body = email_body + single +"\n"
            email_body = email_body + "Delivery Boys:\n"
            for single in dgs_data:
                email_body = email_body + single + "\n"
        # ---------------------------------------------------
        # For unassociated pgs and dgs
        all_associated_guys = []
        all_unassociated_pgs = []
        all_unassociated_dgs = []

        orders_count = 0
        assigned_orders_count = 0
        executed_orders_count = 0
        ops_cod_to_be_collected = 0
        ops_cod_collected = 0

        for single_ops_exec in all_ops_execs:
            all_associated_guys.extend(single_ops_exec.associate_delivery_guys.all())

        for single_pg in all_pgs:
            pg_ph_number = single_pg['pickup_guy__user__username']
            if pg_ph_number is not None:
                pickup_guy = DeliveryGuy.objects.get(user__username=pg_ph_number)
                if not (pickup_guy in all_associated_guys):
                    pickup_guy_full_name = pickup_guy.user.first_name + pickup_guy.user.last_name

                    no_of_assigned_orders = delivery_statuses_today.filter(pickup_guy__user__username=pg_ph_number).count()
                    assigned_orders_count = assigned_orders_count + no_of_assigned_orders

                    no_of_executed_orders = orders_executed_pg.filter(pickup_guy__user__username=pg_ph_number).count()
                    executed_orders_count = executed_orders_count + no_of_executed_orders
                    all_unassociated_pgs.append("%s - Orders: %s/%s" % (pickup_guy_full_name, no_of_executed_orders,
                                                                            no_of_assigned_orders))
        for single_dg in all_dgs:
            dg_ph_number = single_dg['delivery_guy__user__username']
            if dg_ph_number is not None:
                dg = DeliveryGuy.objects.get(user__username=dg_ph_number)
                if dg not in all_associated_guys:
                    cod_collected = single_dg['sum_of_cod_collected']
                    if cod_collected is None:
                        cod_collected = 0

                    cod_to_be_collected = single_dg['sum_of_cod_amount']
                    if cod_to_be_collected is None:
                        cod_to_be_collected = 0

                    dg_full_name = dg.user.first_name + dg.user.last_name

                    no_of_assigned_orders = delivery_statuses_today.filter(delivery_guy__user__username=dg_ph_number).count()
                    assigned_orders_count = assigned_orders_count + no_of_assigned_orders

                    no_of_executed_orders = orders_executed_dg.filter(delivery_guy__user__username=dg_ph_number).count()
                    executed_orders_count = executed_orders_count + no_of_executed_orders
                    all_unassociated_dgs.append("%s - Orders: %s/%s, COD: %s/%s" % (dg_full_name, no_of_executed_orders,
                                                                                        no_of_assigned_orders, cod_collected,
                                                                                        cod_to_be_collected))
                    ops_cod_to_be_collected = ops_cod_to_be_collected + cod_to_be_collected
                    ops_cod_collected = ops_cod_collected + cod_collected

                    orders_count = "%s/%s" %(executed_orders_count, assigned_orders_count)

        email_body = email_body + "\n\nUNASSOCIATED PICKP/DELIVERY BOYS - Orders: %s, COD: %s/%s"%(orders_count, ops_cod_collected,
                                                                                       ops_cod_to_be_collected)

        email_body = email_body + "\nPickup Boys:\n"
        for single in all_unassociated_pgs:
            email_body = email_body + single +"\n"
        email_body = email_body + "Delivery Boys:\n"
        for single in all_unassociated_dgs:
            email_body = email_body + single + "\n"

        email_body = email_body + "\n"
        email_body = email_body + "\n\n- YourGuy BOT"
        send_email(constants.EMAIL_DG_REPORT, email_subject, email_body)


@api_view(['GET'])
def vendor_report(request):
    date = datetime.today()
    day_start = ist_day_start(date)
    day_end = ist_day_end(date)

    # TOTAL ORDERS ----------------------------------------------------------------------
    # filter on today
    # filter on all orders statues
    # then group by vendor name to get sum_of_cod_collected and sum_of_cod_amount
    # iterate over this list and for each vendor check length of orders

    delivery_statuses_today = OrderDeliveryStatus.objects.filter(date__gte=day_start, date__lte=day_end)
    delivery_statuses_today = delivery_statuses_today.filter(
        Q(order_status=constants.ORDER_STATUS_QUEUED) |
        Q(order_status=constants.ORDER_STATUS_INTRANSIT) |
        Q(order_status=constants.ORDER_STATUS_PICKUP_ATTEMPTED) |
        Q(order_status=constants.ORDER_STATUS_DELIVERY_ATTEMPTED) |
        Q(order_status=constants.ORDER_STATUS_DELIVERED) |
        Q(order_status=constants.ORDER_STATUS_CANCELLED)
    )
    delivery_statuses_cancelled_today = delivery_statuses_today.filter(order_status=constants.ORDER_STATUS_CANCELLED)

    # Executed orders are delivery attempted and delivered orders since we charge the vendors under both these cases
    delivery_statuses_executed_today = delivery_statuses_today.filter(Q(order_status=constants.ORDER_STATUS_DELIVERY_ATTEMPTED) |
                                                                      Q(order_status=constants.ORDER_STATUS_DELIVERED))

    vendors_tracked = delivery_statuses_today.values('order__vendor__store_name'). \
        annotate(sum_of_cod_collected=Sum('cod_collected_amount'), sum_of_cod_amount=Sum('order__cod_amount'),
                 total_orders=Count('order'))

    # Adding COD exclusions for cancelled, pickup attempted and delivery attempted amount
    delivery_statuses_without_attempted = delivery_statuses_today.exclude(order_status=constants.ORDER_STATUS_DELIVERY_ATTEMPTED)
    delivery_statuses_without_attempted = delivery_statuses_without_attempted.exclude(order_status=constants.ORDER_STATUS_PICKUP_ATTEMPTED)
    vendors_tracked_2 = delivery_statuses_without_attempted.values('order__vendor__store_name'). \
        annotate(sum_of_cod_collected_without_attempted=Sum('cod_collected_amount'),
                 sum_of_cod_amount_without_attempted=Sum('order__cod_amount'), total_orders=Count('order'))

    # This is for handling delivery and pickup attempted case in COD
    # In both these cases, COD is not considered, but the order is still considered to be executed order
    for vendor in vendors_tracked:
        vendor_store_name = vendor['order__vendor__store_name']
        filtered_vendors = vendors_tracked_2.filter(order__vendor__store_name=vendor_store_name)
        if len(filtered_vendors) ==1:
            single = filtered_vendors[0]
            # for single in filtered_dgs:
            vendor['sum_of_cod_collected'] = single['sum_of_cod_collected_without_attempted']
            vendor['sum_of_cod_amount'] = single['sum_of_cod_amount_without_attempted']
        else:
            vendor['sum_of_cod_collected'] = 0
            vendor['sum_of_cod_amount'] = 0
    #=================================================================

    for item in vendors_tracked:
        vendor_name = item['order__vendor__store_name']
        sum_of_cod_collected = item['sum_of_cod_collected']
        sum_of_cod_amount = item['sum_of_cod_amount']
        orders_total_count = item['total_orders']

        vendors = Vendor.objects.get(store_name=vendor_name)
        vendor_mail_id = [vendors.email]

        # -----------------------------------------------------------------------------------

        if orders_total_count == 0:
            today_string = datetime.now().strftime("%Y %b %d")
            email_subject = 'YourGuy Vendor Report for %s: %s' % (vendor_name, today_string)

            email_body = "Good Evening,"
            email_body = email_body + "\n\n You have no orders today."
            email_body = email_body + "\n\n- YourGuy BOT"

            send_email(vendor_mail_id, email_subject, email_body)
            return Response(status=status.HTTP_200_OK)
        else:
            orders_for_this_vendor = OrderDeliveryStatus.objects.filter(date__gte=day_start, date__lte=day_end,
                                                                        order__vendor=vendors)
            list_of_orders = []
            for single_order in orders_for_this_vendor:
                order_ids = single_order.id
                list_of_orders.append(order_ids)

            cancelled_orders = delivery_statuses_cancelled_today.filter(order__vendor__store_name=vendor_name)
            count_cancelled_orders = len(cancelled_orders)

            executed_orders = delivery_statuses_executed_today.filter(order__vendor__store_name=vendor_name)
            count_executed_orders = len(executed_orders)

            today_string = datetime.now().strftime("%Y %b %d")
            email_subject = 'YourGuy Vendor Report for %s: %s' % (vendor_name, today_string)

            email_body = "Good Evening Guys, \n\nPlease find the report of the day."
            email_body = email_body + "\nTotal orders = %s" % (orders_total_count)
            email_body = email_body + "\nCancelled orders = %s" % (count_cancelled_orders)
            email_body = email_body + "\nExecuted orders = %s" % (count_executed_orders)
            email_body = email_body + "\nCOD supposed to be collected: %s" % (sum_of_cod_amount)
            email_body = email_body + "\nCOD collected: %s" % (sum_of_cod_collected)
            email_body = email_body + "\nAll order numbers: %s" % (list_of_orders)

            email_body = email_body + "\n-----------------------------------"
            email_body = email_body + "\n\n- YourGuy BOT"

            send_email(vendor_mail_id, email_subject, email_body)
    return Response(status=status.HTTP_200_OK)
