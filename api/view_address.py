from yourguy.models import Address

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets

from api.serializers import AddressSerializer

class AddressViewSet(viewsets.ModelViewSet):
    """
    Address viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Address.objects.all()
    serializer_class = AddressSerializer
