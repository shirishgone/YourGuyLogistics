from yourguy.models import Vendor, Address, VendorAgent, Area

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route

from api.serializers import VendorSerializer
from api.views import user_role

import constants

class VendorViewSet(viewsets.ModelViewSet):
    """
    Vendor viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

    def list(self, request):
    	role = user_role(request.user)
    	if role == constants.SALES:
    		all_vendors = Vendor.objects.all()
    		serializer = VendorSerializer(all_vendors, many=True)
    		return Response(serializer.data, status=status.HTTP_201_CREATED)
    	elif role == constants.VENDOR:
    		vendor_agent = VendorAgent.objects.get(user = request.user)
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

    	area = Area.objects.get(area_code = area_code)
    	new_address = Address.objects.create(flat_number=flat_number, building=building, street=street, area = area)
    	vendor = Vendor.objects.create(store_name = store, address = new_address, email = email, phone_number = phone_number)

    	content = {'status':'Thank you! We have received your request. Our sales team will contact you soon.'}
    	return Response(content, status = status.HTTP_201_CREATED)

    @list_route()
    def requestedvendors():
        vendors = Vendor.objects.filter(verified=False)
        serializer = VendorSerializer(vendors, many=True)
        return Response(serializer.data)