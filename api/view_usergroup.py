from yourguy.models import UserGroup

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets

from api.serializers import UserGroupSerializer

class UserGroupViewSet(viewsets.ModelViewSet):
    """
    UserGroup viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = UserGroup.objects.all()
    serializer_class = UserGroupSerializer