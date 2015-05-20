from yourguy.models import RequestedVendor

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets

from api.serializers import RequestedVendorSerializer

class RequestedVendorViewSet(viewsets.ModelViewSet):
    """
    Requested Vendor viewset that provides the standard actions 
    """
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    queryset = RequestedVendor.objects.none()
    serializer_class = RequestedVendorSerializer
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

    	new_address = Address.objects.create(flat_number=flat_number, building=building, street=street, area_code= area_code)
    	vendor = RequestedVendor.objects.create(store_name = store, address = new_address, email = email, phone_number = phone_number)

    	content = {'status':'Thank you! We have received your request. Our sales team will contact you soon.'}
    	return Response(content, status = status.HTTP_201_CREATED)
