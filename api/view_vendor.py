from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route

from yourguy.models import Vendor, Address, VendorAgent, Area, User, VendorAgent
from api.serializers import VendorSerializer
from api.views import user_role, IsAuthenticatedOrWriteOnly, send_email, is_userexists, send_sms, create_token

import constants

class VendorViewSet(viewsets.ModelViewSet):
    """
    Vendor viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticatedOrWriteOnly]
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

    def list(self, request):
    	role = user_role(request.user)
    	if (role == constants.SALES) or (role == constants.OPERATIONS):
    		all_vendors = Vendor.objects.filter(verified=True)
    		serializer = VendorSerializer(all_vendors, many=True)
    		return Response(serializer.data, status=status.HTTP_201_CREATED)
    	elif role == constants.VENDOR:
    		vendor_agent = get_object_or_404(VendorAgent, user = request.user)
    		serializer = VendorSerializer(vendor_agent.vendor)
    		return Response(serializer.data, status=status.HTTP_201_CREATED)
    	else:
    		content = {'error':'You dont have permissions to view all vendors'}
    		return Response(content, status = status.HTTP_400_BAD_REQUEST)

    def create(self, request):
    	try:
    		store = request.data['store_name']
    		phone_number = request.data['phone_number']
    		email = request.data['email']

    		flat_number = request.data['flat_number']
    		building = request.data['building']
    		street = request.data['street']
    		area_code = request.data['area_code']
    	except:
    		content = {'error':'Incomplete params', 'description':'phone_number, store_name, email, flat_number, building, street, area_code'}
    		return Response(content, status = status.HTTP_400_BAD_REQUEST)


        # CHECK IF THE VENDOR HAS ALREADY REQUESTED FOR AN ACCOUNT
        existing_vendors = Vendor.objects.filter(phone_number=phone_number)
        if len(existing_vendors) > 0:
            content = {'error':'Already exists', 'description':'Vendor with similar details already exists'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)


    	area = get_object_or_404(Area, area_code = area_code)
    	new_address = Address.objects.create(flat_number=flat_number, building=building, street=street, area = area)

    	vendor = Vendor.objects.create(store_name = store, email = email, phone_number = phone_number)
        vendor.addresses.add(new_address)
        vendor.save()

        # SEND EMAIL TO SALES
        approval_link = 'http://vendor-yourguy.herokuapp.com/#/home/vendor/{}'.format(vendor.id)
        subject = 'YourGuy: New Vendor Account Request'
        body = constants.VENDOR_ACCOUNT_REQUESTED_MESSAGE_SALES.format(store, phone_number, email, flat_number, building, street, area_code, approval_link)
        send_email(constants.SALES_EMAIL, subject, body)

    	content = {'status':'Thank you! We have received your request. Our sales team will contact you soon.'}
    	return Response(content, status = status.HTTP_201_CREATED)

    @list_route()
    def requestedvendors(self, request):
        vendors = Vendor.objects.filter(verified=False)
        serializer = VendorSerializer(vendors, many=True)
        return Response(serializer.data)

    @detail_route(methods=['post'])
    def approve(self, request, pk):
        vendor = get_object_or_404(Vendor, pk = pk)
        notes = request.data.get('notes')
        is_retail = request.data.get('is_retail')
        # pricing = request.data.get('pricing')
        # pan = request.data.get('pan')

        try:
            username = vendor.phone_number
            password = vendor.store_name.replace(" ", "")
            password = password.lower()

            if is_userexists(username):
                user = get_object_or_404(User, username = username)
            else:    
                user = User.objects.create_user(username = username, password = password)
            
            token = create_token(user, constants.VENDOR)
            vendor_agent = VendorAgent.objects.create(user = user, vendor = vendor)
            
            vendor.verified = True
            vendor.notes = notes
            if is_retail is not None:
                vendor.is_retail = is_retail
            
            vendor.save()
        except Exception, e:
            content = {'error':'An error occurred creating the account. Please try again'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        # TODO: CREATE BILLING ACCOUNT
        # if pricing is None:
        #     pricing = 0.0  
        # else:
        #     pricing = float(pricing)
        
        # new_account = VendorAccount.objects.create(vendor = vendor, pricing = pricing)
        # if pan is not None:
        #     new_account.pan = pan
        #     new_account.save()

        # SEND AN EMAIL/SMS TO CUSTOMER AND SALES WITH ACCOUNT CREDENTIALS
        subject = 'YourGuy: Account created for {}'.format(vendor.store_name)
        customer_message = constants.VENDOR_ACCOUNT_APPROVED_MESSAGE.format(vendor.phone_number, password)
        customer_emails = [vendor.email]
        send_email(customer_emails, subject, customer_message)
        send_sms(vendor.phone_number, customer_message)

        sales_message = constants.VENDOR_ACCOUNT_APPROVED_MESSAGE_SALES.format(vendor.store_name)
        send_email(constants.SALES_EMAIL, subject, sales_message)

        content = {'description': 'Your account credentials has been sent via email and SMS.'}
        return Response(content, status = status.HTTP_200_OK)