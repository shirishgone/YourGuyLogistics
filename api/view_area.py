from django.db.models.functions import Lower
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets
from api.serializers import AreaSerializer
from yourguy.models import Area

class AreaViewSet(viewsets.ModelViewSet):
    """
    Area viewset that provides the standard actions 
    """
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    
    def get_queryset(self):
        queryset = Area.objects.order_by(Lower('area_name'))
        return queryset