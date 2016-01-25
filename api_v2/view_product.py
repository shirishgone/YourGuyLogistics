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

def product_list_dict(product):
    product_dict = {
            'id' : product.id,
            'name':product.name,
            'description':product.description,
            'cost':product.cost,
            }
    product_dict['timeslots'] = []
    
    for timeslot in product.timeslots.all():
        timeslot_dict = {
        'timeslot_start':timeslot.start_time,
        'timeslot_end':timeslot.end_time
        }
        product_dict['timeslots'].append(timeslot_dict)
        
    return product_dict

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
            products_of_vendor = Product.objects.filter(vendor = vendor_agent.vendor).order_by(Lower('name')).prefetch_related('timeslots')

            result = []
            for product in products_of_vendor:
                product_dict = product_list_dict(product)
                result.append(product_dict)
        
            response_content = { 
            "products": result
            }
            return Response(response_content, status = status.HTTP_200_OK)
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
            
            product_dict = product_list_dict(new_product)
            response_content = { 
            "product": product_dict
            }
            return Response(response_content, status = status.HTTP_201_CREATED)
        else:
            content = {'error':'You dont have permissions to add a product'}
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk):        
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)