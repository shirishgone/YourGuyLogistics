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

    # from rest_framework.decorators import detail_route, list_route
    # from rest_framework.response import Response
    # @list_route()
    # def vendor_address(self, vendor_id, request):
    #     vendor = self.get_vendor(vendor_id)
    #     serializer = AddressSerializer(vendor.address)
    #     return Response(serializer.data)

    # @list_route()
    # def consumer_address(self, consumer_id, request):
    #     consumer = self.get_consumer(vendor_id)
    #     serializer = AddressSerializer(consumer.address)
    #     return Response(serializer.data)
