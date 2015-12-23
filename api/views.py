# from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import Http404
from django.db.models.base import ObjectDoesNotExist

from rest_framework.authtoken.models import Token
from rest_framework import status, authentication, permissions, viewsets, serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from yourguy.models import Vendor, Consumer, DeliveryGuy, VendorAgent, Address
from api.serializers import UserSerializer, OrderSerializer, ConsumerSerializer

from datetime import datetime, timedelta, time
import random
import string

import constants
import base64
import requests

from boto.s3.connection import S3Connection
import os

import datetime
import pytz
from datetime import datetime, timedelta, time
from server import settings

def s3_connection():
    AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
    return S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)

def s3_bucket_pod():
    return os.environ.get('S3_BUCKET_POD')

def days_in_int(by_day):
	day_values = {'MO':0, 'TU':1 , 'WE':2 , 'TH':3 , 'FR':4 , 'SA':5 , 'SU': 6}
	int_days = []
	for day in by_day:
		int_days.append(day_values[day])
	return int_days

def generate_random_number(size):
	"""
	:param size:
	:return:
	"""
	char_set = string.ascii_uppercase + string.digits + string.ascii_lowercase
	token = ''.join(random.sample(char_set * size, size))
	return token

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

def is_vendoragentexists(user):
	if VendorAgent.objects.filter(user=user).count():
		return True
	else:	
		return False	

def is_vendorexists(vendor_id):
	if Vendor.objects.filter(id=vendor_id).count():
		return True
	else:
		return False

def is_dgexists(user):
	if DeliveryGuy.objects.filter(user=user).count():
		return True
	else:
		return False

def create_token(user,user_role):
	if Token.objects.filter(user=user).count():
		token = get_object_or_404(Token, user = user)
	else:
		full_string = '%s:%s'% (user.username, user_role)
		token_string = base64.b64encode(full_string)
		token = Token.objects.create(user = user, key= token_string)
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

def send_email(to_mail_ids, subject, body):
	try:
		if settings.ENVIRONMENT == 'PRODUCTION':
			send_mail(subject, body, constants.FROM_MAIL_ID, to_mail_ids, fail_silently=False)
		else:
			print 'test doesnt send emails'	
	except Exception, e:
		pass

def send_sms(phonenumber, message):
	url = constants.SMS_URL.format(mobile_number=phonenumber, message_text=message)
	try:
		if settings.ENVIRONMENT == 'PRODUCTION':
			r = requests.get(url)
		else:
			print 'test doesnt send sms'
	except Exception, e:
		pass

def verify_password(user, password):
	verified_user = authenticate(username=user.username, password=password)
	if verified_user is not None:
		return True
	else:
		return False

def is_address_exists(flat_number, building, street, landmark, pin_code):
	try:
		addresses = Address.objects.filter(flat_number = flat_number, 
			building = building,
			street = street,
			landmark = landmark,
			pin_code = pin_code)
		if len(addresses) > 0:
			return addresses[0]
		else:
			return None
	except:
		return None

def log_exception(e, message):
	print e
	# SEND AN EMAIL OR LOG IT SOMEWHERE
	# TODO

# TIME ZONE ISSUES =============
def is_today_date(date):
	today = datetime.now()
	if today.date() == date.date():
		return True
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
    #day_start = datetime.combine(date, time()).replace(hour=0, minute=0, second=0)
    return datetime + ist_timedelta

# =============

def normalize_offset_awareness(dt, from_dt=None):
    """
    Given two `datetime.datetime` objects, return the second object as
    timezone offset-aware or offset-naive depending on the existence
    of the first object's tzinfo.
    If the second object is to be made offset-aware, it is assumed to
    be in the local timezone (with the timezone derived from the
    TIME_ZONE setting). If it is to be made offset-naive, It is first
    converted to the local timezone before being made naive.
    :Parameters:
        `dt` : `datetime.datetime`
            The datetime object to make offset-aware/offset-naive.
        `from_dt` : `datetime.datetime`
            The datetime object to test the existence of a tzinfo. If
            the value is nonzero, it will be understood as
            offset-naive
    """
    if from_dt and from_dt.tzinfo and dt.tzinfo:
        return dt
    elif from_dt and from_dt.tzinfo and not dt.tzinfo:
        dt = localtz.localize(dt)
    elif dt.tzinfo:
        dt = dt.astimezone(localtz)
        dt = datetime.datetime(
            dt.year, dt.month, dt.day,
            dt.hour, dt.minute, dt.second)
    return dt


class IsAuthenticatedOrWriteOnly(permissions.BasePermission):
    """
    The request is authenticated as a user, or is a write-only request.
    """

    def has_permission(self, request, view):
        WRITE_METHODS = ["POST", ]

        return (
            request.method in WRITE_METHODS or
            request.user and
            request.user.is_authenticated()
        )
