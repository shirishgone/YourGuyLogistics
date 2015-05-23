from django.contrib.auth.models import User, Group
from yourguy.models import VendorAgent, Vendor

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets
from rest_framework.response import Response

from api.serializers import VendorAgentSerializer
from api.views import user_role, is_userexists, create_token, is_vendoragentexists
import constants

class VendorAgentViewSet(viewsets.ModelViewSet):
    """
    VendorAgent viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = VendorAgent.objects.all()
    serializer_class = VendorAgentSerializer
	
    def list(self, request):
    	role = user_role(request.user)
    	if role == constants.VENDOR:
    		vendor_agent = VendorAgent.objects.get(user = request.user)
    		vendor_agents_of_vendor = VendorAgent.objects.filter(vendor = vendor_agent.vendor)
    		serializer = VendorAgentSerializer(vendor_agents_of_vendor, many=True)
    		return Response(serializer.data, status=status.HTTP_201_CREATED)
    	else:
    		content = {'error':'You dont have permissions to view all vendors'}
    		return Response(content, status = status.HTTP_400_BAD_REQUEST)

    def create(self, request):
    	role = user_role(request.user)
    	if (role == constants.VENDOR) or (role == constants.SALES):
    		try:
    			vendor_id = request.data['vendor_id']
    			phone_number = request.data['phone_number']
    			name = request.data.get('name')
    			password = request.data['password']	
    		except Exception, e:
    			content = {'error':'Incomplete params', 'description':'vendor_id, phone_number, name, password'}	
    			return Response(content, status = status.HTTP_400_BAD_REQUEST)
    		
    		try:
    			vendor = Vendor.objects.get(id = vendor_id)
    		except:
    			content = {'error':'Vendor with id doesnt exists'}
    			return Response(content, status = status.HTTP_400_BAD_REQUEST)
            
    		if is_userexists(phone_number) is True:
    			user = User.objects.get(username = phone_number)
    			if is_vendoragentexists(user) is True:
    				content = {'error':'Vendor Agent with same details exists'}
    				return Response(content, status = status.HTTP_400_BAD_REQUEST)
    			else:
    				vendor_agent = VendorAgent.objects.create(user = user)
    		else:
    			user = User.objects.create(username=phone_number, password=password)
    			new_vendor_agent = VendorAgent.objects.create(user = user, vendor = vendor)

    		# ADDING USER TO THE GROUP
    		# group = Group.objects.get(name=constants.VENDOR) 
    		# group.user_set.add(user)

    		token = create_token(user, constants.VENDOR)
    		content = {'auth_token':token.key}
    		return Response(content, status = status.HTTP_201_CREATED)

    	else:
    		content = {'error':'No permissions to create vendor agent'}   
    		return Response(content, status = status.HTTP_400_BAD_REQUEST)
