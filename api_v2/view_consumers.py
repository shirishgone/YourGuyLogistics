
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
        
class ConsumerViewSet(viewsets.ModelViewSet):
    """
    Consumer viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Consumer.objects.all()

    def list(self, request):
        page = self.request.QUERY_PARAMS.get('page', None)

        role = user_role(request.user)
        if role == 'vendor':
            vendor_agent = get_object_or_404(VendorAgent, user = request.user)
            total_consumers_of_vendor = Consumer.objects.filter(associated_vendor = vendor_agent.vendor).order_by(Lower('user__first_name'))
        
            # PAGINATE ========
            customers = paginate(total_consumers_of_vendor, page)
            total_customers_count = len(total_consumers_of_vendor)
            total_pages =  int(total_customers_count/constants.PAGINATION_PAGE_SIZE) + 1

            result = []
            for consumer in customers:
                result_consumer = {
                "id":consumer.id,
                "name":consumer.user.first_name,
                "phone_number":consumer.user.username,
                "addresses":[]
                }

                all_addresses = consumer.addresses.all()
                for address in all_addresses:
                    adr = {
                        "id":address.id,
                        "flat":address.flat_number,
                        "building":address.building,
                        "street":address.street,
                        "landmark":address.landmark,
                        "pin_code":address.pin_code
                    }
                    area = address.area
                    if area is not None:
                        adr["area_name"] = address.area.area_name
                        adr["area_code"] = address.area.area_code
                    else:
                        adr["area_name"] = None
                        adr["area_code"] = None

                    result_consumer['addresses'].append(adr)
                result.append(result_consumer)
        
            response_content = { "data": result, "total_pages": total_pages }
            return Response(response_content, status = status.HTTP_200_OK)
        else:
            content = {'error':'You dont have permissions to view all Consumers'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)