# from django.shortcuts import render
from django.core.mail import send_mail
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
from rest_framework import permissions

from yourguy.models import Vendor, Consumer, DeliveryGuy, VendorAgent, Address
from api.serializers import UserSerializer, OrderSerializer, ConsumerSerializer

from datetime import datetime, timedelta, time
import random
import string

import constants
import base64
import requests

from boto.s3.connection import S3Connection
import os

def paginate(list, page):    
    paginator = Paginator(list, constants.PAGINATION_PAGE_SIZE) # Show 25 contacts per page
    try:
        result = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        result = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        result = paginator.page(paginator.num_pages)

    return result.object_list
