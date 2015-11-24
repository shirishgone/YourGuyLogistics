from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from django.db.models.functions import Lower

from yourguy.models import Vendor, Address, VendorAgent, Area, User, Industry
from api.serializers import VendorSerializer
from api.views import user_role, IsAuthenticatedOrWriteOnly, send_email, is_userexists, send_sms, create_token

import constants

def vendor_detail_dict(vendor):
    vendor_dict = {
            'id' : vendor.id,
            'name':vendor.store_name,
            'email':vendor.email,
            'phone_number':vendor.phone_number,
            'alternate_phone_number':vendor.alternate_phone_number,
            'is_retail':vendor.is_retail,
            'website_url':vendor.website_url,
            'notes':vendor.notes,
            "addresses":[]
            }
    
    all_addresses = vendor.addresses.all()
    for address in all_addresses:
        adr_dict = {
        "id":address.id,
        "full_address":address.full_address,
        "pin_code":address.pin_code
        }   
        if address.landmark is not None:
            adr_dict['landmark'] = address.landmark
        vendor_dict['addresses'].append(adr_dict)

    return vendor_dict

def vendor_list_dict(vendor):
    vendor_dict = {
            'id' : vendor.id,
            'name':vendor.store_name,
            }
    return vendor_dict

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

    def destroy(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, pk = None):        
        vendor = get_object_or_404(Vendor, id = pk)
        role = user_role(request.user)
        can_respond = False
        
        if role == 'vendor':
            vendor_agent = get_object_or_404(VendorAgent, user = request.user)
            if vendor.id == vendor_agent.vendor.id:
                can_respond = True
            else:
                can_respond = False
        else:
            can_respond = True
            
        if can_respond:
            vendor_detail = vendor_detail_dict(vendor)
            response_content = { 
            "data": vendor_detail
            }
            return Response(response_content, status = status.HTTP_200_OK)
        else:
            content = {
            'error':'You dont have permissions to view this vendor details.'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        role = user_role(request.user)
        if (role == constants.SALES) or (role == constants.OPERATIONS):
            all_vendors = Vendor.objects.filter(verified=True).order_by(Lower('store_name'))

            all_vendors_array = []
            for vendor in all_vendors:
                vendor_dict = vendor_list_dict(vendor)
                all_vendors_array.append(vendor_dict)
            
            response_content = { 
            "data": all_vendors_array
            }
            return Response(response_content, status = status.HTTP_200_OK)
        elif role == constants.VENDOR:
            vendor_agent = get_object_or_404(VendorAgent, user = request.user)
            vendor_detail = vendor_detail_dict(vendor_agent.vendor)
            response_content = { 
            "data": vendor_detail
            }
            return Response(response_content, status = status.HTTP_200_OK)
        else:
            content = {'error':'You dont have permissions to view all vendors'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

    @list_route()
    def requestedvendors(self, request):
        role = user_role(request.user)
        if (role == constants.SALES) or (role == constants.OPERATIONS):
            all_vendors = Vendor.objects.filter(verified=False).order_by(Lower('store_name'))
            all_vendors_array = []
            for vendor in all_vendors:
                vendor_dict = vendor_list_dict(vendor)
                all_vendors_array.append(vendor_dict)
            
            response_content = { 
            "data": all_vendors_array
            }
            return Response(response_content, status = status.HTTP_200_OK)
        else:
            content = {'error':'You dont have permissions to view all vendors'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

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
        try:
            approval_link = 'http://app.yourguy.in/#/home/vendor/{}'.format(new_address.id)
            subject = 'YourGuy: New Vendor Account Request'
            body = constants.VENDOR_ACCOUNT_REQUESTED_MESSAGE_SALES.format(store_name, phone_number, email, full_address, pin_code, approval_link)
            send_email(constants.SALES_EMAIL, subject, body)
        except Exception, e:
            pass
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
            