from yourguy.models import Product, VendorAgent, Vendor

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.db.models.functions import Lower

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

    def list(self, request):
        role = user_role(request.user)
        if role == constants.VENDOR:
            vendor_agent = VendorAgent.objects.get(user = self.request.user)
            products_of_vendor = Product.objects.filter(vendor = vendor_agent.vendor).order_by(Lower('name'))
            serializer = ProductSerializer(products_of_vendor, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            content = {'error':'You dont have permissions to view products'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
    
    def create(self, request):
        role = user_role(request.user)
        if role == constants.VENDOR:
            vendor_agent = get_object_or_404(VendorAgent, user = self.request.user)
            vendor = vendor_agent.vendor
            
            try:
                name = request.data['name']
                description = request.data['description']
                cost_string = request.data['cost']
                cost = float(cost_string)
            except:
                content = {'error':'missing params with name, description, cost, vendor'}
                return Response(content, status = status.HTTP_400_BAD_REQUEST)

            new_product = Product.objects.create(vendor = vendor,
                name = name, 
                description = description, 
                cost = cost)

            content = {
            'product_id':new_product.id,
            'description': 'product added successfully'
            }

            return Response(content, status = status.HTTP_200_OK)
        else:
            content = {'error':'You dont have permissions to add a product'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)

