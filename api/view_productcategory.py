from yourguy.models import ProductCategory

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets

from api.serializers import ProductCategorySerializer

class ProductCategoryViewSet(viewsets.ModelViewSet):
    """
    ProductCategory viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
