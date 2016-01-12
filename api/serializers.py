from rest_framework import serializers
from django.contrib.auth.models import User, Group

from yourguy.models import OrderDeliveryStatus, Order, OrderItem
from yourguy.models import Area, Address
from yourguy.models import Consumer, Industry, Vendor, VendorAgent, Product, ProductCategory
from yourguy.models import DeliveryGuy, DGAttendance

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

class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(required=False)
    class Meta:
        model = OrderItem

class OrderDeliveryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDeliveryStatus    

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

class DGAttendanceSerializer(serializers.ModelSerializer):
    dg = DGSerializer(required= False)
    class Meta:
        model = DGAttendance

class OrderSerializer(serializers.ModelSerializer):
    consumer = ConsumerSerializer(required=False)
    order_items = OrderItemSerializer(required=False, many = True)
    pickup_address = AddressSerializer(required=False)
    delivery_address = AddressSerializer(required=False)
    vendor = VendorSerializer(required = False)

    class Meta:
        model = Order
     
