# from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import Http404
from django.db.models.base import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

from rest_framework.authtoken.models import Token
from rest_framework import status, authentication, permissions, viewsets, serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from yourguy.models import Vendor, Consumer, DeliveryGuy, VendorAgent, Address, OrderDeliveryStatus, Order, DGAttendance
from api.serializers import UserSerializer, OrderSerializer, ConsumerSerializer

import dateutil.relativedelta
from datetime import datetime, timedelta, time
import random
import string

import constants
import base64
import requests

from boto.s3.connection import S3Connection
import os

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from api.views import send_email, ist_day_start, ist_day_end
from django.db.models import Q
from django.db.models import Sum

def assign_dg():
    
    # FETCH ALL TODAY ORDERS --------------------------------------------
    date = datetime.today()
    day_start = ist_day_start(date)
    day_end = ist_day_end(date)
    
    unassigned_order_ids = ''

    delivery_status_queryset = OrderDeliveryStatus.objects.filter(date__gte = day_start, date__lte = day_end, delivery_guy = None)            
    # FILTER BY ORDER STATUS --------------------------------------------------------------------
    delivery_status_queryset = delivery_status_queryset.filter(Q(order_status = constants.ORDER_STATUS_PLACED ) | Q(order_status = constants.ORDER_STATUS_QUEUED) | Q(order_status = constants.ORDER_STATUS_INTRANSIT)) 
    # ------------------------------------------------------------------------------------------------

    # --------------------------------------------------------------------
    for delivery_status in delivery_status_queryset.all():
        try:
            order = get_object_or_404(Order, delivery_status = delivery_status)
            
            # CUSTOMER AND VENDOR FILTERING -----------------------------------------------------------------
            vendor = order.vendor
            consumer = order.consumer
            
            previous_delivery_statuses = OrderDeliveryStatus.objects.filter(delivery_guy__isnull = False, order__consumer = consumer, order__vendor = vendor)
            # ------------------------------------------------------------------------------------------------

            # FILTER LAST 2 MONTHS ORDERS --------------------------------------------------------------------
            two_months_previous_date = day_start - dateutil.relativedelta.relativedelta(months = 1)
            previous_delivery_statuses = previous_delivery_statuses.filter(date__gte = two_months_previous_date, date__lte = day_start)
            # ------------------------------------------------------------------------------------------------

            # FILTERING BY PICKUP TIME RANGE -----------------------------------------------------------------
            pickup_hour = int(order.pickup_datetime.hour)
            previous_delivery_statuses = previous_delivery_statuses.filter(Q(order__pickup_datetime__hour = pickup_hour - 1 ) | Q(order__pickup_datetime__hour = pickup_hour) | Q(order__pickup_datetime__hour = pickup_hour + 1 ))
            # ------------------------------------------------------------------------------------------------

            # FILTERING BY PICKUP TIME RANGE -----------------------------------------------------------------
            try:
                latest_assigned_delivery = previous_delivery_statuses.latest('date')            
                if latest_assigned_delivery is not None:
                    req_delivery_guy = latest_assigned_delivery.delivery_guy
                    delivery_status.delivery_guy = req_delivery_guy
                    delivery_status.save()                   
            except Exception, e:                
                unassigned_order_ids = unassigned_order_ids + "\n %s - %s - %s" % (vendor.store_name, order.id, consumer.user.first_name)
                pass
                
        except Exception, e:
            pass
    
    
    # SEND AN EMAIL SAYING CANT FIND APPROPRAITE DELIVERY GUY FOR THIS ORDER. PLEASE ASSIGN MANUALLY
    today_string = datetime.now().strftime("%Y %b %d")
    email_subject = 'Unassigned orders for %s' % (today_string) 
    
    email_body = "Good Morning Guys, \nUnassigned Orders: %s \nPlease assign manually. \n\n- Team YourGuy" % (unassigned_order_ids)
    send_email(constants.EMAIL_UNASSIGNED_ORDERS, email_subject, email_body)
    # ------------------------------------------------------------------------------------------------  

    # TODO
    #inform_dgs_about_orders_assigned()    
    return
    

