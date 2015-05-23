from yourguy.models import Product, VendorAgent

# from django.contrib.auth.decorators import permission_required, group_required
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets
from rest_framework.response import Response

from api.serializers import ProductSerializer
from api.views import user_role
import constants


class ProductViewSet(viewsets.ModelViewSet):
    """
    Product viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # @group_required(constants.VENDOR)
    # @permission_required(constants.VENDOR)
    def list(self, request):
    	role = user_role(request.user)
    	if role == constants.VENDOR:
    		vendor_agent = VendorAgent.objects.get(user = self.request.user)
    		products_of_vendor = Product.objects.filter(vendor = vendor_agent.vendor)
    		serializer = ProductSerializer(products_of_vendor, many=True)
    		return Response(serializer.data, status=status.HTTP_201_CREATED)
    	else:
    		content = {'error':'You dont have permissions to view all vendors'}
    		return Response(content, status = status.HTTP_400_BAD_REQUEST)


