from yourguy.models import Vendor, Address

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets
from rest_framework.response import Response

from api.serializers import VendorSerializer
from api.views import user_role

import constants

class VendorViewSet(viewsets.ModelViewSet):
    """
    Vendor viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
    	role = user_role(request.user)
    	if role == constants.SALES:
    		all_vendors = Vendor.objects.all()
    		serializer = VendorSerializer(all_vendors, many=True)
    		return Response(serializer.data, status=status.HTTP_201_CREATED)
    	else:
    		content = {'error':'You dont have permissions to view all vendors'}
    		return Response(content, status = status.HTTP_400_BAD_REQUEST)

    def create(self, request):
    	role = user_role(request.user)
    	if role == constants.SALES:
    		# serializer = VendorSerializer(data=request.data)
      #   	if serializer.is_valid():
      #   		# TODO: CREATE OBJECT
      #       	return Response({'vendor_id': return vendor id}, status=status.HTTP_201_CREATED)
      #   	else:
      #       	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    		
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

    		new_address = Address.objects.create(flat_number=flat_number, building=building, street=street, area_code= area_code)
    		vendor = Vendor.objects.create(store_name = store, address = new_address, email = email, alternate_phone_number = phone_number)

    		content = {'vendor_id':vendor.id}
    		return Response(content, status = status.HTTP_201_CREATED)

    		#TODO: CREATE ADMIN VENDOR AGENT
    	else:
    		content = {'error':'No permissions to create vendor'}   
    		return Response(content, status = status.HTTP_400_BAD_REQUEST)