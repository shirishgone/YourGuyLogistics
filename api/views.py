# from django.shortcuts import render

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

from yourguy.models import Vendor, Address, Consumer, DeliveryGuy, VendorAgent, RequestedVendor
from api.serializers import UserSerializer, OrderSerializer, AddressSerializer, ConsumerSerializer

import datetime
import random
import string

import constants
import base64


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
	return False

def is_vendorexists(vendor_id):
	if Vendor.objects.filter(id=vendor_id).count():
		return True
	return False

def is_dgexists(phone_number):
	if is_userexists(phone_number):
		user = User.objects.get(username = phone_number)
		if DeliveryGuy.objects.filter(user=user).count():
			return True
		return False
	else:
		return False	

def is_consumerexists(phone_number):
	# import pdb
 #   	pdb.set_trace()

	if is_userexists(phone_number):
		user = User.objects.get(username = phone_number)
		if Consumer.objects.filter(user=user).count():
			return True
		else:	
			return False
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
	else:
		return None	

def verify_password(user, password):
	verified_user = authenticate(username=user.username, password=password)
	if verified_user is not None:
		return True
	else:
		return False

def create_consumer(phone_number, password, name, email):
	user = User.objects.create(username=phone_number, password=password)
	token = create_token(user, constants.CONSUMER)
	consumer = Consumer.objects.create(user = user)
	if name is not None:
		user.first_name = name
		user.save()
	if email is not None:
		user.email = email
		user.save()
	return consumer