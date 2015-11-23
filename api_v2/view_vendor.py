from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route

from yourguy.models import Vendor, Address, VendorAgent, Area, User, Industry
from api.serializers import VendorSerializer
from api.views import user_role, IsAuthenticatedOrWriteOnly, send_email, is_userexists, send_sms, create_token

import constants

def create_address(full_address, pin_code, landmark):
    new_address = Address.objects.create(full_address = full_address, pin_code = pin_code)
    if landmark is not None:
        new_address.landmark = landmark
        new_address.save()
    return new_address


class VendorViewSet(viewsets.ModelViewSet):
    """
    Vendor viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticatedOrWriteOnly]
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

    @detail_route(methods=['post'])
    def request_vendor_account(self, request, pk = None):
        # INPUT PARAMETER CHECK ----------------------------------------------------------
        try:
            store_name = request.data['store_name']
            phone_number = request.data['phone_number']
            email = request.data['email']

            full_address = request.data['full_address']
            pin_code = request.data['pin_code']
            landmark = request.data.get('landmark')
        except:
            content = {'error':'Incomplete parameters', 'description':'store_name, phone_number, email, full_address, pin_code, landmark[optional]'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # ----------------------------------------------------------------------------------
        
        # CHECK IF THE VENDOR HAS ALREADY REQUESTED FOR AN ACCOUNT ------------------------
        existing_vendors = Vendor.objects.filter(phone_number=phone_number)
        if len(existing_vendors) > 0:
            content = {'error':'Already exists', 'description':'Vendor with similar details already exists'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        # ----------------------------------------------------------------------------------

        # CREATING NEW VENDOR --------------------------------------------------------------
        new_vendor = Vendor.objects.create(store_name = store_name, email = email, phone_number = phone_number)
        new_address = create_address(full_address, pin_code, landmark)
        new_vendor.addresses.add(new_address)
        new_vendor.save()
        # ----------------------------------------------------------------------------------
        
        # SEND EMAIL TO SALES ---------------------------------------------------------------
        approval_link = 'http://app.yourguy.in/#/home/vendor/{}'.format(new_address.id)
        subject = 'YourGuy: New Vendor Account Request'
        body = constants.VENDOR_ACCOUNT_REQUESTED_MESSAGE_SALES.format(store_name, phone_number, email, full_address, pin_code, landmark, approval_link)
        send_email(constants.SALES_EMAIL, subject, body)
        # ----------------------------------------------------------------------------------

        content = {'status':'Thank you! We have received your request. Our sales team will contact you soon.'}
        return Response(content, status = status.HTTP_201_CREATED)

    @detail_route(methods=['post'])
    def add_address(self, request, pk):
        try:
            full_address = request.data['full_address']
            pin_code = request.data['pin_code']
            landmark = request.data.get('landmark')
        except:
            content = {'error':'Incomplete parameters', 'description':'full_address, pin_code, landmark'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        role = user_role(request.user)
        if role == constants.VENDOR:
            vendor_agent = get_object_or_404(VendorAgent, user = request.user)
            vendor = vendor_agent.vendor
            
            new_address = create_address(full_address, pin_code, landmark)
            vendor.addresses.add(new_address)

            content = {'description': 'Address added successfully'}
            return Response(content, status = status.HTTP_200_OK)
        else:
            content = {'description': 'You dont have permissions to add address.'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
    
    @detail_route(methods=['post'])
    def remove_address(self, request, pk):
        try:
            address_id = request.data['address_id']
        except:
            content = {'error':'Incomplete params', 'description':'address_id'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        
        role = user_role(request.user)
        if role == constants.VENDOR:
            address = get_object_or_404(Address, pk = address_id)
            
            vendor_agent = get_object_or_404(VendorAgent, user = request.user)
            vendor = vendor_agent.vendor
            vendor.addresses.remove(address)
            
            content = {'description': 'Address removed successfully'}
            return Response(content, status = status.HTTP_200_OK)
        else:
            content = {'description': 'You dont have permissions to add address.'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
            