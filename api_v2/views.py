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

from yourguy.models import Vendor, Consumer, DeliveryGuy, VendorAgent, Address, OrderDeliveryStatus, Order
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

def assign_dg():
    
    # FETCH ALL TODAY ORDERS --------------------------------------------
    date = datetime.today()
    day_start = ist_day_start(date)
    day_end = ist_day_end(date)
    
    unassigned_order_ids = ''
    assigned_orders = ''

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
                    delivery_status.delivery_guy = latest_assigned_delivery.delivery_guy
                    delivery_status.save()                   
                    assigned_orders = assigned_orders + "\n %s - %s - %s - %s" % (vendor.store_name, order.id, consumer.user.first_name, delivery_guy.user.first_name)
            except Exception, e:                
                unassigned_order_ids = unassigned_order_ids + "\n %s - %s - %s" % (vendor.store_name, order.id, consumer.user.first_name)
                pass
                
        except Exception, e:
            pass
    
    
    
    # SEND AN EMAIL SAYING CANT FIND APPROPRAITE DELIVERY GUY FOR THIS ORDER. PLEASE ASSIGN MANUALLY
    today_string = datetime.now().strftime("%Y %b %d")
    email_subject = 'Unassigned orders for %s' % (today_string) 
    
    email_body = "Good Morning Guys, \nAssigned orders: %s \nUnassigned Orders: %s \nPlease assign manually. \n\n- Team YourGuy" % (assigned_orders, unassigned_order_ids)
    send_email(constants.OPS_EMAIL_IDS, email_subject, email_body)
    # ------------------------------------------------------------------------------------------------  

    # TODO
    #inform_dgs_about_orders_assigned()
    
    return

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
    send_email(['tech@yourguy.in'],'Scheduled test CRON at 5.30 IST','Scheduled testing CRON details')
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
