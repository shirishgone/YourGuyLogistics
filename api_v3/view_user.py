from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from api_v3 import constants
from api_v3.utils import is_userexists, create_token, assign_usergroup_with_name, assign_usergroup
from yourguy.models import User, Vendor, VendorAgent, Consumer, DeliveryGuy, Employee


@api_view(['POST'])
def register(request):
    try:
        role = request.data['role']
        phone_number = request.data['phone_number']
        password = request.data['password']
        name = request.data['name']

        email = request.data.get('email')
        vendor_id = request.data.get('vendor_id')
    except APIException:
        content = {
            'error': 'Incomplete params',
            'description': 'MANDATORY: role, phone_number, password, name. OPTIONAL: email, vendor_id'
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    # CHECK IF USER EXISTS  -----------------------------------
    if is_userexists(phone_number):
        content = {
            'error': 'User already exists',
            'description': 'User with same phone number already exists'
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    # -----------------------------------------------------------

    # VENDOR AGENT CREATION NEEDS VENDOR_ID ----------------------
    if role == constants.VENDOR:
        if vendor_id is None:
            content = {
                'error': 'Incomplete params',
                'description': 'MANDATORY: vendor_id. For creating vendor agent pass vendor_id'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            vendor = Vendor.objects.get(id=vendor_id)
        except APIException:
            content = {
                'error': 'Vendor with given id doesnt exists'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
    # ---------------------------------------------------------------

    user = User.objects.create_user(username=phone_number, password=password, first_name=name)
    if email is not None:
        user.email = email
    user.save()

    token = None
    if role == constants.VENDOR:
        token = create_token(user, constants.VENDOR)
        vendor = get_object_or_404(Vendor, id=vendor_id)
        vendor_agent = VendorAgent.objects.create(user=user, vendor=vendor)
        assign_usergroup(user)
    elif role == constants.DELIVERY_GUY:
        token = create_token(user, constants.DELIVERY_GUY)
        delivery_guy = DeliveryGuy.objects.create(user=user)
        assign_usergroup(user)
    elif role == constants.CONSUMER:
        consumer = Consumer.objects.create(user=user)
        assign_usergroup_with_name(user, constants.CONSUMER)
    elif role == constants.OPERATIONS:
        token = create_token(user, constants.OPERATIONS)
        employee = Employee.objects.create(user=user)
        employee.department = constants.OPERATIONS
        assign_usergroup(user)
    elif role == constants.SALES:
        token = create_token(user, constants.SALES)
        employee = Employee.objects.create(user=user)
        employee.department = constants.SALES
        assign_usergroup(user)
    else:
        token = None

    if token is not None:
        content = {'auth_token': token.key}
    else:
        content = {'auth_token': None,
                   'user created for group: ': role}

    return Response(content, status=status.HTTP_201_CREATED)
