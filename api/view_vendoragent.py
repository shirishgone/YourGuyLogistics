from django.contrib.auth.models import User
from yourguy.models import VendorAgent, Vendor

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets
from rest_framework.response import Response

from api.serializers import VendorAgentSerializer
from api.views import user_role, is_userexists, create_token
import constants

class VendorAgentViewSet(viewsets.ModelViewSet):
    """
    VendorAgent viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = VendorAgent.objects.all()
    serializer_class = VendorAgentSerializer
   	
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
    			content = {'error':'User already exists with same phone number'}	
    			return Response(content, status = status.HTTP_400_BAD_REQUEST)		
    		else:
    			pass
    		
    		new_user = User.objects.create(username = phone_number, password = password)
    		new_vendor_agent = VendorAgent.objects.create(user = new_user, vendor = vendor)
    		if name is not None:
    			new_user.first_name = name
    			new_user.save()
    		else:
    			pass
    		
    		token = create_token(new_user, constants.VENDOR)
    		content = {'auth_token':token.key}
    		return Response(content, status = status.HTTP_201_CREATED)

    	else:
    		content = {'error':'No permissions to create vendor agent'}   
    		return Response(content, status = status.HTTP_400_BAD_REQUEST)
