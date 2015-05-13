from django.db import models
from django.contrib.auth.models import User

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

import datetime

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance = None, created = False, **kwargs):
    if created:
        Token.objects.create(user = instance)


class YGUser(models.Model):

    user = models.OneToOneField(User)

    # Mandatory Fields
    phone_number = models.CharField(max_length = 100, unique = True)

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
    flat_number = models.CharField(max_length = 50)
    # area_name = models.CharField(max_length = 50)
    area = models.ForeignKey(Area, related_name='area', default=0)

    # Optional Fields
    floor_number = models.CharField(max_length = 50, blank = True)
    building_name = models.CharField(max_length = 50, blank = True)
    wing = models.CharField(max_length = 50, blank = True)
    road = models.CharField(max_length = 50, blank = True)
    landmark = models.CharField(max_length = 50, blank = True)
    pin_code = models.CharField(max_length = 10, blank = True)
    country_code = models.CharField(max_length = 10, default='IN')
    def __unicode__(self):        
        return u"%s" % self.id


class DeliveryGuy(YGUser):
    # Mandatory Fields
    # assigned_locality_code = models.CharField(max_length = 10)
    assigned_area = models.ForeignKey(Area, related_name='assigned_area', blank = True, default=0)
    
    AVAILABLE = 'AV'
    BUSY = 'BS'
    STATUS_CHOICES = (
        (AVAILABLE, 'Available'),
        (BUSY, 'Busy'),
    )
    availability = models.CharField(max_length = 2, choices = STATUS_CHOICES, default = AVAILABLE)

    # Optional Fields
    address  = models.ForeignKey(Address, related_name='dg_home_address', blank = True)
    latitude = models.CharField(max_length = 10, blank = True)
    longitude = models.CharField(max_length = 10, blank = True)
    alternate_phone_number = models.CharField(max_length = 15, blank = True)
    escalation_phone_number = models.CharField(max_length = 15, blank = True)

    def __unicode__(self):
        return unicode(self.assigned_locality_code)


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

    SALES = 'SL'
    OPS = 'OP'
    CALLCENTER = 'CC'
    MANAGER = 'MG'
    DEPARTMENT_CHOICES = (
            (SALES, 'Sales'),
            (OPS, 'Operations'),
            (CALLCENTER, 'CallCenter'),
            (MANAGER, 'Manager')
            )
    department = models.CharField(max_length = 2, choices = DEPARTMENT_CHOICES, default = CALLCENTER)

    def __unicode__(self):
        return unicode(self.employee_code)


class Consumer(YGUser):

    # Optional Fields
    facebook_id = models.CharField(max_length = 50, blank = True)
    address = models.ForeignKey(Address, related_name='consumer_address', blank = True, on_delete = models.CASCADE)
    associated_vendor = models.ManyToManyField(Vendor, blank = True)
    is_verified = models.BooleanField(blank = True, default = False)

    def __unicode__(self):
        return unicode(self.facebook_id)


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

    LEAVE = 'LE'
    WORKING = 'WG'
    UNKNOWN = 'UN'
    STATUS_CHOICES = (
            (LEAVE, 'Leave'),
            (WORKING, 'Working'),
            (UNKNOWN, 'UN'),
            )
    status = models.CharField(max_length = 2, choices = STATUS_CHOICES, default = UNKNOWN)

    # Optional Fields
    login_time = models.DateTimeField(blank = True)
    logout_time = models.DateTimeField(blank = True)

    def __unicode__(self):
        return u"%s" % self.dg.id


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

    # Mandatory Fields
    pickup_datetime = models.DateTimeField()
    delivery_datetime = models.DateTimeField()
    created_date_time = models.DateTimeField(auto_now_add = True)

    created_by_user = models.ForeignKey(User, related_name='order_created_by')
    pickup_address = models.ForeignKey(Address, related_name='pickup_address', on_delete = models.CASCADE)
    delivery_address = models.ForeignKey(Address, related_name='delivery_address', on_delete = models.CASCADE)

    UNASSIGNED = 'UN'
    ASSIGNED = 'AS'
    COMPLETED = 'CD'
    ORDER_CHOICES = (
        (UNASSIGNED, 'UnAssigned'),
        (ASSIGNED, 'Assigned'),
        (COMPLETED, 'Completed'),
    )
    order_status = models.CharField(max_length = 2, choices = ORDER_CHOICES, default = UNASSIGNED)

    # Optional Fields =====
    vendor = models.ForeignKey(Vendor, blank = True, null = True)
    is_COD = models.BooleanField(blank = True, default = False)
    assigned_to = models.ForeignKey(User, blank = True, related_name = 'assinged_dg', null = True)

    completed_datetime = models.DateTimeField(blank = True, null = True)
    modified_by_user = models.ForeignKey(User, blank = True, related_name='order_modified_by', null = True)
    modified_date_time = models.DateTimeField(blank = True, null = True)
    quantity = models.FloatField(blank = True, null = True)

    cancel_request_by_user = models.ForeignKey(User, blank = True, related_name='cancelled_by_user', null = True)
    cancel_request_time = models.DateTimeField(blank = True, null = True)

    amount = models.CharField(max_length = 50, blank = True)
    notes = models.CharField(max_length = 500, blank = True)
    vendor_order_id = models.CharField(max_length = 10, blank = True)

    def __unicode__(self):
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
