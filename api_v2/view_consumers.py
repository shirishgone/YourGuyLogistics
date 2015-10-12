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
from api.views import user_role

from api_v2.views import paginate

import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import constants
        
def consumer_list_dict(consumer):
    consumer_dict = {
            'id' : consumer.id,
            'name':consumer.user.first_name,
            'phone_number':consumer.user.username
            }
    return consumer_dict


def consumer_detail_dict(consumer):
    consumer_dict = {
            'id' : consumer.id,
            'name':consumer.user.first_name,
            'phone_number':consumer.user.username,
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


class ConsumerViewSet(viewsets.ModelViewSet):
    """
    Consumer viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Consumer.objects.all()

    def retrieve(self, request, pk = None):        
        consumer = get_object_or_404(Consumer, id = pk)
        role = user_role(request.user)
        if role == 'vendor':
            vendor_agent = get_object_or_404(VendorAgent, user = request.user)
            all_associated_vendors = consumer.associated_vendor.all()
            is_consumer_associated_to_vendor = False
            for vendor in all_associated_vendors:
                if vendor.id == vendor_agent.vendor.id:
                    is_consumer_associated_to_vendor = True
                    break
            if is_consumer_associated_to_vendor:
                detail_dict = consumer_detail_dict(consumer)
                response_content = { "data": detail_dict}
                return Response(response_content, status = status.HTTP_200_OK)
            else:
                content = {'error':'You dont have permissions to view this consumer.'}
                return Response(content, status = status.HTTP_400_BAD_REQUEST)  
        else:
            content = {'error':'You dont have permissions to view this consumer.'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)  

    def list(self, request):
        page = self.request.QUERY_PARAMS.get('page', None)

        if page is not None:
            page = int(page)
        else:
            page = 1    

        role = user_role(request.user)
        if role == 'vendor':
            vendor_agent = get_object_or_404(VendorAgent, user = request.user)
            total_consumers_of_vendor = Consumer.objects.filter(associated_vendor = vendor_agent.vendor).order_by(Lower('user__first_name'))
        
            # PAGINATE ========
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
                consumer_dict = consumer_list_dict(consumer)
                result.append(consumer_dict)
        
            response_content = { "data": result, "total_pages": total_pages }
            return Response(response_content, status = status.HTTP_200_OK)
        else:
            content = {'error':'You dont have permissions to view all Consumers'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)