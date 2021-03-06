import base64
import os
import string
import calendar
from datetime import time, datetime, timedelta

import requests
from boto.s3.connection import S3Connection
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token

from api_v3 import constants
from server import settings
from yourguy.models import Order, OrderDeliveryStatus, VendorAgent, Consumer, Employee, NotificationType, DeliveryAction, ServiceablePincode, CODAction
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status

def response_structure():
    result = {
    'success': False,
    'payload': {
        # Application-specific data would go here. 
        'message':None,
        'data':None
    },
    'error': {
        'code': None,
        'message': None
        }
    }
    return result

def response_with_payload(data, message):
    response = response_structure()    
    payload = {
        'data': data,
        'message': message
    }
    response['payload'] = payload
    response['success'] = True
    response['error'] = None
    return Response(response, status=status.HTTP_200_OK) 

def response_success_with_message(message):
    response = response_structure()    
    response['success'] = True
    payload = {
        'data': None,
        'message': message
    }
    response['payload'] = payload
    response['error'] = None
    return Response(response, status=status.HTTP_200_OK) 

def response_access_denied():
    response = response_structure()    
    error = {
    'code':'101',
    'message':'Access Denied'
    }
    response['error'] = error
    response['payload'] = None
    return Response(response, status=status.HTTP_400_BAD_REQUEST) 

def response_incomplete_parameters(parameters):
    response = response_structure()    
    error = {
    'code':'102',
    'message':'Incomplete parameters %s'%(parameters)
    }
    response['error'] = error
    response['payload'] = None
    return Response(response, status=status.HTTP_400_BAD_REQUEST) 

def response_invalid_pagenumber():
    response = response_structure()  
    error = {
    'code':'103',
    'message':'Invalid page number'
    }
    response['error'] = error
    response['payload'] = None
    return Response(response, status=status.HTTP_400_BAD_REQUEST) 

def response_error_with_message(message):
    response = response_structure()  
    error = {
    'code':'104',
    'message':message
    }
    response['error'] = error
    response['payload'] = None
    return Response(response, status=status.HTTP_400_BAD_REQUEST) 

def ops_managers_for_pincode(pincode):
    result = []
    try:
        serving_pincode = get_object_or_404(ServiceablePincode, pincode = pincode)
        result = Employee.objects.filter(Q(serving_pincodes__in=[serving_pincode]) & Q(department=constants.OPERATIONS_MANAGER))
        return result
    except Exception as e:
        return result

def ops_executive_for_pincode(pincode):
    result = []
    try:
        serving_pincode = get_object_or_404(ServiceablePincode, pincode = pincode)
        result = Employee.objects.filter(Q(serving_pincodes__in=[serving_pincode]) & Q(department=constants.OPERATIONS))
        return result
    except Exception as e:
        return result

def ops_executive_for_dg(dg):
    result = []
    try:
        result = Employee.objects.filter(Q(associate_delivery_guys__in=[dg]) & Q(department=constants.OPERATIONS))    
        return result
    except Exception as e:
        return result

def ops_manager_for_dg(dg):
    result = []
    try:
        result = Employee.objects.filter(Q(associate_delivery_guys__in=[dg]) & Q(department=constants.OPERATIONS_MANAGER))    
        return result
    except Exception as e:
        return result

def notification_type_for_code(code):
    return get_object_or_404(NotificationType, code = code)

def s3_connection():
    AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
    return S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)


def s3_bucket_pod():
    return os.environ.get('S3_BUCKET_POD')

def address_string(address):
    try:
        if len(address.full_address) > 1:
            address_string = address.full_address 
            if address.landmark is not None and len(address.landmark) > 0:
                address_string += ', '
                address_string += address.landmark
            if address.pin_code is not None:
                address_string += ', '
                address_string += address.pin_code
        else:
            address_string = address.flat_number + ', ' + address.building + ', ' + address.street + ', ' + address.pin_code

        address_string = string.replace(address_string, ',,', '')
        address_string = string.replace(address_string, ', ,', '')
        return address_string
    except Exception as e:
        print(e)

def address_with_location(address):
    result = {
    "full_address": address_string(address),
    }

    if address.latitude is not None and address.longitude is not None and len(address.latitude) > 0 and len(address.longitude):
        location = {
        "latitude": address.latitude,
        "longitude": address.longitude        
        }
        result['location'] = location
    else:
        result['location'] = None
    return result


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
    ist_date = date + ist_timedelta
    day_start = datetime.combine(ist_date, time()).replace(hour=0, minute=0, second=0)
    return day_start - ist_timedelta


def ist_day_end(date):
    ist_timedelta = time_delta()
    ist_date = date + ist_timedelta
    day_end = datetime.combine(ist_date, time()).replace(hour=23, minute=59, second=59)
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
    elif role == constants.OPERATIONS:
        return constants.OPERATIONS
    elif role == constants.OPERATIONS_MANAGER:
        return constants.OPERATIONS_MANAGER
    elif role == constants.SALES:
        return constants.SALES
    elif role == constants.DELIVERY_GUY:
        return constants.DELIVERY_GUY
    elif role == constants.HR:
        return constants.HR
    elif role == constants.ACCOUNTS:
        return constants.ACCOUNTS
    else:
        return None


def log_exception(e, message):
    subject = 'Error has occurred.'
    body = message, e
    send_email(constants.EMAIL_ERRORS, subject, body)


def send_email(to_mail_ids, subject, body):
    try:
        if settings.ENVIRONMENT == 'PRODUCTION' or settings.ENVIRONMENT == 'STAGE':
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


def is_pickup_time_acceptable(pickup_datetime):
	current_datetime = datetime.now()
	if time(0, 0) <= pickup_datetime.time() <= time(18, 0) and pickup_datetime.date() >= current_datetime.date():
		return True
	else:
		return False


def inform_dgs_about_orders_assigned():
    pass
    # TODO


def delivery_actions(code):
    return DeliveryAction.objects.get(code=code)


def cod_actions(code):
    return CODAction.objects.get(code=code)

# Util method for calculating the month start date and end date
def check_month(month, year):
    month = int(month)
    year = int(year)
    start_date = datetime(year, month, 1)
    end_date = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, end_date)
    return {
        'start_date': start_date,
        'end_date': end_date
    }

