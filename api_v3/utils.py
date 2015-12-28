import base64
import os
import string
from datetime import time, datetime, timedelta

import requests
from boto.s3.connection import S3Connection
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api_v3 import constants
from server import settings
from yourguy.models import Order, OrderDeliveryStatus, VendorAgent, Consumer


def s3_connection():
    AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
    return S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)


def s3_bucket_pod():
    return os.environ.get('S3_BUCKET_POD')


def address_string(address):
    try:
        if len(address.full_address) > 1:
            address_string = address.full_address + ', ' + address.pin_code
        else:
            address_string = address.flat_number + ', ' + address.building + ', ' + address.street + ', ' + address.pin_code

        address_string = string.replace(address_string, ',,', '')
        address_string = string.replace(address_string, ', ,', '')
        return address_string
    except Exception as e:
        print(e)


def is_correct_pincode(pincode):
    if pincode.isdigit() and len(pincode) == 6:
        return True
    else:
        return False


def is_vendor_has_same_address_already(vendor, pincode):
    try:
        addresses = vendor.addresses.all()
        for address in addresses:
            if address.pin_code == pincode:
                return address
        return None
    except Exception as e:
        return None


def is_consumer_has_same_address_already(consumer, pincode):
    try:
        addresses = consumer.addresses.all()
        for address in addresses:
            if address.pin_code == pincode:
                return address
        return None
    except Exception as e:
        return None


def is_userexists(username):
    if User.objects.filter(username=username).count():
        return True
    else:
        return False


def is_consumerexists(user):
    if Consumer.objects.filter(user=user).count():
        return True
    else:
        return False


def is_groupexists(name):
    if Group.objects.filter(name=name).count():
        return True
    else:
        return False


def assign_usergroup_with_name(user, group_name):
    try:
        group = Group.objects.get(name=group_name)
        group.user_set.add(user)
        return True
    except:
        return False


def assign_usergroup(user):
    if is_groupexists(user_role(user)):
        role = user_role(user)
        return assign_usergroup_with_name(user, role)
    else:
        return False


def time_delta():
    return timedelta(hours=5, minutes=30)


def ist_day_start(date):
    ist_timedelta = time_delta()
    day_start = datetime.combine(date, time()).replace(hour=0, minute=0, second=0)
    return day_start - ist_timedelta


def ist_day_end(date):
    ist_timedelta = time_delta()
    day_end = datetime.combine(date, time()).replace(hour=23, minute=59, second=59)
    return day_end - ist_timedelta


def ist_datetime(datetime):
    ist_timedelta = time_delta()
    return datetime + ist_timedelta


def days_in_int(by_day):
    day_values = {'MO': 0, 'TU': 1, 'WE': 2, 'TH': 3, 'FR': 4, 'SA': 5, 'SU': 6}
    int_days = []
    for day in by_day:
        int_days.append(day_values[day])
    return int_days


def is_today_date(date):
    today = datetime.now()
    if today.date() == date.date():
        return True
    else:
        return False


def create_token(user, user_role):
    if Token.objects.filter(user=user).count():
        token = get_object_or_404(Token, user=user)
    else:
        full_string = '%s:%s' % (user.username, user_role)
        token_string = base64.b64encode(full_string)
        token = Token.objects.create(user=user, key=token_string)
    return token


def user_role(user):
    token = Token.objects.get(user=user)
    token_string = base64.b64decode(token.key)
    role = token_string.split(':').pop()
    if role == constants.VENDOR:
        return constants.VENDOR
    elif role == constants.CONSUMER:
        return constants.CONSUMER
    elif role == constants.OPERATIONS:
        return constants.OPERATIONS
    elif role == constants.SALES:
        return constants.SALES
    elif role == constants.DELIVERY_GUY:
        return constants.DELIVERY_GUY
    else:
        return None


def log_exception(e, message):
    subject = 'Error has occurred.'
    body = message, e
    send_email(constants.EMAIL_ERRORS, subject, body)


def send_email(to_mail_ids, subject, body):
    try:
        if settings.ENVIRONMENT == 'PRODUCTION':
            send_mail(subject, body, constants.FROM_MAIL_ID, to_mail_ids, fail_silently=False)
        else:
            print('Emails are not sent during testing')
    except Exception as e:
        pass


def send_sms(phonenumber, message):
    url = constants.SMS_URL.format(mobile_number=phonenumber, message_text=message)
    try:
        if settings.ENVIRONMENT == 'PRODUCTION':
            r = requests.get(url)
        else:
            print('test doesnt send sms')
    except Exception as e:
        pass


def is_vendoragentexists(user):
    if VendorAgent.objects.filter(user=user).count():
        return True
    else:
        return False


def paginate(list, page):
    paginator = Paginator(list, constants.PAGINATION_PAGE_SIZE)  # Show 25 contacts per page
    try:
        result = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        result = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        result = paginator.page(paginator.num_pages)

    return result.object_list


def is_pickup_time_acceptable(datetime):
    if time(0, 0) <= datetime.time() <= time(16, 30):
        return True
    else:
        return False


def inform_dgs_about_orders_assigned():
    pass
    # TODO


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
