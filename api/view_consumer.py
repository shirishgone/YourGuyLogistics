from yourguy.models import Consumer, Vendor

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets

# from rest_framework.decorators import detail_route, list_route
# from rest_framework.response import Response

from api.serializers import ConsumerSerializer

class ConsumerViewSet(viewsets.ModelViewSet):
    """
    Consumer viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = ConsumerSerializer
    def get_vendor(self, pk):
        try:
            return Vendor.objects.get(pk=pk)
        except:
            raise Http404
    
    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `consumer_id` or 'vendor_id' query parameter in the URL.
        """
        queryset = Consumer.objects.all()
        
        # filtering through Vendor id        
        vendor_id = self.request.QUERY_PARAMS.get('vendor_id', None)
        if vendor_id is not None:
            vendor = self.get_vendor(vendor_id)
            queryset = queryset.filter(vendor=vendor)

	return queryset

