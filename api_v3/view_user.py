from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from rest_framework.authtoken.models import Token

from api_v3 import constants
from api_v3.utils import is_userexists, create_token, assign_usergroup_with_name, assign_usergroup, user_role
from yourguy.models import User, Vendor, VendorAgent, Consumer, DeliveryGuy, Employee

from api_v3.utils import response_access_denied, response_with_payload, response_error_with_message, response_success_with_message, response_invalid_pagenumber, response_incomplete_parameters


def dg_details_dict(delivery_guy):
    dg_detail_dict = {
        'auth_token': None,
        'id': delivery_guy.id,
        'username': delivery_guy.user.username,
        'shift_start_datetime': delivery_guy.shift_start_datetime,
        'shift_end_datetime': delivery_guy.shift_end_datetime,
        'is_teamlead': delivery_guy.is_teamlead,
        'role': None
    }
    return dg_detail_dict


def vendor_details_dict(vendor_agent):
    vendor_detail_dict = {
        'auth_token': None,
        'vendor_agent_username': vendor_agent.user.username,
        'vendor_agent_name': vendor_agent.user.first_name,
        'vendor_store_name': vendor_agent.vendor.store_name,
        'role': None
    }
    return vendor_detail_dict


def emp_details_dict(emp):
    emp_detail_dict = {
        'auth_token': None,
        'employee_name': emp.user.first_name,
        'role': None
    }
    return emp_detail_dict


# Login api is being developed as a wrapper around the djoser login api
@api_view(['POST'])
def login(request):
    try:
        username = request.data['username']
        password = request.data['password']
    except APIException:
        params = ['username', 'password']
        return response_incomplete_parameters(params)

    try:
        user = authenticate(username=username, password=password)
        role = user_role(user)
    except Exception as e:
        error_message = 'No such user found or No such token found for the role'
        return response_error_with_message(error_message)

    if role == constants.DELIVERY_GUY:
        dg = get_object_or_404(DeliveryGuy, user=user)
        if dg.is_active is True:
            try:
                auth_login(request, user)
                user_details = dg_details_dict(dg)
                token = Token.objects.get(user=user)
                if token is not None:
                    auth_token = token.key
                    user_details['auth_token'] = auth_token
                user_details['role'] = role
                content = user_details
                return response_with_payload(content, None)
            except Exception as e:
                error_message = 'Something went wrong'
                return response_error_with_message(error_message)
        else:
            error_message = 'This DG is deactive'
            return response_error_with_message(error_message)
    elif role == constants.VENDOR:
        vendor_agent = get_object_or_404(VendorAgent, user=user)
        try:
            auth_login(request, user)
            vendor_details = vendor_details_dict(vendor_agent)
            token = Token.objects.get(user=user)
            if token is not None:
                auth_token = token.key
                vendor_details['auth_token'] = auth_token
            vendor_details['role'] = role
            content = vendor_details
            return response_with_payload(content, None)
        except Exception as e:
            error_message = 'Something went wrong'
            return response_error_with_message(error_message)
    else:
        emp = get_object_or_404(Employee, user=user)
        try:
            auth_login(request, user)
            emp_details = emp_details_dict(emp)
            token = Token.objects.get(user=user)
            if token is not None:
                auth_token = token.key
                emp_details['auth_token'] = auth_token
            emp_details['role'] = emp.department
            content = emp_details
            return response_with_payload(content, None)
        except Exception as e:
            error_message = 'Something went wrong'
            return response_error_with_message(error_message)

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
        params = ['role', 'phone_number', 'password', 'name', 'email(optional)', 'vendor_id(optional)']
        return response_incomplete_parameters(params)

    # CHECK IF USER EXISTS  -----------------------------------
    if is_userexists(phone_number):
        error_message = 'User with same phone number already exists'
        return response_error_with_message(error_message)
    # -----------------------------------------------------------

    # VENDOR AGENT CREATION NEEDS VENDOR_ID ----------------------
    if role == constants.VENDOR:
        if vendor_id is None:
            params = ['vendor_id']
            return response_incomplete_parameters(params)
        try:
            vendor = Vendor.objects.get(id=vendor_id)
        except APIException:
            error_message = 'Vendor with given id doesnt exists'
            return response_error_with_message(error_message)
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
    elif role == constants.OPERATIONS_MANAGER:
        token = create_token(user, constants.OPERATIONS_MANAGER)
        employee = Employee.objects.create(user=user)
        employee.department = constants.OPERATIONS_MANAGER
        assign_usergroup(user)
    elif role == constants.SALES:
        token = create_token(user, constants.SALES)
        employee = Employee.objects.create(user=user)
        employee.department = constants.SALES
        assign_usergroup(user)
    elif role == constants.HR:
        token = create_token(user, constants.HR)
        employee = Employee.objects.create(user=user)
        employee.department = constants.HR
        assign_usergroup(user)
    elif role == constants.ACCOUNTS:
        token = create_token(user, constants.ACCOUNTS)
        employee = Employee.objects.create(user=user)
        employee.department = constants.ACCOUNTS
        assign_usergroup(user)
    elif role == constants.CALLER:
        token = create_token(user, constants.CALLER)
        employee = Employee.objects.create(user=user)
        employee.department = constants.CALLER
        assign_usergroup(user)
    else:
        token = None
    
    employee.save()
    
    if token is not None:
        content = {'auth_token': token.key}
    else:
        content = {'auth_token': None,
                   'user created for group: ': role}

    return response_with_payload(content, None)


