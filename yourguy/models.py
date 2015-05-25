from django.db import models
from django.contrib.auth.models import User

from django.core.validators import RegexValidator
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

import datetime

class Area(models.Model):

    # Mandatory Fields
    area_code = models.CharField(max_length = 10)
    area_name = models.CharField(max_length = 50)

    # Optional Fields

    def __unicode__(self):
        return u"%s" % self.area_name

class Address(models.Model):

    # Mandatory Fields
    flat_number = models.CharField(max_length = 50) 
    building = models.CharField(max_length = 100)
    street = models.CharField(max_length = 100)
    area = models.ForeignKey(Area, blank = True, null = True)

    # Optional Fields
    landmark = models.CharField(max_length = 50, blank = True)
    pin_code = models.CharField(max_length = 10, blank = True)
    country_code = models.CharField(max_length = 10, default='IN')

    latitude = models.CharField(max_length = 20, blank = True)
    longitude = models.CharField(max_length = 20, blank = True)

    def __unicode__(self):
        return u"%s - %s - %s" % (self.flat_number, self.building, self.street)                

class YGUser(models.Model):

    user = models.OneToOneField(User)

    # Optional Fields
    picture_link = models.CharField(max_length = 50, blank = True)

    class Meta:
        abstract = True

class DeliveryGuy(YGUser):
    # Mandatory Fields
    AVAILABLE = 'AVAILABLE'
    BUSY = 'BUSY'
    STATUS_CHOICES = (
        (AVAILABLE, 'AVAILABLE'),
        (BUSY, 'BUSY'),
    )
    status = models.CharField(max_length = 15, choices = STATUS_CHOICES, default = AVAILABLE)

    # Optional Fields    
    latitude = models.CharField(max_length = 10, blank = True)
    longitude = models.CharField(max_length = 10, blank = True)

    def __unicode__(self):
        return unicode(self.user.username)

class Vendor(models.Model):
    # Mandatory Fields
    store_name = models.CharField(max_length = 100)
    email = models.EmailField(max_length = 50)
    phone_number = models.CharField(max_length = 15, blank = True, null = True)
    addresses = models.ManyToManyField(Address)
    
    # Optional
    website_url = models.CharField(max_length = 100, blank = True)
    verified = models.BooleanField(blank = True, default = False)
    pan_card = models.CharField(max_length = 15, blank = True)
    notes = models.CharField(max_length = 500, blank = True)

    def __unicode__(self):
        return unicode(self.store_name)

class VendorAgent(YGUser):
    vendor = models.ForeignKey(Vendor, related_name='vendor')
    branch = models.CharField(max_length = 50, blank = True)
    
    EMPLOYEE = 'EMPLOYEE'
    MANAGER = 'MANAGER'
    VENDOR_AGENT_CHOICES = (
            (EMPLOYEE, 'EMPLOYEE'),
            (MANAGER, 'MANAGER')
            )
    role = models.CharField(max_length = 15, choices = VENDOR_AGENT_CHOICES, default = EMPLOYEE)

    def __unicode__(self):
        return u"%s - %s" % (self.vendor.store_name, self.user.first_name)

class Employee(YGUser):
    
    # Mandatory Fields
    employee_code = models.CharField(max_length = 20)

    SALES = 'SALES'
    OPS = 'OPERATIONS'
    CALLER = 'CALLER'
    MANAGER = 'MANAGER'
    DEPARTMENT_CHOICES = (
            (SALES, 'SALES'),
            (OPS, 'OPERATIONS'),
            (CALLER, 'CALLER'),
            (MANAGER, 'MANAGER')
            )
    department = models.CharField(max_length = 15, choices = DEPARTMENT_CHOICES, default = CALLER)

    def __unicode__(self):
        return unicode(self.user.username)


class Consumer(YGUser):
    
    # Optional Fields
    facebook_id = models.CharField(max_length = 50, blank = True)
    associated_vendor = models.ManyToManyField(Vendor, blank = True)
    phone_verified = models.BooleanField(blank = True, default = False)
    addresses  = models.ManyToManyField(Address)

    def __unicode__(self):
        return unicode(self.user.first_name)


class PushDetail(models.Model):

    # Mandatory Fields
    user = models.ForeignKey(User)
    device_token = models.CharField(max_length = 200)

    # Optional Fields
    device_id = models.CharField(max_length = 100, blank = True)
    platform = models.CharField(max_length = 10, blank = True)

    def __unicode__(self):
        return unicode(self.device_token)


class DGAttendance(models.Model):

    # Mandatory Fields
    dg = models.ForeignKey(DeliveryGuy)
    date = models.DateField(default = datetime.date.today)

    LEAVE = 'LEAVE'
    WORKING = 'WORKING'
    UNKNOWN = 'UNKNOWN'
    STATUS_CHOICES = (
            (LEAVE, 'LEAVE'),
            (WORKING, 'WORKING'),
            (UNKNOWN, 'UNKNOWN'),
            )
    status = models.CharField(max_length = 15, choices = STATUS_CHOICES, default = UNKNOWN)

    # Optional Fields
    login_time = models.DateTimeField(blank = True, null = True)
    logout_time = models.DateTimeField(blank = True, null = True)

    def __unicode__(self):
        return u"%s %s" % (self.dg.user.username, self.status)


