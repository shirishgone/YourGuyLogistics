from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.db.models.functions import Lower
import json

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from yourguy.models import Consumer, Vendor, VendorAgent, Address, Area
from api.views import user_role, is_userexists

from api_v2.views import paginate

import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import constants
from django.db.models import Q

from api_v3.view_consumer import is_consumer_has_same_address_already, fetch_or_create_consumer, fetch_or_create_consumer_address

def consumer_list_dict(consumer):
    consumer_dict = {
            'id' : consumer.id,
            'name':consumer.full_name,
            'phone_number':consumer.phone_number
            }
    return consumer_dict


def consumer_detail_dict(consumer):
    consumer_dict = {
            'id' : consumer.id,
            'name':consumer.full_name,
            'phone_number':consumer.phone_number,
            "addresses":[]
            }
    
    all_addresses = consumer.addresses.all()
    for address in all_addresses:
        adr_dict = {
        "id":address.id,
        "full_address":address.full_address,
        "landmark":address.landmark,
        "pin_code":address.pin_code
        }   
        consumer_dict['addresses'].append(adr_dict)

    return consumer_dict

def excel_download_consumer_detail(consumer):
    consumer_dict = {
            'name':consumer.full_name,
            'phone_number':consumer.phone_number,
            "addresses":[]
            }
    
    all_addresses = consumer.addresses.all()
    for address in all_addresses:
        adr_dict = {
        "full_address":address.full_address,
        "landmark":address.landmark,
        "pin_code":address.pin_code
        }   
        consumer_dict['addresses'].append(adr_dict)
    return consumer_dict

class ConsumerViewSet(viewsets.ModelViewSet):
    """
    Consumer viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Consumer.objects.all()

    def destroy(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, pk = None):        
        consumer = get_object_or_404(Consumer, id = pk)
        role = user_role(request.user)
        if role == constants.VENDOR:
            vendor_agent = get_object_or_404(VendorAgent, user = request.user)
            if consumer.vendor.id == vendor_agent.vendor.id:
                detail_dict = consumer_detail_dict(consumer)
                return Response(detail_dict, status = status.HTTP_200_OK)
            else:
                content = {'error':'You dont have permissions to view this consumer.'}
                return Response(content, status = status.HTTP_400_BAD_REQUEST)  
        else:
            content = {'error':'You dont have permissions to view this consumer.'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)  

    def list(self, request):
        page = self.request.QUERY_PARAMS.get('page', None)
        search_query = request.QUERY_PARAMS.get('search', None)
        addresses_required = False
        
        if page is not None:
            page = int(page)
        else:
            page = 1    

        role = user_role(request.user)
        if role == constants.VENDOR:
            vendor_agent = get_object_or_404(VendorAgent, user = request.user)
            total_consumers_of_vendor = Consumer.objects.filter(vendor = vendor_agent.vendor).order_by(Lower('full_name'))
        
            # SEARCH KEYWORD FILTERING -------------------------------------------------
            if search_query is not None:
                total_consumers_of_vendor = total_consumers_of_vendor.filter(Q(full_name__icontains=search_query) | Q(phone_number=search_query))
                addresses_required = True
            # --------------------------------------------------------------------------

            # FETCH ADDRESSES OF CUSTOMER ----------------------------------------------
            if addresses_required:
                total_consumers_of_vendor = total_consumers_of_vendor.prefetch_related('addresses')
            # --------------------------------------------------------------------------            
            
            # PAGINATE -----------------------------------------------------------------
            total_customers_count = len(total_consumers_of_vendor)
            total_pages =  int(total_customers_count/constants.PAGINATION_PAGE_SIZE) + 1

            if page > total_pages or page<=0:
                response_content = {
                "error": "Invalid page number"
                }
                return Response(response_content, status = status.HTTP_400_BAD_REQUEST)
            else:
                customers = paginate(total_consumers_of_vendor, page)
            
            result = []
            for consumer in customers:
                if addresses_required:
                    consumer_dict = consumer_detail_dict(consumer)
                else:    
                    consumer_dict = consumer_list_dict(consumer)
                result.append(consumer_dict)
        
            response_content = { "data": result, "total_pages": total_pages }
            return Response(response_content, status = status.HTTP_200_OK)
        else:
            content = {'error':'You dont have permissions to view all Consumers'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
    
    def create(self, request):        
        role = user_role(request.user)
        if (role == constants.VENDOR):
            vendor_agent = VendorAgent.objects.get(user = request.user)
            # REQUEST PARAM CHECK --------------------------------------------
            try:
                phone_number = request.data['phone_number']
                name = request.data['name']
                full_address = request.data['full_address']
                pin_code = request.data['pin_code']
                landmark = request.data.get('landmark')
            except Exception, e:
                content = {
                        'error':'Incomplete parameters',
                        'description':'Mandatory Fields: phone_number, name, full_address, pin_code, landmark [Optional]'
                    }   
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
            # -------------------------------------------------------------
            
            new_consumer = fetch_or_create_consumer(phone_number, name, vendor_agent.vendor)
            new_address = fetch_or_create_consumer_address(new_consumer, full_address, pin_code, landmark)
            
            content = {
            'consumer_id': new_consumer.id,
            'new_address_id':new_address.id
            }
            return Response(content, status = status.HTTP_200_OK)
        else:
            content = {'error':'No permissions to create consumer'}   
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['get'])
    def file_download(self, request):
        role = user_role(request.user)
        if role == constants.VENDOR:
            vendor_agent = get_object_or_404(VendorAgent, user = request.user)
            all_consumers_of_vendor = Consumer.objects.filter(vendor = vendor_agent.vendor).order_by(Lower('full_name'))
            
            result = []
            for consumer in all_consumers_of_vendor:
                consumer_dict = excel_download_consumer_detail(consumer)
                result.append(consumer_dict)
            
            response_content = { 
            "data": result
            }
            return Response(response_content, status = status.HTTP_200_OK)
        else:
            content = {
            'error':'No permissions to access customers',
            'description':'You dont have permissions to fetch customers list'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
    
    @detail_route(methods=['post'])
    def add_address(self, request, pk):
        try:
            full_address = request.data['full_address']
            pin_code = request.data['pin_code']
            landmark = request.data.get('landmark')
        except:
            content = {
            'error':'Incomplete parameters', 
            'description':'full_address, pin_code, landmark [optional]'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

        role = user_role(request.user)
        if role == constants.VENDOR:
            consumer = get_object_or_404(Consumer, pk = pk)
            new_address = fetch_or_create_consumer_address(consumer, full_address, pin_code, landmark)
            content = {
            'address_id': new_address.id
            }
            return Response(content, status = status.HTTP_200_OK)
        else:
            content = {'description': 'You dont have permissions to add address.'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
    
    @detail_route(methods=['post'])
    def remove_address(self, request, pk):
        try:
            address_id = request.data['address_id']
        except:
            content = {
            'error':'Incomplete parameters', 
            'description':'address_id'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        
        role = user_role(request.user)
        if role == constants.VENDOR:
            address = get_object_or_404(Address, pk = address_id)
            consumer = get_object_or_404(Consumer, pk = pk)                        
            consumer.addresses.remove(address)
            
            content = {'description': 'Address removed successfully'}
            return Response(content, status = status.HTTP_200_OK)
        else:
            content = {'description': 'You dont have permissions to add address.'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)