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

from yourguy.models import Vendor, Address, Consumer
from api.serializers import UserSerializer, OrderSerializer, AddressSerializer, ConsumerSerializer

import datetime
import random
import string

import constants

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

def is_vendorexists(phone_number):
	if Vendor.objects.filter(phone_number=phone_number).count():
		return True
	return False

def is_consumerexists(phone_number):
	if Consumer.objects.filter(phone_number=phone_number).count():
		return True
	return False


import base64
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


@api_view(['POST'])
def register_vendor(request):
	"""
	Registration for Vendor
	"""
	print request.user
	try:
		store = request.data['store_name']
		username = request.data['username']
		password = request.data['password']
		phone_number = request.data['phone_number']

		if is_userexists(username) is True:
			content = {'error':'user already exists'}	
			return Response(content, status = status.HTTP_404_NOT_FOUND)

		if is_vendorexists(phone_number) is True:
			content = {'error':'Vendor with same phone number exists'}	
			return Response(content, status = status.HTTP_404_NOT_FOUND)

		new_user = User.objects.create(username=username, password=password, email='')
		new_vendor = Vendor.objects.create(user=new_user, store_name=store, phone_number = phone_number)
		token = create_token(new_user, constants.VENDOR)

		content = {'user_id': new_user.id, 'vendor_id': new_vendor.id, 'auth_token': token.key }
		return Response(content, status = status.HTTP_201_CREATED)    			

	except Exception, e:
		raise e


@api_view(['POST'])
def register_consumer(request):
	"""
	Registration for Consumer
	"""
	try:
		print request.user
		print request.META

		username = request.data['username']
		phone_number = request.data['phone_number']

		if is_userexists(username) is True:
			content = {'error':'user already exists'}	
			return Response(content, status = status.HTTP_404_NOT_FOUND)

		if is_consumerexists(phone_number) is True:
			content = {'error':'Customer with same phone number exists'}	
			return Response(content, status = status.HTTP_404_NOT_FOUND)
		
		# Flat_number, Building Name, Street, Area Code
		flat_number = request.data['flat_number']
		building = request.data['building']
		street = request.data['street']
		area_code = request.data['area_code']

		#create address
		new_address = Address.objects.create(flat_number=flat_number, building=building, street=street, area_code= area_code)
		# TODO: Fetch vendor with token id and add it to associated_vendor
		
		new_user = User.objects.create(username=username, password=password, email='')
		new_consumer = Consumer.objects.create(user=new_user, phone_number = phone_number, address = new_address)
		token = create_token(new_user, constants.CONSUMER)

		content = {'auth_token': token.key, 'consumer_id':new_consumer.id , 'user_id':new_user.id}
		return Response(content, status = status.HTTP_201_CREATED)    			

	except Exception, e:
		raise e		