class Group(models.Model):
    
    # Mandatory Fields
    name = models.CharField(max_length = 50)
    created_by = models.ForeignKey(User)
    created_date_time = models.DateTimeField(auto_now_add = True)

    # Optional Fields

    def __unicode__(self):
        return unicode(self.name)

class UserGroup(models.Model):
    
    # Mandatory Fields
    group = models.ForeignKey(Group)     
    user =  models.ForeignKey(User)
    
    # Optional Fields
 
    def __unicode__(self):
        return unicode(self.group.id)
                        
class Product(models.Model):

    # Mandatory Fields
    name = models.CharField(max_length = 100)
    description = models.CharField(max_length = 500, blank = True, null = True)
    cost = models.FloatField(default = 0.0)
    vendor = models.ForeignKey(Vendor, blank = True, null = True)

    # Optional Fields
    category = models.CharField(max_length = 50, blank = True, null = True)

    def __unicode__(self):
        return u"%s" % self.name

class ProductCategory(models.Model):

    # Mandatory Fields
    category_name = models.CharField(max_length = 100)

    # Optional Fields
    details = models.CharField(max_length = 500, blank = True, null = True)

    def __unicode__(self):
        return u"%s" % self.id

class OrderItem(models.Model):
    product = models.ForeignKey(Product, blank = True, null = True)
    quantity = models.FloatField(default = 1.0)
    cost = models.FloatField(default = 0.0)
    def __unicode__(self):
        return u"%s" % self.id

class Order(models.Model):

    # Mandatory Fields =====
    vendor = models.ForeignKey(Vendor)
    consumer = models.ForeignKey(Consumer)

    QUEUED = 'QUEUED'
    INTRANSIT = 'INTRANSIT'
    DELIVERED = 'DELIVERED'
    ORDER_CHOICES = (
        (QUEUED, 'QUEUED'),
        (INTRANSIT, 'INTRANSIT'),
        (DELIVERED, 'DELIVERED'),
    )
    order_status = models.CharField(max_length = 15, choices = ORDER_CHOICES, default = QUEUED)

    order_items = models.ManyToManyField(OrderItem)
    total_cost = models.FloatField(default = 0.0)

    pickup_datetime = models.DateTimeField()
    delivery_datetime = models.DateTimeField()
    
    pickup_address = models.ForeignKey(Address, related_name='pickup_address', on_delete = models.CASCADE)
    delivery_address = models.ForeignKey(Address, related_name='delivery_address', on_delete = models.CASCADE)

    # Auto Generated Fields =====
    created_date_time = models.DateTimeField(auto_now_add = True)
    created_by_user = models.ForeignKey(User, related_name='order_created_by')

    # Optional Fields =====
    pickedup_datetime = models.DateTimeField(blank = True, null = True)
    completed_datetime = models.DateTimeField(blank = True, null = True)

    notes = models.CharField(max_length = 500, blank = True)
    vendor_order_id = models.CharField(max_length = 10, blank = True)

    is_COD = models.BooleanField(blank = True, default = False)
    assigned_deliveryGuy = models.ForeignKey(User, blank = True, related_name = 'assinged_dg', null = True)

    # Order Modified =====
    modified_by_user = models.ForeignKey(User, blank = True, related_name='order_modified_by', null = True)
    modified_date_time = models.DateTimeField(blank = True, null = True)
    
    # Cancel Request =====
    cancel_request_by_user = models.ForeignKey(User, blank = True, related_name='cancelled_by_user', null = True)
    cancel_request_time = models.DateTimeField(blank = True, null = True)


    def __unicode__(self):
        return u"%s - %s - %s" % (self.vendor.store_name, self.consumer.user.first_name, self.order_status)


class Suggestion(models.Model):

    # Mandatory Fields
    description = models.TextField()
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    date_time = models.DateTimeField(auto_now_add = True)

    # Optional Fields

    def __unicode__(self):
        return u"%s" % self.id

class Message(models.Model):

    # Mandatory Fields
    message = models.TextField()
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    date_time = models.DateTimeField(auto_now_add = True)

    # Optional Fields


    def __unicode__(self):
        return u"%s" % self.id

class Account(models.Model):

    # Mandatory Fields
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    balance = models.FloatField(default = 0.0)
    last_update_date = models.DateTimeField(auto_now_add = True)

    # Optional Fields

    def __unicode__(self):
        return u"%s" % self.id

class UserSetting(models.Model):

    # Mandatory Fields
    user = models.ForeignKey(User, on_delete = models.CASCADE)

    # Optional Fields
    is_push_enabled = models.BooleanField(blank = True, default = False)

    def __unicode__(self):
        return u"%s" % self.user.id

class Transaction(models.Model):

    # Mandatory Fields
    from_user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'from_user')
    to_user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'to_user')
    date_time = models.DateTimeField(auto_now_add = True)
    amount = models.FloatField(default = 0.0)

    def __unicode__(self):
        return u"%s" % self.from_user.id
