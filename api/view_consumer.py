from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.db.models.functions import Lower

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from yourguy.models import Consumer, Vendor, VendorAgent, Address, Area
from api.serializers import ConsumerSerializer
from api.views import user_role
from api.views import user_role, is_userexists, is_vendorexists, is_dgexists
import constants
from api_v3.view_consumer import is_consumer_has_same_address_already, fetch_or_create_consumer, fetch_or_create_consumer_address

class ConsumerViewSet(viewsets.ModelViewSet):
    """
    Consumer viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Consumer.objects.all()
    serializer_class = ConsumerSerializer

    def destroy(self, request, pk= None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)            

    def list(self, request):
        role = user_role(request.user)
        if role == constants.VENDOR:
            vendor_agent = get_object_or_404(VendorAgent, user = request.user)
            consumers_of_vendor = Consumer.objects.filter(vendor = vendor_agent.vendor).order_by(Lower('full_name'))
            
            serializer = ConsumerSerializer(consumers_of_vendor, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif role == constants.OPERATIONS:
            all_customers = Consumer.objects.all()
            serializer = ConsumerSerializer(all_customers, many=True)
        else:
            content = {'error':'You dont have permissions to view all Consumers'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        role = user_role(request.user)
        if (role == constants.VENDOR):
            vendor_agent = VendorAgent.objects.get(user = request.user)
            try:
                phone_number = request.data['phone_number']
                name = request.data['name']
            except Exception, e:
                content = {
                        'error':'Incomplete params',
                        'description':'Mandatory Fields: phone_number, name'
                    }   
                return Response(content, status = status.HTTP_400_BAD_REQUEST)

            ## ADDING ADDRESS           
            try:
                flat_number = request.data['flat_number']
                building = request.data['building']
                street = request.data['street']
                area_code = request.data['area_code']
                area = get_object_or_404(Area, area_code= area_code)
            except:
                content = {
                        'error':'Address details missing',
                        'description':'Mandatory Fields: flat_number, building, street, area_code'
                    }   
                return Response(content, status = status.HTTP_400_BAD_REQUEST)

            consumer = fetch_or_create_consumer(phone_number, name, vendor)
            full_address = flat_number + building + street
            address = fetch_or_create_consumer_address(consumer, full_address, None, None)            
            
            serializer = ConsumerSerializer(consumer)
            content = {
            'consumer':serializer.data
            }

            return Response(content, status = status.HTTP_201_CREATED)
        else:
            content = {'error':'No permissions to create consumer'}   
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk):                
        content = {'description': 'You dont have permissions to remove the customer.'}
        return Response(content, status = status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def add_address(self, request, pk):
        try:
            flat_number = request.data['flat_number']
            building = request.data['building']
            street = request.data['street']
            area_code = request.data['area_code']
        except:
            content = {'error':'Incomplete params', 'description':'flat_number, building, street, area_code, consumer_id'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        area = get_object_or_404(Area, area_code = area_code)
        new_address = Address.objects.create(flat_number=flat_number, building=building, street=street, area = area)

        role = user_role(request.user)
        if role == constants.VENDOR:
            consumer = get_object_or_404(Consumer, pk = pk)
            consumer.addresses.add(new_address)

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
        
        address = get_object_or_404(Address, pk = address_id)
        address.delete()
        
        content = {'description': 'Deleted successfully'}
        return Response(content, status = status.HTTP_200_OK)
        