from datetime import datetime

from django.db.models import Sum, Q, F
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api_v3 import constants
from api_v3.utils import send_email, ist_day_start, ist_day_end
from yourguy.models import DeliveryGuy, OrderDeliveryStatus, DGAttendance


@api_view(['GET'])
def daily_report(request):
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
        return Response(status=status.HTTP_200_OK)

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

        executable_deliveries = delivery_statuses_today.filter(
            Q(order_status=constants.ORDER_STATUS_QUEUED) |
            Q(order_status=constants.ORDER_STATUS_INTRANSIT) |
            Q(order_status=constants.ORDER_STATUS_DELIVERED) |
            Q(order_status=constants.ORDER_STATUS_DELIVERY_ATTEMPTED) |
            Q(order_status=constants.ORDER_STATUS_PICKUP_ATTEMPTED))
        total_cod_dict = executable_deliveries.aggregate(total_cod=Sum('order__cod_amount'))
        total_cod_to_be_collected = total_cod_dict['total_cod']

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
            cod_with_dg_string = cod_with_dg_string + "\n%s = %s" % (delivery_guy, total)
        # -----------------------------------------------------------------------------------

        # SEND AN EMAIL SAYING CANT FIND APPROPRAITE DELIVERY GUY FOR THIS ORDER. PLEASE ASSIGN MANUALLY
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
        
        return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def cod_report(request):
    date = datetime.today()
    day_start = ist_day_start(date)
    day_end = ist_day_end(date)

    # TOTAL ORDERS ----------------------------------------------------------------------
    delivery_statuses_today = OrderDeliveryStatus.objects.filter(date__gte=day_start, date__lte=day_end, order__cod_amount__gt = 0)
    orders_total_count = len(delivery_statuses_today)
    # -----------------------------------------------------------------------------------

    if orders_total_count == 0:
        today_string = datetime.now().strftime("%Y %b %d")
        email_subject = 'COD Report : %s' % (today_string)

        email_body = "Good Evening Guys,"
        email_body = email_body + "\n\n No COD today on the app."
        email_body = email_body + "\n\n- YourGuy BOT"

        send_email(constants.EMAIL_COD_REPORT, email_subject, email_body)
        return Response(status=status.HTTP_200_OK)
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
        orders_executed = orders_executed_queryset.aggregate(sum_of_cod_collected=Sum('cod_collected_amount'),sum_of_cod_amount=Sum('order__cod_amount'))
        delivered_cod_collected = orders_executed['sum_of_cod_collected']
        delivered_cod_amount = orders_executed['sum_of_cod_amount']

        pending_cod = delivered_cod_amount - delivered_cod_collected
        pending_cod_amount = pending_cod_amount + pending_cod

        orders_executed_queryset = delivery_statuses_today.filter(order_status=constants.ORDER_STATUS_DELIVERED)
        orders_executed = orders_executed_queryset.aggregate(sum_of_cod_collected=Sum('cod_collected_amount'),sum_of_cod_amount=Sum('order__cod_amount'))
        delivered_cod_collected = orders_executed['sum_of_cod_collected']
        delivered_cod_amount = orders_executed['sum_of_cod_amount']

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
            sum_of_cod_amount = item['sum_of_cod_amount']
            cod_with_vendor = cod_with_vendor + \
                              "\n%s, %s/%s" % \
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
            sum_of_cod_amount = single_dg['sum_of_cod_amount']

            if dg_ph_number is not None:
                dg = DeliveryGuy.objects.get(user__username=dg_ph_number)
                dg_full_name = dg.user.first_name + dg.user.last_name
            else:
                dg_full_name = 'Unassigned'

            cod_with_dg = "\n%s, %s/%s" % \
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
                sum_of_cod_amount = item['sum_of_cod_amount']
                cod_with_vendor = ''
                cod_with_vendor = "\n  %s, %s/%s" %(vendor_name, sum_of_cod_collected, sum_of_cod_amount)
                email_body = email_body + "\n" + cod_with_vendor

        # ---------------------------------------------------------------------------
        email_body = email_body + "\n----------------------------"
        email_body = email_body + "\n\n- YourGuy BOT"

        send_email(constants.EMAIL_COD_REPORT, email_subject, email_body)
        return Response(status=status.HTTP_200_OK)
    # ------------------------------------------------------------------------------------------------


