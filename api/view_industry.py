from yourguy.models import Industry

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets

from api.serializers import IndustrySerializer

class IndustryViewSet(viewsets.ModelViewSet):
    """
    Industry viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer
