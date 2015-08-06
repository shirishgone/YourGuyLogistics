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

import constants

class DGViewSet(viewsets.ModelViewSet):
    """
    DeliveryGuy viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = DeliveryGuy.objects.all()
    serializer_class = DGSerializer

    def get_queryset(self):
        queryset = DeliveryGuy.objects.order_by(Lower('user__first_name'))
        return queryset

    @list_route()
    def available_dgs():
    	dg_list = DeliveryGuy.objects.filter(availability = 'AV')
    	serializer = DGSerializer(dg_list, many = True)
    	return Response(serializer.data)

    @detail_route(methods=['post'])
    def update_pushtoken(self, request, pk=None):
        push_token = request.data['push_token']
        
        dg = get_object_or_404(DeliveryGuy, user = request.user)
        dg.device_token = push_token
        dg.save()

        content = {'description': 'Push Token updated'}
        return Response(content, status = status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def update_location(self, request, pk=None):
        latitude = request.data['latitude']
        longitude = request.data['longitude']
        
        dg = get_object_or_404(DeliveryGuy, user = request.user)
        dg.latitude = latitude
        dg.longitude = longitude
        dg.last_connected_time = datetime.now() 
        dg.save()

        content = {'description': 'Location updated'}
        return Response(content, status = status.HTTP_200_OK)

        
    @detail_route(methods=['post'])
    def check_in(self, request, pk=None):   
        app_version = request.data.get('app_version')

        dg = get_object_or_404(DeliveryGuy, user = request.user)
        dg.status = constants.DG_STATUS_AVAILABLE
        if app_version is not None:
            dg.app_version = app_version
        dg.save()

        today = datetime.now()
        is_today_checkedIn = False
        
        attendance_list = DGAttendance.objects.filter(dg = dg, date__year = today.year , date__month = today.month, date__day = today.day)
        if len(attendance_list) > 0:
            is_today_checkedIn = True

        if is_today_checkedIn == False:
            attendance = DGAttendance.objects.create(dg = dg, date = today, login_time = today)
            attendance.status = constants.DG_STATUS_WORKING
            attendance.save()
            is_today_checkedIn = True

        if is_today_checkedIn is True:
            content = {'description': 'Thanks for checking in.'}
            return Response(content, status = status.HTTP_200_OK)
        else:
            content = {'error':'Something went wrong'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
 

    @detail_route(methods=['post'])
    def check_out(self, request, pk=None):
        dg = get_object_or_404(DeliveryGuy, user = request.user)
        dg.status = constants.DG_STATUS_UN_AVAILABLE
        dg.save()
    
        is_checkout_done = False
        today = datetime.now()
                
        attendance = DGAttendance.objects.filter(dg = dg, date__year = today.year , date__month = today.month, date__day = today.day).latest('date')
        
        if attendance is not None:
            attendance.logout_time = datetime.now()
            attendance.save()
            is_checkout_done = True

        if is_checkout_done is True:
            content = {'description': 'Thanks for checking out.'}
            return Response(content, status = status.HTTP_200_OK)
        else:
            content = {'error':'Something went wrong'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
    

    @detail_route(methods=['post'])
    def attendance(self, request, pk):
        month = request.data.get('month')
        year = request.data.get('year')
         
        dg = get_object_or_404(DeliveryGuy, pk = pk)
        all_attendance = DGAttendance.objects.filter(dg = dg)

        if year is not None:
            all_attendance = all_attendance.filter(date__year = year)
        if month is not None:
            all_attendance = all_attendance.filter(date__month = month)

        serializer = DGAttendanceSerializer(all_attendance, many=True)
        return Response(serializer.data)
    
    @list_route()
    def all_dg_attendance(self, request):
        date_string = self.request.QUERY_PARAMS.get('date', None)
        if date_string is not None:
            date = parse_datetime(date_string)
        else:
            date = datetime.today()

        all_attendance = DGAttendance.objects.filter(date = date)

        serializer = DGAttendanceSerializer(all_attendance, many=True)
        return Response(serializer.data)

