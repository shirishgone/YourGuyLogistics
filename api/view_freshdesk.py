from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework import status, authentication
from rest_framework.response import Response

from api.views import user_role
from yourguy.models import VendorAgent

import requests
import constants

import urllib2
from base64 import encodestring
import json

def auth_headers():
	#TODO:
	#freshdesk_key = os.environ['freshdesk_key']
	freshdesk_test_key = 'wxMmvYfVzHCaYaXi1yln'
	freshdesk_production_key = 'iUVZ8uJ1AywpVsQKL'

	base64string = encodestring(freshdesk_production_key).replace('\n', '')
	headers = {'Authorization': 'Basic %s' % base64string , 'Content-Type':'application/json;charset=UTF-8' }
	return headers

@api_view(['GET'])
def all_tickets(request):	
	role = user_role(request.user)
	if role == constants.VENDOR:
		vendor_agent = get_object_or_404(VendorAgent, user = request.user)
		vendor = vendor_agent.vendor
		url = '{}/helpdesk/tickets.json?email={}&filter_name=all_tickets'.format(constants.FRESHDESK_BASEURL, vendor.email)
	elif role == constants.OPERATIONS:
		url = '{}/helpdesk/tickets/filter/all_tickets?format=json'.format(constants.FRESHDESK_BASEURL)
	else:
		content = {'error':'You dont have permissions'}
		return Response(content, status = status.HTTP_400_BAD_REQUEST)
	
	try:
		r = requests.get(url, headers = auth_headers())
		return Response(r.json(), status = status.HTTP_200_OK)

	except Exception, e:
		content = {'error':'Something went wrong'}
		return Response(content, status = status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_open_ticket_count(request):
    role = user_role(request.user)
    if role == constants.VENDOR:
        vendor_agent = get_object_or_404(VendorAgent, user=request.user)
        vendor = vendor_agent.vendor
        url = '{}/helpdesk/tickets.json?email={}&filter_name=new_and_my_open'.format(constants.FRESHDESK_BASEURL,
                                                                                 vendor.email)
    elif role == constants.OPERATIONS:
        url = '{}/helpdesk/tickets/filter/new_and_my_open?format=json'.format(constants.FRESHDESK_BASEURL)
    else:
        return response_access_denied()
    try:
        r = requests.get(url, headers=auth_headers())
        content = r.json()
        response = {'count':len(content)}
        return Response(response, status = status.HTTP_200_OK)
    except Exception, e:
		content = {'error':'Something went wrong'}
		return Response(content, status = status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def groups(request):	
	url = '{}/groups.json'.format(constants.FRESHDESK_BASEURL)
	try:
		r = requests.get(url, headers = auth_headers())
		return Response(r.json(), status = status.HTTP_200_OK)
	
	except Exception, e:
		content = {'error':'Something went wrong'}
		return Response(content, status = status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_ticket(request):
	url = '{}/helpdesk/tickets.json'.format(constants.FRESHDESK_BASEURL)	
	try:
		r = requests.post(url, data = json.dumps(request.data) , headers = auth_headers())
		return Response(r.json(), status = status.HTTP_200_OK)
	except Exception, e:
		content = {'error':'Something went wrong'}
		return Response(content, status = status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_ticket(request):
	ticket_id = request.QUERY_PARAMS.get('ticket_id', None)

	url = '{}/helpdesk/tickets/{}.json'.format(constants.FRESHDESK_BASEURL, ticket_id)
	try:
		r = requests.get(url, headers = auth_headers())
		return Response(r.json(), status = status.HTTP_200_OK)
	except Exception, e:
		content = {'error':'Something went wrong'}
		return Response(content, status = status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_note(request):
	ticket_id = request.data['id']
	note = request.data['note']
	url = '{}/helpdesk/tickets/{}/conversations/note.json'.format(constants.FRESHDESK_BASEURL, ticket_id)
	
	try:
		r = requests.post(url, data = json.dumps(note) , headers = auth_headers())
		return Response(r.json(), status = status.HTTP_200_OK)
	except Exception, e:
		content = {'error':'Something went wrong'}
		return Response(content, status = status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def resolve(request):
	ticket_id = request.data['id']
	note = request.data['note']
	resolve = request.data['resolve']

	note_url = '{}/helpdesk/tickets/{}/conversations/note.json'.format(constants.FRESHDESK_BASEURL, ticket_id)
	resolve_url = '{}/helpdesk/tickets/{}.json'.format(constants.FRESHDESK_BASEURL, ticket_id)
	try:
		note_request = requests.post(note_url, data = json.dumps(note) , headers = auth_headers())
		resolve_request = requests.put(resolve_url, data = json.dumps(resolve) , headers = auth_headers())
		
		content = {'meta':'Successfully resolved the issue.'}
		return Response(status = status.HTTP_200_OK)
	except Exception, e:
		content = {'error':'Something went wrong'}
		return Response(content, status = status.HTTP_400_BAD_REQUEST)
