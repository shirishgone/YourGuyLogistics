from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from django.db.models.functions import Lower

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from yourguy.models import DeliveryGuy, DGAttendance
from api.serializers import DGSerializer, DGAttendanceSerializer

from datetime import date, datetime, timedelta, time
from api.views import user_role
from api_v2.views import paginate

import constants


def dg_list_dict(delivery_guy):
    dg_list_dict = {
            'id' : delivery_guy.id,
            'name':delivery_guy.user.first_name,
            'phone_number':delivery_guy.user.username,
            'app_version':delivery_guy.app_version,
            'status': delivery_guy.status
            }
    return dg_list_dict

def dg_details_dict(delivery_guy):
    dg_detail_dict = {
            'id' : delivery_guy.id,
            'name':delivery_guy.user.first_name,
            'phone_number':delivery_guy.user.username,
            'app_version':delivery_guy.app_version,
            'status': delivery_guy.status,
            'shift_start_datetime':delivery_guy.shift_start_datetime,
            'shift_end_datetime':delivery_guy.shift_end_datetime,
            'current_load':delivery_guy.current_load,
            'capacity':delivery_guy.capacity,
            'area':delivery_guy.area,
            'battery_percentage': delivery_guy.battery_percentage,
            'last_connected_time': delivery_guy.last_connected_time,
            'assignment_type':delivery_guy.assignment_type,
            'transportation_mode':delivery_guy.assignment_type
            }
    return dg_detail_dict

class DGViewSet(viewsets.ModelViewSet):
    """
    DeliveryGuy viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = DeliveryGuy.objects.all()
    serializer_class = DGSerializer
    
    def retrieve(self, request, pk = None):        
        delivery_guy = get_object_or_404(DeliveryGuy, id = pk)
        role = user_role(request.user)
        if role == 'vendor':
            content = {'error':'You dont have permissions to view delivery guy info'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        else:
            detail_dict = dg_details_dict(delivery_guy)
            response_content = { "data": detail_dict}
            return Response(response_content, status = status.HTTP_200_OK)

    def list(self, request):
        page = self.request.QUERY_PARAMS.get('page', None)
        role = user_role(request.user)
        
        if role == 'vendor':
            content = {'error':'You dont have permissions to view delivery guy info'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
        else:
            all_dgs = DeliveryGuy.objects.all().order_by(Lower('user__first_name'))
            
            # PAGINATE ========
            dgs = paginate(all_dgs, page)
            total_dg_count = len(all_dgs)
            total_pages =  int(total_dg_count/constants.PAGINATION_PAGE_SIZE) + 1

            result = []
            for delivery_guy in dgs:
                result.append(dg_list_dict(delivery_guy))
        
            response_content = { "data": result, "total_pages": total_pages }
            return Response(response_content, status = status.HTTP_200_OK)
