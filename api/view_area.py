from yourguy.models import Area

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets

from api.serializers import AreaSerializer

class AreaViewSet(viewsets.ModelViewSet):
    """
    Area viewset that provides the standard actions 
    """
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    queryset = Area.objects.all()
    serializer_class = AreaSerializer
