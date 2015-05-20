from yourguy.models import RequestedVendor

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets

from api.serializers import RequestedVendorSerializer

class RequestedVendorViewSet(viewsets.ModelViewSet):
    """
    Requested Vendor viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = RequestedVendor.objects.all()
    serializer_class = VendorSerializer