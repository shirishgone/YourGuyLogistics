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

from yourguy.models import Vendor, Address, Consumer, DeliveryGuy, VendorAgent
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
	if Vendor.objects.filter(username=phone_number).count():
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
	if is_userexists(phone_number):
		user = User.objects.get(username = phone_number)
		if Consumer.objects.filter(user=user).count():
			return True
		return False
	else:
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

def verify_password(user, password):
	verified_user = authenticate(username=user.username, password=password)
	if verified_user is not None:
		return True
	else:
		return False

@api_view(['POST'])
def create_vendor_agent(request):
	"""
	Creating Vendor Agent for vendor
	"""
	try:
		vendor_id = request.data['vendor_id']
		phone_number = request.data['phone_number']
		name = request.data.get('name')
		password = request.data['password']	
	except Exception, e:
		content = {'error':'Incomplete params', 'description':'vendor_id, phone_number, name, password'}	
		return Response(content, status = status.HTTP_400_BAD_REQUEST)
	
	try:
		vendor = Vendor.objects.get(id = vendor_id)
	except:
		content = {'error':'Vendor with id doesnt exists'}
		return Response(content, status = status.HTTP_400_BAD_REQUEST)

	if is_userexists(phone_number) is True:
		content = {'error':'User already exists with same phone number'}	
		return Response(content, status = status.HTTP_400_BAD_REQUEST)		
		
	new_user = User.objects.create(username = phone_number, password = password)
	new_vendor_agent = VendorAgent.objects.create(user = new_user, vendor = vendor)
	if name is not None:
		new_user.first_name = name
		new_user.save()

	token = create_token(new_user, constants.VENDOR)
	content = {'auth_token':token.key}
	return Response(content, status = status.HTTP_201_CREATED)

@api_view(['POST'])
def request_vendor_account(request):
	"""
	Registration for Vendor
	"""
	try:
		store = request.data['store_name']
		phone_number = request.data['phone_number']
		email = request.data['email']

		flat_number = request.data['flat_number']
		building = request.data['building']
		street = request.data['street']
		area_code = request.data['area_code']
	except:
		content = {'error':'Incomplete params', 'description':'phone_number, name'}	
		return Response(content, status = status.HTTP_400_BAD_REQUEST)

	new_requested_vendor = RequestedVendor.objects.create(store_name = store, email = email, phone_number = phone_number)
	new_address = Address.objects.create(flat_number=flat_number, building=building, street=street, area_code= area_code)
	new_requested_vendor.address = new_address
	new_requested_vendor.save()

	content = {'description':'Request submitted successfully'}
	return Response(content, status = status.HTTP_201_CREATED)

@api_view(['POST'])
def dg_signin(request):
	phone_number = request.data['phone_number']
	password = request.data['password']
	if is_dgexists(phone_number) is True:
		user = User.objects.get(username = phone_number)
		dg = DeliveryGuy.objects.get(user = user)
		
		if verify_password(user, password):
			token = Token.objects.get(user=dg.user)
			content = {'auth_token': token.key}
			return Response(content, status = status.HTTP_201_CREATED)   
		else:
			content = {'error': 'Invalid Credentials'}
			return Response(content, status = status.HTTP_201_CREATED)   
	else:
		content = {'error':'user with phone number doesnt exists'}	
		return Response(content, status = status.HTTP_404_NOT_FOUND)

def create_consumer(phone_number, password, name, email):
	user = User.objects.create(username=phone_number, password=password)
	token = create_token(user, constants.CONSUMER)
	
	if name is not None:
		user.name = name
		user.save()
	if email is not None:
		user.email = email
		user.save()
	return user

@api_view(['POST'])
def register_consumer(request):
	"""
	Registration for Consumer
	"""
	if request.user is not None:
		role = user_role(request.user)
		if role == constants.VENDOR:
			# CREATING CONSUMER BY VENDOR
			try:
				phone_number = request.data['phone_number']
				name = request.data['name']

			except Exception, e:
				content = {
					'error':'Incomplete params',
					'description':'phone_number, name'
				}	
				return Response(content, status = status.HTTP_400_BAD_REQUEST)

			if is_consumerexists(phone_number) is True:
				user = User.objects.get(username = phone_number)
				consumer = Consumer.objects.get(user = user)
			else:
				consumer = create_consumer(phone_number, '', name, '')

			## ADDING ADDRESS			
			try:
				flat_number = request.data['flat_number']
				building = request.data['building']
				street = request.data['street']
				area_code = request.data['area_code']
			
				new_address = Address.objects.create(flat_number=flat_number, building=building, street=street, area_code= area_code)
				consumer.address = new_address
				consumer.save()

			except Exception, e:
				pass

			# SETTING ASSOCIATED VENDOR
			associated_vendor = Vendor.objects.get(user = request.user)
			consumer.associated_vendor.add(associated_vendor)
			consumer.save()
			
			# SUCCESS RESPONSE FOR CONSUMER CREATION BY VENDOR
			content = {
				'consumer_id':consumer.id
			}	
			return Response(content, status = status.HTTP_201_CREATED)

		else:
			content = {
				'error':'No permissions to create consumer'
			}	
			return Response(content, status = status.HTTP_400_BAD_REQUEST)

	else:
		## CONSUMER DIRECT REGISTRATION
		try:
			phone_number = request.data['phone_number']
			password = request.data['password']
			name = request.data.get('name')
			email = request.data.get('email')
		
		except Exception, e:
			content = {
				'error':'Incomplete params',
				'description':'phone_number, password, email'
			}	
			return Response(content, status = status.HTTP_400_BAD_REQUEST)

		consumer = create_consumer(phone_number, password, name, email)
		token = Token.objects.get(user = consumer.user)
		content = {'auth_token': token.key}
		return Response(content, status = status.HTTP_201_CREATED)    			