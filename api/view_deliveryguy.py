from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets

from yourguy.models import DeliveryGuy
from api.serializers import DGSerializer

from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

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
    def update_location(self, request):
        latitude = request.data['latitude']
        longitude = request.data['longitude']
        
        dg = get_object_or_404(DeliveryGuy, user = request.user)
        dg.latitude = latitude
        dg.longitude = longitude
        dg.save()

        content = {'description': 'Location updated'}
        return Response(content, status = status.HTTP_201_CREATED)