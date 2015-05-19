from yourguy.models import Consumer, Vendor, VendorAgent

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets

from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from api.serializers import ConsumerSerializer
from api.views import user_role
import constants

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
        Optionally restricts the returned customers to a given vendor,
        by filtering against a 'vendor' query parameter in the URL.
        """
        queryset = Consumer.objects.all()        
        
        # FILTERING THROUGH VENDOR
        role = user_role(self.request.user)
        if role == constants.VENDOR:
            try:
                vendor_agent = VendorAgent.objects.get(user = self.request.user)
            except:
                raise Http404
            queryset = queryset.filter(associated_vendor=vendor_agent.vendor)
        elif role == constants.CONSUMER:
            raise Http404
        else:
            pass

	return queryset

    @detail_route(methods=['post'])
    def add_vendor(self, request, pk=None):
        vendor_id = request.POST['vendor_id']
        vendor = Vendor.objects.get(id = vendor_id)
        
        current_consumer = Consumer.objects.get(user = self.request.user)
        current_consumer.associated_vendor.add(vendor)
        current_consumer.save()
        
        content = {'description': 'Vendor added to consumer'}
        return Response(content, status = status.HTTP_201_CREATED)
