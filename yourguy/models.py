from django.db import models
from django.contrib.auth.models import User

from django.core.validators import RegexValidator
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

import datetime

# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_auth_token(sender, instance = None, created = False, **kwargs):
#     if created:
#         Token.objects.create(user = instance)


class YGUser(models.Model):

    user = models.OneToOneField(User)

    # Mandatory Fields
    phone_number = models.CharField(max_length = 15, unique = True)

    # Optional Fields
    picture_link = models.CharField(max_length = 50, blank = True)
    email = models.EmailField(max_length = 254, blank = True)

    class Meta:
        abstract = True

class Area(models.Model):

    # Mandatory Fields
    area_code = models.CharField(max_length = 10)
    area_name = models.CharField(max_length = 50)

    # Optional Fields

    def __unicode__(self):
        return u"%s" % self.area_name

class Address(models.Model):

    # Mandatory Fields
    flat_number = models.CharField(max_length = 10) 
    building = models.CharField(max_length = 100)
    street = models.CharField(max_length = 100)
    area_code = models.CharField(max_length = 10)

    # Optional Fields
    landmark = models.CharField(max_length = 50, blank = True)
    pin_code = models.CharField(max_length = 10, blank = True)
    country_code = models.CharField(max_length = 10, default='IN')

    latitude = models.CharField(max_length = 20, blank = True)
    longitude = models.CharField(max_length = 20, blank = True)

    def __unicode__(self):
        return u"%s %s %s %s" % (self.flat_number, self.building, self.street, self.area_code)                


class DeliveryGuy(YGUser):
    # Mandatory Fields

    # Optional Fields
    
    AVAILABLE = 'AVAILABLE'
    BUSY = 'BUSY'
    STATUS_CHOICES = (
        (AVAILABLE, 'AVAILABLE'),
        (BUSY, 'BUSY'),
    )
    availability = models.CharField(max_length = 15, choices = STATUS_CHOICES, default = AVAILABLE)
    
    assigned_area = models.ForeignKey(Area, related_name='assigned_area', blank = True, default=0, null = True)
    address  = models.ForeignKey(Address, related_name='dg_home_address', blank = True, null = True)
    latitude = models.CharField(max_length = 10, blank = True)
    longitude = models.CharField(max_length = 10, blank = True)
    alternate_phone_number = models.CharField(max_length = 15, blank = True)
    escalation_phone_number = models.CharField(max_length = 15, blank = True)

    def __unicode__(self):
        return unicode(self.user.username)


class Vendor(YGUser):
    # Mandatory Fields
    store_name = models.CharField(max_length = 200)

    # Optional
    address = models.ForeignKey(Address, related_name='vendor_address', blank = True, null = True)
    website_url = models.CharField(max_length = 100, blank = True)

    def __unicode__(self):
        return unicode(self.store_name)


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
    address = models.ForeignKey(Address, related_name='consumer_address', null = True, blank = True, on_delete = models.CASCADE)
    associated_vendor = models.ManyToManyField(Vendor, blank = True)
    is_verified = models.BooleanField(blank = True, default = False)

    def __unicode__(self):
        return unicode(self.user.username)


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
                        

class Order(models.Model):

    # Auto Generated Fields =====
    created_date_time = models.DateTimeField(auto_now_add = True)
    created_by_user = models.ForeignKey(User, related_name='order_created_by')

    # Mandatory Fields =====
    pickup_datetime = models.DateTimeField()
    delivery_datetime = models.DateTimeField()
    
    pickup_address = models.ForeignKey(Address, related_name='pickup_address', on_delete = models.CASCADE)
    delivery_address = models.ForeignKey(Address, related_name='delivery_address', on_delete = models.CASCADE)

    QUEUED = 'QUEUED'
    INTRANSIT = 'INTRANSIT'
    DELIVERED = 'DELIVERED'
    ORDER_CHOICES = (
        (QUEUED, 'QUEUED'),
        (INTRANSIT, 'INTRANSIT'),
        (DELIVERED, 'DELIVERED'),
    )
    order_status = models.CharField(max_length = 15, choices = ORDER_CHOICES, default = QUEUED)

    # Optional Fields =====
    vendor = models.ForeignKey(Vendor, blank = True, null = True)
    consumer = models.ForeignKey(Consumer, blank = True, null = True)

    completed_datetime = models.DateTimeField(blank = True, null = True)
    quantity = models.FloatField(blank = True, null = True)
    amount = models.CharField(max_length = 50, blank = True)
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
        # return u"%s %s" % (self.vendor.user.username, self.cusumer.user.username, self.order_status)
        return u"%s" % self.id


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

class Product(models.Model):

    # Mandatory Fields
    name = models.CharField(max_length = 100)
    category = models.CharField(max_length = 50)

    # Optional Fields

    def __unicode__(self):
        return u"%s" % self.id

class ProductCategory(models.Model):

    # Mandatory Fields
    category_name = models.CharField(max_length = 100)

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