@api_view(['GET'])
def dg_report(request):
    date = datetime.today()
    day_start = ist_day_start(date)
    day_end = ist_day_end(date)

    # Number of dgs working today ----------------------------------------------------------------------
    dg_working_today_count = 0
    attendance = DGAttendance.objects.all()
    for single in attendance:
        attendance_status = single.status
        if attendance_status == constants.DG_STATUS_WORKING:
            dg_working_today_count = dg_working_today_count + 1
        else:
            pass
    # --------------------------------------------
    delivery_statuses_today = OrderDeliveryStatus.objects.filter(date__gte=day_start, date__lte=day_end)
    delivery_statuses_today = delivery_statuses_today.filter(
            Q(order_status=constants.ORDER_STATUS_QUEUED) |
            Q(order_status=constants.ORDER_STATUS_INTRANSIT) |
            Q(order_status=constants.ORDER_STATUS_PICKUP_ATTEMPTED) |
            Q(order_status=constants.ORDER_STATUS_DELIVERY_ATTEMPTED) |
            Q(order_status=constants.ORDER_STATUS_DELIVERED)
            )
    delivery_statuses_today = delivery_statuses_today.exclude(delivery_guy=None)
    delivery_statuses_today = delivery_statuses_today.exclude(pickup_guy=None)
    all_dgs = delivery_statuses_today.values('delivery_guy__user__username').\
        annotate(sum_of_cod_collected=Sum('cod_collected_amount'), sum_of_cod_amount=Sum('order__cod_amount'))

    all_pickup_guys = delivery_statuses_today.values('pickup_guy__user__username').annotate(sum_of_cod_amount=Sum('order__cod_amount'))

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

        email_body = "Good Evening Guys, \n\nPlease find the dg report of the day."
        email_body = email_body + "\n\nTotal dgs working today = %s" % (dg_working_today_count)

        email_body = email_body + "\n\nPICKUP BOY DETAILS -------\n"

        orders_executed = delivery_statuses_today.filter(order_status=constants.ORDER_STATUS_DELIVERED)

        for single_pickup_guy in all_pickup_guys:
            pickup_guy_ph_number = single_pickup_guy['pickup_guy__user__username']

            pickup_guy = DeliveryGuy.objects.get(user__username=pickup_guy_ph_number)
            pickup_guy_full_name = pickup_guy.user.first_name + pickup_guy.user.last_name

            orders_assigned_tracked = delivery_statuses_today.filter(delivery_guy__user__username=single_pickup_guy['pickup_guy__user__username'])
            no_of_assigned_orders = len(orders_assigned_tracked)

            orders_executed_tracked = orders_executed.filter(delivery_guy__user__username=single_pickup_guy['pickup_guy__user__username'])
            no_of_executed_orders = len(orders_executed_tracked)

            email_body = email_body + "\n\n%s, %s/%s" %(pickup_guy_full_name, no_of_executed_orders, no_of_assigned_orders)
            email_body = email_body + "\n-----------------------------------"


        email_body = email_body + "\n\nDELIVERY BOY DETAILS -------\n* COD of Cancelled orders are not considered."

        for single_dg in all_dgs:
            dg_ph_number = single_dg['delivery_guy__user__username']
            cod_collected = single_dg['sum_of_cod_collected']
            cod_to_be_collected = single_dg['sum_of_cod_amount']

            dg = DeliveryGuy.objects.get(user__username=dg_ph_number)
            dg_first_name = dg.user.first_name
            dg_last_name = dg.user.last_name
            dg_full_name = dg_first_name + dg_last_name

            orders_assigned_tracked = delivery_statuses_today.filter(delivery_guy__user__username=single_dg['delivery_guy__user__username'])
            no_of_assigned_orders = len(orders_assigned_tracked)

            orders_executed_tracked = orders_executed.filter(delivery_guy__user__username=single_dg['delivery_guy__user__username'])
            no_of_executed_orders = len(orders_executed_tracked)

            email_body = email_body + "\n\n%s, %s/%s, %s/%s" %(dg_full_name, no_of_executed_orders,
                                                        no_of_assigned_orders, cod_collected, cod_to_be_collected)
            email_body = email_body + "\n-----------------------------------"

        email_body = email_body + "\n-----------------------------------"
        email_body = email_body + "\n\n- YourGuy BOT"

        send_email(constants.EMAIL_DG_REPORT, email_subject, email_body)
        return Response(status=status.HTTP_200_OK)
