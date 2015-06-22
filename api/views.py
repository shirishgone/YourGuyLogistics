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

import datetime
import random
import string

import constants
import base64
import requests

def days_in_int(by_day):
	day_values = {'MO':0, 'TU':1 , 'WE':2 , 'TU':3 , 'FR':4 , 'SA':5 , 'SU': 6}
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

def send_email(subject, body):
	try:
		send_mail(subject, body, constants.FROM_MAIL_ID, constants.TO_EMAIL_IDS, fail_silently=False)        
	except Exception, e:
		pass

def send_sms(phonenumber, message):
    # url = "http://api.smscountry.com/SMSCwebservice_bulk.aspx?User=shirishgone&passwd=shirish542&mobilenumber={mobile_number}&message={message_text}&sid=GTTEAM&mtype=N&DR=Y".format(mobile_number=mobilenumber, message_text=message)
    url = "http://api.smscountry.com/SMSCwebservice_bulk.aspx?User=yourguy&passwd=yourguydotin&mobilenumber={mobile_number}&message={message_text}&mtype=N&DR=Y".format(mobile_number=phonenumber, message_text=message)
    try:
        r = requests.get(url)
    except:
        send_email('SMS error', 'problem sending SMS \nplease check {} {}'.format(phonenumber,message),
              SERVER_MAIL, ['tech@yourguy.in'], fail_silently=False)


def verify_password(user, password):
	verified_user = authenticate(username=user.username, password=password)
	if verified_user is not None:
		return True
	else:
		return False

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
