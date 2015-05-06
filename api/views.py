# from django.shortcuts import render

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token

from rest_framework import status, authentication, permissions, viewsets, serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.response import Response

from django.http import Http404
from django.db.models.base import ObjectDoesNotExist

from yourguy.models import Vendor, Address
from api.serializers import UserSerializer, OrderSerializer, AddressSerializer, ConsumerSerializer

import datetime
import random
import string

def generate_random_number(size):
    """
    :param size:
    :return:
    """

    char_set = string.ascii_uppercase + string.digits + string.ascii_lowercase
    token = ''.join(random.sample(char_set * size, size))
    return token


# @api_view(('GET',))
# def api_root(request, format = None):
#     return Response({
#         # 'signup': reverse('signup', request = request, format = format),
#         # 'signin': reverse('signin', request = request, format = format),
#         # 'forgot_password': reverse('forgot_password', request = request, format = format),
#
#         'create_address' : reverse('create_address', request = request, format = format),
#         'update_address' : reverse('update_address', request = request, format = format),
#
#         'create_order': reverse('create_order', request = request, format = format),
#         'view_orders': reverse('view_orders', request = request, format = format),
#         'update_order': reverse('update_order', request = request, format = format),
#         'cancel_order': reverse('cancel_order', request = request, format = format),
#         'assign_order': reverse('assign_order', request = request, format = format),
#         'mark_pickedup': reverse('mark_pickedup', request = request, format = format),
#         'mark_delivered': reverse('mark_delivered', request = request, format = format),
#         'update_dg_location': reverse('update_dg_location', request = request, format = format),
#         'view_all_dg_locations': reverse('view_all_dg_locations', request = request, format = format),
#         'create_customer': reverse('create_customer', request = request, format = format),
#         'view_customers': reverse('view_customers', request = request, format = format),
#         'update_customer': reverse('update_customer', request = request, format = format),
#         'delete_customer': reverse('delete_customer', request = request, format = format),
    # })


@api_view(['POST'])
def signup(request):
    VALID_USER_FIELDS = [user.name for user in get_user_model()._meta.fields]
    DEFAULTS = {
        # you can define any defaults that you would like for the user, here
    }
    serialized = UserSerializer(data = request.DATA)
    if serialized.is_valid():
        user_data = {field: data for (field, data) in request.DATA.items() if field in VALID_USER_FIELDS}
        user_data.update(DEFAULTS)
        user = get_user_model().objects.create_user(
            **user_data
        )

        token = Token.objects.get(user=user)
        content = {'user_id': user.id,
                    'token':token.key
                    }
        return Response(content, status = status.HTTP_201_CREATED)
    else:
        return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def signin(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username = username, password = password)
    if user is not None:
        if user.is_active:
            login(request, user)
            # response a success

            token = Token.objects.get(user=user)
            content = { 'user_id': user.id,
                        'token':token.key
                        }
            return Response(content, status = status.HTTP_201_CREATED)

        else:
            # Return a 'disabled account' error message
            content = {'description': 'disabled account'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
    else:
        # Return an 'invalid login' error message.
        content = {'description': 'Invalid login'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def forgot_password(request):
    username = request.POST['username']
    # TODO: Send an SMS

    return Response(content, status=status.HTTP_201_CREATED)
