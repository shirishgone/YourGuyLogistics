import json
from base64 import encodestring

import requests
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view

from api_v3 import constants
from api_v3.utils import user_role
from yourguy.models import VendorAgent
from api_v3.utils import response_access_denied, response_with_payload, response_error_with_message, response_success_with_message, response_invalid_pagenumber, response_incomplete_parameters

def auth_headers():
    # TODO:
    # freshdesk_key = os.environ['freshdesk_key']
    # Can save the keys in Heroku Shared preferences and fetch it dynamically
    base64string = encodestring(constants.FRESHDESK_KEY).replace('\n', '')
    headers = {
        'Authorization': 'Basic %s' % base64string, 'Content-Type': 'application/json;charset=UTF-8'
    }
    return headers

@api_view(['GET'])
def get_open_ticket_count(request):
    try:
        role = user_role(request.user)
        if role == constants.VENDOR:
            vendor_agent = get_object_or_404(VendorAgent, user=request.user)
            vendor = vendor_agent.vendor
            count_url = '{}helpdesk/tickets/summary.json?view_name=open&email={}'.format(constants.FRESHDESK_BASEURL,vendor.email)
        elif role == constants.OPERATIONS:
            count_url = '{}helpdesk/tickets/summary.json?view_name=open'.format(constants.FRESHDESK_BASEURL)    
        else:
            return response_access_denied()

        count_request = requests.get(count_url, headers=auth_headers())
        count_response = count_request.json()
        count = count_response['view_count']
        response = {'count':count}
        return response_with_payload(response, None)
    except Exception as e:
        error_message = 'Something went wrong'
        return response_error_with_message(error_message)

@api_view(['GET'])
def all_tickets(request):
    role = user_role(request.user)
    page = request.QUERY_PARAMS.get('page', 1)
    page = int(page)
    if role == constants.VENDOR:
        vendor_agent = get_object_or_404(VendorAgent, user=request.user)
        vendor = vendor_agent.vendor
        url = '{}api/v2/tickets?updated_since=2015-01-19T02:00:00Z&email={}&per_page={}&page={}'.format(constants.FRESHDESK_BASEURL, vendor.email, constants.FRESHDESK_PAGE_COUNT, page)
    elif role == constants.OPERATIONS:
        url = '{}api/v2/tickets?updated_since=2015-01-19T02:00:00Z&per_page={}&page={}'.format(constants.FRESHDESK_BASEURL, constants.FRESHDESK_PAGE_COUNT, page)
    else:
        return response_access_denied()
    
    try: 
        if role == constants.VENDOR:
            vendor_agent = get_object_or_404(VendorAgent, user=request.user)
            vendor = vendor_agent.vendor
            count_url = '{}helpdesk/tickets/summary.json?view_name=all&email={}'.format(constants.FRESHDESK_BASEURL,vendor.email)
        elif role == constants.OPERATIONS:
            count_url = '{}helpdesk/tickets/summary.json?view_name=all'.format(constants.FRESHDESK_BASEURL)
        else:
            return response_access_denied()
        
        count_request = requests.get(count_url, headers=auth_headers())
        count_response = count_request.json()
        count = count_response['view_count']
        total_pages = int(count / constants.FRESHDESK_PAGE_COUNT) + 1

        r = requests.get(url, headers=auth_headers())
        content = r.json()
        response_content = {
            "data": content,
            "total_pages": total_pages,
            "total_tickets": count
        }
        return response_with_payload(response_content, None)
    except Exception as e:
        error_message = 'Something went wrong'
        return response_error_with_message(error_message)

@api_view(['GET'])
def groups(request):
    url = '{}/groups.json'.format(constants.FRESHDESK_BASEURL)
    try:
        r = requests.get(url, headers=auth_headers())
        content = r.json()
        return response_with_payload(content, None)

    except Exception as e:
        error_message = 'Something went wrong'
        return response_error_with_message(error_message)


@api_view(['POST'])
def create_ticket(request):
    url = '{}api/v2/tickets'.format(constants.FRESHDESK_BASEURL)
    try:
        r = requests.post(url, data=json.dumps(request.data), headers=auth_headers())
        content = r.json()
        return response_with_payload(content, None)
    except Exception as e:
        error_message = 'Something went wrong'
        return response_error_with_message(error_message)

@api_view(['GET'])
def get_ticket(request):
    ticket_id = request.QUERY_PARAMS.get('ticket_id', None)
    url = '{}/helpdesk/tickets/{}.json'.format(constants.FRESHDESK_BASEURL, ticket_id)
    try:
        r = requests.get(url, headers=auth_headers())
        content = r.json()
        return response_with_payload(content, None)
    except Exception as e:
        error_message = 'Something went wrong'
        return response_error_with_message(error_message)

@api_view(['POST'])
def add_note(request):
    ticket_id = request.data['id']
    note = request.data['note']
    url = '{}/helpdesk/tickets/{}/conversations/note.json'.format(constants.FRESHDESK_BASEURL, ticket_id)

    try:
        r = requests.post(url, data=json.dumps(note), headers=auth_headers())
        content = r.json()
        return response_with_payload(content, None)
    except Exception as e:
        error_message = 'Something went wrong'
        return response_error_with_message(error_message)

@api_view(['PUT'])
def resolve(request):
    ticket_id = request.data['id']
    note = request.data['note']
    resolve = request.data['resolve']

    note_url = '{}/helpdesk/tickets/{}/conversations/note.json'.format(constants.FRESHDESK_BASEURL, ticket_id)
    resolve_url = '{}/helpdesk/tickets/{}.json'.format(constants.FRESHDESK_BASEURL, ticket_id)
    try:
        note_request = requests.post(note_url, data=json.dumps(note), headers=auth_headers())
        resolve_request = requests.put(resolve_url, data=json.dumps(resolve), headers=auth_headers())

        success_message = 'Successfully resolved the ticket'
        return response_success_with_message(success_message)
    except Exception as e:
        error_message = 'Something went wrong'
        return response_error_with_message(error_message)
