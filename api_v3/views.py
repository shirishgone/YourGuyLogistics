from rest_framework import authentication
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from yourguy.models import Industry, ProductCategory


class IsAuthenticatedOrWriteOnly(permissions.BasePermission):
    """
    The request is authenticated as a user, or is a write-only request.
    """

    def has_permission(self, request, view):
        WRITE_METHODS = ["POST", ]

        return (
            request.method in WRITE_METHODS or
            request.user and
            request.user.is_authenticated()
        )


class IndustryViewSet(viewsets.ModelViewSet):
    """
    Industry viewset that provides the standard actions
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Industry.objects.all()
    # serializer_class = IndustrySerializer



class ProductCategoryViewSet(viewsets.ModelViewSet):
    """
    ProductCategory viewset that provides the standard actions
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = ProductCategory.objects.all()
    # serializer_class = ProductCategorySerializer

