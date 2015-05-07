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
