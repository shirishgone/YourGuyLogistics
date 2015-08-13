
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

import datetime
class ConsumerViewSet(viewsets.ModelViewSet):
    """
    Consumer viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Consumer.objects.all()

    def list(self, request):
        role = user_role(request.user)
        if role == 'vendor':
            vendor_agent = get_object_or_404(VendorAgent, user = request.user)
            consumers_of_vendor = Consumer.objects.filter(associated_vendor = vendor_agent.vendor).order_by(Lower('user__first_name'))

            print datetime.datetime.now()

            result = []
            for consumer in consumers_of_vendor:
                result_consumer = {
                "id":consumer.id,
                "name":consumer.user.first_name,
                "phone_number":consumer.user.username
                }
                all_addresses = consumer.addresses.all()
                for address in all_addresses:
                    ad = {
                        "id":address.id,
                        "flat":address.flat_number,
                        "building":address.building,
                        "street":address.street,
                        "landmark":address.landmark,
                        "pin_code":address.pin_code,
                        "area_name":address.area.area_name,
                        "area_code":address.area.area_code
                    }
                    result_consumer['address'] = ad
                
                result.append(result_consumer)
            
            print datetime.datetime.now()
            return Response(json.dumps(result), status = status.HTTP_200_OK)
        else:
            content = {'error':'You dont have permissions to view all Consumers'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)