@api_view(['GET'])
def profile(request):
    role = user_role(request.user)
    if role == constants.VENDOR:
        vendor_agent = VendorAgent.objects.get(user=request.user)
        name = vendor_agent.vendor.store_name
    elif role == constants.OPERATIONS or role == constants.OPERATIONS_MANAGER or role == constants.SALES or role == constants.HR or role == constants.ACCOUNTS or role == constants.CALLER:
        employee = Employee.objects.get(user = request.user)
        name = employee.user.first_name
    else:
        return response_access_denied()

    result = {
    'name':name,
    'role':role
    }
    return response_with_payload(result, None)


# DO NOT DELETE
# Reset password implementation will be implemented later on


# @api_view(['POST'])
# def reset_password_link(request):
#     try:
#         phone_number = request.data['phone_number']
#     except APIException:
#         content = {
#             'error': 'Incomplete params',
#             'description': 'MANDATORY: phone_number'
#         }
#         return Response(content, status=status.HTTP_400_BAD_REQUEST)
#
#     user = User.objects.get(username=phone_number)
#     if is_userexists(user):
#         try:
#             approval_link = 'http://app.yourguy.in/resetpassword'
#             to_mail_ids = user.email
#             subject = 'YourGuy: Password Reset'
#             body = 'Please use the below link to reset your password \n' + approval_link
#
#             send_email(to_mail_ids, subject, body)
#             content = {
#                 'description': 'Password reset link has been mailed'
#             }
#             return Response(content, status=status.HTTP_200_OK)
#         except Exception as e:
#             message = 'Failed to send email for password reset'
#             log_exception(e, message)
#             content = {
#                 'description': 'Failed to send the reset password email'
#             }
#             return Response(content, status=status.HTTP_400_BAD_REQUEST)
#     else:
#         content = {
#             'description': 'No such user exists.'
#         }
#         return Response(content, status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(['PUT'])
# def reset_password(request):
#     try:
#         phone_number = request.data['phone_number']
#         old_password = request.data['old_password']
#         new_password = request.data['new_password']
#     except APIException:
#         content = {
#             'error': 'Incomplete params',
#             'description': 'MANDATORY: phone_number, old_password, new_password'
#         }
#         return Response(content, status=status.HTTP_400_BAD_REQUEST)
#
#     user = User.objects.get(username=phone_number)
#
#     if old_password != new_password and new_password is not None:
#         user.set_password(new_password)
#         user.save()
#         content = {
#             'description': 'Password changed successfully'
#         }
#         return Response(content, status=status.HTTP_201_CREATED)
#     else:
#         content = {
#             'description': 'Please try a different password.'
#         }
#         return Response(content, status=status.HTTP_400_BAD_REQUEST)
