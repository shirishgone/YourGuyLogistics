from rest_framework import serializers
from django.contrib.auth.models import User, Group

from yourguy.models import Order, Area, Address, Consumer, Vendor, DeliveryGuy, Group, UserGroup, VendorAgent, Product, ProductCategory


from django.contrib.auth import get_user_model
# User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'first_name', 'last_name', 'username', 'email')

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area

class AddressSerializer(serializers.ModelSerializer):
    area = AreaSerializer(required=False)
    class Meta:
        model = Address

class ConsumerSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    address = AddressSerializer(required=False, many=True)
    class Meta:
        model = Consumer

class OrderSerializer(serializers.ModelSerializer):
    consumer = ConsumerSerializer(required=False)
    class Meta:
        model = Order

class VendorSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=False)
    class Meta:
        model = Vendor

class VendorAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorAgent

class DGSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryGuy

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group

class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        
