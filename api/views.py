# from django.shortcuts import render
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

from yourguy.models import Vendor, Consumer, DeliveryGuy, VendorAgent
from api.serializers import UserSerializer, OrderSerializer, ConsumerSerializer

from datetime import datetime, timedelta, time
import random
import string

import constants
import base64
import requests

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
		send_mail(subject, body, constants.FROM_MAIL_ID, to_mail_ids, fail_silently=False)
	except Exception, e:
		pass

def send_sms(phonenumber, message):
    url = constants.SMS_URL.format(mobile_number=phonenumber, message_text=message)
    try:
        r = requests.get(url)
    except:
        send_email('SMS error', 'problem sending SMS \nplease check {} {}'.format(phonenumber,message), constants.FROM_MAIL_ID, ['tech@yourguy.in'], fail_silently=False)


def verify_password(user, password):
	verified_user = authenticate(username=user.username, password=password)
	if verified_user is not None:
		return True
	else:
		return False


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


def delivery_status_of_the_day(order, date):
	delivery_statuses = order.delivery_status.all()
	for delivery_status in delivery_statuses:
		date_1 = datetime.combine(date, time()).replace(hour=0, minute=0, second=0)
		date_2 = datetime.combine(delivery_status.date, time()).replace(hour=0, minute=0, second=0)
		if date_1 == date_2:
			delivery_item = delivery_status
			break
	return delivery_item  	

def update_daily_status(order, date):
	delivery_status = delivery_status_of_the_day(order, date)
	order.delivered_at = delivery_status.delivered_at
	order.pickedup_datetime = delivery_status.pickedup_datetime
	order.completed_datetime = delivery_status.completed_datetime
	order.order_status = delivery_status.order_status
	order.delivery_guy = delivery_status.delivery_guy
	return order

    
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
