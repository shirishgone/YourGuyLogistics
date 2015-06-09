from rest_framework import serializers
from django.contrib.auth.models import User, Group

from yourguy.models import Order, OrderItem, Area, Address, Consumer, Vendor, DeliveryGuy, Group, UserGroup, VendorAgent, Product, ProductCategory


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
    addresses = AddressSerializer(required=False, many=True)
    class Meta:
        model = Consumer

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(required=False)
    class Meta:
        model = OrderItem

class OrderSerializer(serializers.ModelSerializer):
    consumer = ConsumerSerializer(required=False)
    order_items = OrderItemSerializer(required=False, many = True)
    pickup_address = AddressSerializer(required=False)
    delivery_address = AddressSerializer(required=False)
    class Meta:
        model = Order

class VendorSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(required=False, many=True)
    class Meta:
        model = Vendor

class VendorAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorAgent

class DGSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    class Meta:
        model = DeliveryGuy

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group

class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup

        
