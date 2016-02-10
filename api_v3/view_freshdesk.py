import json
from base64 import encode

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
    freshdesk_test_key = constants.FRESHDESK_TEST_KEY
    freshdesk_production_key = constants.FRESHDESK_PRODUCTION_KEY

    base64string = encode(freshdesk_production_key).replace('\n', '')
    headers = {
        'Authorization': 'Basic %s' % base64string, 'Content-Type': 'application/json;charset=UTF-8'
    }
    return headers


@api_view(['GET'])
def all_tickets(request):
    role = user_role(request.user)
    if role == constants.VENDOR:
        vendor_agent = get_object_or_404(VendorAgent, user=request.user)
        vendor = vendor_agent.vendor
        url = '{}/helpdesk/tickets.json?email={}&filter_name=all_tickets'.format(constants.FRESHDESK_BASEURL,
                                                                                 vendor.email)
    elif role == constants.OPERATIONS:
        url = '{}/helpdesk/tickets/filter/all_tickets?format=json'.format(constants.FRESHDESK_BASEURL)
    else:
        return response_access_denied()
    try:
        r = requests.get(url, headers=auth_headers())
        content = r.json()
        return response_with_payload(content, None)
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
    url = '{}/helpdesk/tickets.json'.format(constants.FRESHDESK_BASEURL)
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