@api_view(['GET'])
def daily_report(request):
    
    date = datetime.today()
    day_start = ist_day_start(date)
    day_end = ist_day_end(date)
    
    # TOTAL ORDERS ----------------------------------------------------------------------
    delivery_statuses_today = OrderDeliveryStatus.objects.filter(date__gte = day_start, date__lte = day_end)            
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
        return Response(status = status.HTTP_200_OK)
    
    else:
        # TOTAL ORDERS ASSIGNED vs UNASSIGNED ORDERS ----------------------------------------
        orders_unassigned_count = delivery_statuses_today.filter(delivery_guy = None).count()
        orders_assigned_count = orders_total_count - orders_unassigned_count

        orders_unassigned_percentage = "{0:.0f}%".format(float(orders_unassigned_count)/float(orders_total_count) * 100)
        orders_assigned_percentage = "{0:.0f}%".format(float(orders_assigned_count)/float(orders_total_count) * 100)
        # -----------------------------------------------------------------------------------
    
        # ORDERS ACC TO ORDER_STATUS --------------------------------------------------------
        orders_placed_count                 = delivery_statuses_today.filter(order_status = constants.ORDER_STATUS_PLACED).count()
        
        orders_queued_count                 = delivery_statuses_today.filter(order_status = constants.ORDER_STATUS_QUEUED).count()
        orders_queued_percentage            = "{0:.0f}%".format(float(orders_queued_count)/float(orders_total_count) * 100)
        
        orders_intransit_count              = delivery_statuses_today.filter(order_status = constants.ORDER_STATUS_INTRANSIT).count()
        orders_intransit_percentage         = "{0:.0f}%".format(float(orders_intransit_count)/float(orders_total_count) * 100)

        orders_delivered_count              = delivery_statuses_today.filter(order_status = constants.ORDER_STATUS_DELIVERED).count()
        orders_delivered_percentage         = "{0:.0f}%".format(float(orders_delivered_count)/float(orders_total_count) * 100)

        orders_pickup_attempted_count       = delivery_statuses_today.filter(order_status = constants.ORDER_STATUS_PICKUP_ATTEMPTED).count()
        orders_pickup_attempted_percentage  = "{0:.0f}%".format(float(orders_pickup_attempted_count)/float(orders_total_count) * 100)

        orders_delivery_attempted_count     = delivery_statuses_today.filter(order_status = constants.ORDER_STATUS_DELIVERY_ATTEMPTED).count()
        orders_delivert_attempted_percentage= "{0:.0f}%".format(float(orders_delivery_attempted_count)/float(orders_total_count) * 100)

        orders_rejected_count               = delivery_statuses_today.filter(order_status = constants.ORDER_STATUS_REJECTED).count()
        orders_rejected_percentage          = "{0:.0f}%".format(float(orders_rejected_count)/float(orders_total_count) * 100)

        orders_canceled_count               = delivery_statuses_today.filter(order_status = constants.ORDER_STATUS_CANCELLED).count()
        orders_canceled_percentage          = "{0:.0f}%".format(float(orders_canceled_count)/float(orders_total_count) * 100)
    
        pending_orders_count        = orders_queued_count + orders_placed_count + orders_intransit_count
        pending_orders_percentage   = "{0:.0f}%".format(float(pending_orders_count)/float(orders_total_count) * 100)

        completed_orders_count      = orders_delivered_count + orders_pickup_attempted_count + orders_delivery_attempted_count + orders_rejected_count + orders_canceled_count
        completed_orders_percentage = "{0:.0f}%".format(float(completed_orders_count)/float(orders_total_count) * 100)    
        # -----------------------------------------------------------------------------------

        # DG ATTENDANCE DETAILS -------------------------------------------------------------
        total_dg_count = DeliveryGuy.objects.all().count()
        total_dg_checked_in_count = DGAttendance.objects.filter(date__year = date.year, date__month = date.month, date__day = date.day).count()
        dg_checkin_percentage = "{0:.0f}%".format(float(total_dg_checked_in_count)/float(total_dg_count) * 100)
        # -----------------------------------------------------------------------------------
    
        # TOTAL COD COLLECTED Vs SUPPOSSED TO BE COLLECTED ----------------------------------
        total_cod_collected = delivery_statuses_today.aggregate(Sum('cod_collected_amount'))
        total_cod_collected = total_cod_collected['cod_collected_amount__sum']

        orders = Order.objects.filter(delivery_status = delivery_statuses_today)
        total_cod_to_be_collected = orders.aggregate(Sum('cod_amount'))
        total_cod_to_be_collected = total_cod_to_be_collected['cod_amount__sum']
        cod_collected_percentage = "{0:.0f}%".format(float(total_cod_collected)/float(total_cod_to_be_collected) * 100)
        # -----------------------------------------------------------------------------------

        # DELIVERY BOY WHO HAVE COD --------------------------------------------------------    
        cod_deliveries = delivery_statuses_today.filter(cod_collected_amount__gt = 0)
        cod_with_delivery_boys = cod_deliveries.values('delivery_guy__user__first_name').annotate(total=Sum('cod_collected_amount'))

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

        email_body = email_body + "\nPending orders     = %s [%s percent]" % (pending_orders_count, pending_orders_percentage)
        email_body = email_body + "\nExecuted orders    = %s [%s percent]" % (completed_orders_count, completed_orders_percentage)

        email_body = email_body + "\n\nSTATUS WISE BIFURGATION ------------"
        email_body = email_body + "\nOrders assigned    = %s [%s percent]" % (orders_assigned_count, orders_assigned_percentage)    
        email_body = email_body + "\nOrders unassigned  = %s [%s percent]" % (orders_unassigned_count, orders_unassigned_percentage)
        email_body = email_body + "\nQueued         = %s [%s percent]" % (orders_queued_count, orders_queued_percentage)
        email_body = email_body + "\nInTransit      = %s [%s percent]" % (orders_intransit_count, orders_intransit_percentage)
        email_body = email_body + "\ndelivered      = %s [%s percent]" % (orders_delivered_count, orders_delivered_percentage)
        email_body = email_body + "\nPickup Attempted   = %s [%s percent]" % (orders_pickup_attempted_count, orders_pickup_attempted_percentage)
        email_body = email_body + "\nDelivery Attempted = %s [%s percent]" % (orders_delivery_attempted_count, orders_delivered_percentage)
        email_body = email_body + "\nRejected       = %s [%s percent]" % (orders_rejected_count, orders_rejected_percentage)
        email_body = email_body + "\nCanceled       = %s [%s percent]" % (orders_canceled_count, orders_canceled_percentage)
        email_body = email_body + "\n------------------------------------"
    
        email_body = email_body + "\n\nDELIVERY BOY ATTENDANCE -------"
        email_body = email_body + "\nTotal DGs on app   = %s" % total_dg_count  
        email_body = email_body + "\nTotal DGs CheckIn  = %s [%s percent]" % (total_dg_checked_in_count, dg_checkin_percentage)
        email_body = email_body + "\n-----------------------------------"
    
        email_body = email_body + "\n\nCOD DETAILS ------------------"
        email_body = email_body + "\nTotal COD to be collected  = %s" % total_cod_to_be_collected  
        email_body = email_body + "\nTotal COD collected        = %s [%s percent]" % (total_cod_collected, cod_collected_percentage)
        
        email_body = email_body + "\n-----------------------------------"
    
        email_body = email_body + "\n\nCOD WITH EACH DG ------------------"
        email_body = email_body + cod_with_dg_string
        email_body = email_body + "\n-----------------------------------"    
        email_body = email_body + "\n\n- YourGuy BOT"

        send_email(constants.EMAIL_DAILY_REPORT, email_subject, email_body)
        # ------------------------------------------------------------------------------------------------  
    
    return Response(status = status.HTTP_200_OK)


def inform_dgs_about_orders_assigned():
    
    # FETCH ALL ORDERS ASSIGNED TO DGs --------------------------------------------
    date = datetime.today()
    day_start = ist_day_start(date)
    day_end = ist_day_end(date)
    try:
        delivery_status_queryset = OrderDeliveryStatus.objects.filter(delivery_guy__isnull = False, date__gte = day_start, date__lte = day_end).annotate('delivery_guy')
    except Exception, e:
        print e
    # --------------------------------------------------------------------


@api_view(['GET'])
def cron_trial(request):
    print('Scheduled job trial method is called.')
    assign_dg()    
    return Response(status = status.HTTP_200_OK)

def paginate(list, page):    
    paginator = Paginator(list, constants.PAGINATION_PAGE_SIZE) # Show 25 contacts per page
    try:
        result = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        result = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        result = paginator.page(paginator.num_pages)

    return result.object_list
