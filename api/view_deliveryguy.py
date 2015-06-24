from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from yourguy.models import DeliveryGuy, DGAttendance
from api.serializers import DGSerializer
from datetime import datetime

class DGViewSet(viewsets.ModelViewSet):
    """
    DeliveryGuy viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = DeliveryGuy.objects.all()
    serializer_class = DGSerializer

    @list_route()
    def available_dgs():
    	dg_list = DeliveryGuy.objects.filter(availability='AV')
    	serializer = DGSerializer(dg_list, many=True)
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
        dg = get_object_or_404(DeliveryGuy, user = request.user)
        attendance = DGAttendance.objects.create(dg = dg, login_time = datetime.now())

        content = {'description': 'Checked-in done.'}
        return Response(content, status = status.HTTP_200_OK)


    @detail_route(methods=['post'])
    def check_out(self, request, pk=None):        
        dg = get_object_or_404(DeliveryGuy, user = request.user)

        attendance = DGAttendance.objects.filter(dg=dg).latest('date')
        attendance.logout_time = datetime.now()
        attendance.save()

        content = {'description': 'Checkout done.'}
        return Response(content, status = status.HTTP_200_OK)
