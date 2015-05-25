from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from yourguy.models import Consumer, Vendor, VendorAgent, Address, Area
from api.serializers import ConsumerSerializer
from api.views import user_role
from api.views import user_role, is_userexists, is_vendorexists, is_consumerexists, is_dgexists
import constants


class ConsumerViewSet(viewsets.ModelViewSet):
    """
    Consumer viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Consumer.objects.all()
    serializer_class = ConsumerSerializer

    def list(self, request):
        role = user_role(request.user)
        if role == constants.VENDOR:
            vendor_agent = get_object_or_404(VendorAgent, user = request.user)
            consumers_of_vendor = Consumer.objects.filter(associated_vendor = vendor_agent.vendor)
            
            serializer = ConsumerSerializer(consumers_of_vendor, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif role == constants.OPERATIONS:
            all_customers = Consumer.objects.all()
            serializer = ConsumerSerializer(all_customers, many=True)
        else:
            content = {'error':'You dont have permissions to view all Consumers'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def add_vendor(self, request, pk=None):
        vendor_id = request.POST['vendor_id']
        vendor = get_object_or_404(Vendor, id = vendor_id)
        
        current_consumer = get_object_or_404(Consumer, user = request.user)
        current_consumer.associated_vendor.add(vendor)
        current_consumer.save()
        
        content = {'description': 'Vendor added to consumer'}
        return Response(content, status = status.HTTP_201_CREATED)

    def create(self, request):
        role = user_role(request.user)
        if (role == constants.VENDOR) or (role == constants.SALES):
        # CREATING CONSUMER BY VENDOR or SALES
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

            if is_userexists(phone_number) is True:
                user = get_object_or_404(User, username = phone_number)
                if is_consumerexists(user) is True:
                    consumer = get_object_or_404(Consumer, user = user)
                else:
                    consumer = Consumer.objects.create(user = user)
                    address = Address.objects.create(flat_number=flat_number, building=building, street=street, area= area)
                    consumer.address.add(address)
                    consumer.save()
            else:
                user = User.objects.create(username=phone_number, first_name = name, password='')
                consumer = Consumer.objects.create(user = user)
                address = Address.objects.create(flat_number=flat_number, building=building, street=street, area= area)
                consumer.address.add(address)
                consumer.save()

            # SETTING USER GROUP
            group = get_object_or_404(Group, name=constants.CONSUMER)
            group.user_set.add(user)

            # SETTING ASSOCIATED VENDOR
            vendor_agent = VendorAgent.objects.get(user = request.user)
            consumer.associated_vendor.add(vendor_agent.vendor)
            consumer.save()
            
            # SUCCESS RESPONSE FOR CONSUMER CREATION BY VENDOR
            content = {'consumer_id':consumer.id}   
            return Response(content, status = status.HTTP_201_CREATED)
        else:
            content = {'error':'No permissions to create consumer'}   
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        