from django.db import models
from django.contrib.auth.models import User

from django.core.validators import RegexValidator
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

import datetime
from recurrence.fields import RecurrenceField

class Location(models.Model):
    latitude = models.CharField(max_length = 50)
    longitude = models.CharField(max_length = 50)
    
    def __unicode__(self):
        return u"%s - %s" % (self.latitude, self.longitude)
    
class ServiceableCity(models.Model):
    city_code = models.CharField(max_length = 10, unique = True)
    city_name = models.CharField(max_length = 100)
    def __unicode__(self):
        return u"%s" % (self.city_name)        

class ServiceablePincode(models.Model):
    pincode = models.CharField(max_length = 10, unique = True)
    city = models.ForeignKey(ServiceableCity, on_delete=models.PROTECT)
    
    def __unicode__(self):
        return u"%s" % (self.pincode)

class TimeSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    def __unicode__(self):
        return u"%s - %s" % (self.start_time, self.end_time)

class Area(models.Model):

    # Mandatory Fields
    area_code = models.CharField(max_length = 25, unique = True)
    area_name = models.CharField(max_length = 100)
    city_name = models.CharField(max_length = 100, default = 'MUMBAI')
    pin_code = models.CharField(max_length = 25, null = True)

    # Optional Fields
    def __unicode__(self):
        return u"%s" % self.area_name

class Picture(models.Model):
    name = models.CharField(max_length = 100, blank = True)  
    url = models.CharField(max_length = 250, blank = True)
    def __unicode__(self):
        return u"%s" % self.name

class Address(models.Model):

    # Mandatory Fields
    flat_number = models.CharField(max_length = 100) 
    building = models.CharField(max_length = 500)
    street = models.CharField(max_length = 500)
    
    # Optional Fields
    full_address = models.CharField(max_length = 500, default = '-')
    pin_code = models.CharField(max_length = 25, blank = True)
    area = models.ForeignKey(Area, blank = True, null = True)
    landmark = models.CharField(max_length = 100, blank = True)
    country_code = models.CharField(max_length = 25, default = 'IN')

    # Location 
    latitude = models.CharField(max_length = 50, blank = True)
    longitude = models.CharField(max_length = 50, blank = True)

    def __unicode__(self):
        return u"%s - %s" % (self.full_address, self.pin_code)                

class NotificationType(models.Model):
    title = models.CharField(max_length = 100)
    code = models.CharField(max_length = 50, unique = True)
    description = models.CharField(max_length = 500, blank = True, null = True)
    
    def __unicode__(self):
        return unicode(self.title)

class Notification(models.Model):
    notification_type = models.ForeignKey(NotificationType, on_delete=models.PROTECT)
    delivery_id = models.CharField(max_length = 1000, blank = True, null = True)
    message = models.CharField(max_length = 500, blank = True, null = True)
    time_stamp = models.DateTimeField(auto_now_add = True)
    read = models.BooleanField(default = False)
    
    def __unicode__(self):
        return unicode(self.notification_type)

class YGUser(models.Model):
    user = models.OneToOneField(User)
    # Optional Fields
    profile_picture = models.ForeignKey(Picture, blank = True, null = True, on_delete=models.PROTECT)
    notifications = models.ManyToManyField(Notification, blank = True)
    class Meta:
        abstract = True

class VendorAccount(models.Model):
    # Mandatory Fields
    pricing = models.FloatField(default = 0.0)
    
    pan = models.CharField(max_length = 50, blank = True)
    billing_address = models.ForeignKey(Address, related_name='billing_address', null = True, on_delete=models.PROTECT)
    last_update_date = models.DateTimeField(auto_now_add = True)
    
    # Optional Fields

    def __unicode__(self):
        return u"%s" % self.id

class Industry(models.Model):
    name = models.CharField(max_length = 100)

    def __unicode__(self):
        return u"%s" % self.name


class Vendor(models.Model):
    # Mandatory Fields
    store_name = models.CharField(max_length = 100)
    email = models.EmailField(max_length = 50)
    phone_number = models.CharField(max_length = 15, blank = True, null = True)
    alternate_phone_number = models.CharField(max_length = 15, blank = True, null = True)
    industries = models.ManyToManyField(Industry, blank = True)

    addresses = models.ManyToManyField(Address, blank = True)
    is_retail = models.BooleanField(default = False)
    account = models.ForeignKey(VendorAccount, related_name='account', blank = True, null = True, on_delete=models.PROTECT)

    # Optional
    website_url = models.CharField(max_length = 100, blank = True)
    verified = models.BooleanField(blank = True, default = False)
    notes = models.CharField(max_length = 500, blank = True)
    is_hyper_local = models.BooleanField(default = False)
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT)
    approved_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    pickup_boy = models.ForeignKey('DeliveryGuy', null=True, blank=True, on_delete=models.PROTECT) 

    def __unicode__(self):
        return unicode(self.store_name)


class DeliveryGuy(YGUser):
    # Mandatory Fields
    employee_code = models.CharField(max_length = 200, blank = True , null = True)
    UN_AVAILABLE = 'UN_AVAILABLE'
    AVAILABLE = 'AVAILABLE'
    BUSY = 'BUSY'
    STATUS_CHOICES = (
        (UN_AVAILABLE, 'UN_AVAILABLE'),
        (AVAILABLE, 'AVAILABLE'),
        (BUSY, 'BUSY'),
    )
    status = models.CharField(max_length = 50, choices = STATUS_CHOICES, default = UN_AVAILABLE)

    shift_start_datetime = models.TimeField(blank=True, null = True)
    shift_end_datetime = models.TimeField(blank=True, null = True)

    current_load = models.IntegerField(default = 0)
    capacity = models.IntegerField(default = 0)

    latitude = models.CharField(max_length = 50, blank = True)
    longitude = models.CharField(max_length = 50, blank = True)

    device_token = models.CharField(max_length = 200, blank = True , null = True)
    battery_percentage = models.FloatField(default = 0.0)
    last_connected_time = models.DateTimeField(blank = True , null = True)
    app_version = models.CharField(max_length = 50, blank = True , null = True)

    CORPORATE = 'CORPORATE'
    RETAIL = 'RETAIL'
    ALL = 'ALL'
    WORK_ASSIGNMENT_CHOICES = (
        (CORPORATE, 'CORPORATE'),
        (RETAIL, 'RETAIL'),
        (ALL, 'ALL'),
    )
    assignment_type = models.CharField(max_length = 50, choices = WORK_ASSIGNMENT_CHOICES, default = ALL)

    BIKER = 'BIKER'
    WALKER = 'WALKER'
    CAR_DRIVER = 'CAR_DRIVER'
    TRANSPORTATION_MODE_CHOICES = (
        (WALKER, 'WALKER'),
        (BIKER, 'BIKER'),
        (CAR_DRIVER, 'CAR_DRIVER'),
    )
    transportation_mode = models.CharField(max_length = 50, choices = TRANSPORTATION_MODE_CHOICES, default = WALKER)
    is_teamlead = models.BooleanField(default = False)
    is_active = models.BooleanField(default = False)
    deactivated_date = models.DateTimeField(blank=True, null=True)
    pending_salary_deduction = models.FloatField(default=0.0)
    associated_vendors = models.ManyToManyField(Vendor, blank=True, related_name='associated_vendors')

    def __unicode__(self):
        return u"%s - %s" % (self.user.first_name, self.user.username)


class DeliveryTeamLead(models.Model):
    created_date_time = models.DateTimeField(auto_now_add = True, blank = True, null = True)
    delivery_guy = models.ForeignKey(DeliveryGuy, related_name='current_delivery_guy', on_delete=models.PROTECT)
    associate_delivery_guys = models.ManyToManyField(DeliveryGuy, blank = True, related_name ='associate_delivery_guys')
    serving_pincodes = models.ManyToManyField(ServiceablePincode, blank = True)
    demote_date = models.DateTimeField(blank=True, null=True)
    demote_reason = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return u"%s - %s" % (self.delivery_guy.user.username, self.delivery_guy.user.first_name)

class VendorAgent(YGUser):
    vendor = models.ForeignKey(Vendor, related_name='vendor', on_delete=models.PROTECT)
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
    employee_code = models.CharField(max_length = 20, blank = True, null = True)
    
    SALES = 'sales'
    SALES_MANAGER = 'sales_manager'
    OPERATIONS = 'operations'
    OPERATIONS_MANAGER = 'operations_manager'
    ACCOUNTS = 'accounts'
    CALLER = 'caller'
    ADMIN = 'admin'
    HR = 'hr'
    DEPARTMENT_CHOICES = (
            (SALES, 'sales'),
            (SALES_MANAGER, 'sales_manager'),
            (OPERATIONS, 'operations'),
            (OPERATIONS_MANAGER, 'operations_manager'),
            (ACCOUNTS, 'accounts'),
            (CALLER, 'caller'),
            (HR, 'hr'),
            (ADMIN, 'admin')
            )
    department = models.CharField(max_length = 50, choices = DEPARTMENT_CHOICES, default = CALLER)
    serving_pincodes = models.ManyToManyField(ServiceablePincode, blank = True)
    city = models.ForeignKey(ServiceableCity, blank = True, null = True)

    associate_delivery_guys = models.ManyToManyField(DeliveryGuy, blank = True, related_name ='ops_associate_delivery_guys')
    def __unicode__(self):
        return u"%s - %s" % (self.user.username, self.user.first_name)

class Consumer(models.Model):
    created_date = models.DateTimeField(auto_now_add = True, blank = True, null = True)
    phone_number = models.CharField(max_length = 100, blank = True, null = True)
    full_name = models.CharField(max_length = 100, blank = True, null = True)
    vendor = models.ForeignKey(Vendor, blank = True, null = True, related_name = 'single_vendor')
    phone_verified = models.BooleanField(blank = True, default = False)
    addresses  = models.ManyToManyField(Address, blank = True)

    def __unicode__(self):
        return unicode(self.full_name)

class DGAttendance(models.Model):

    # Mandatory Fields
    dg = models.ForeignKey(DeliveryGuy, on_delete=models.PROTECT)
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

    checkin_location = models.ForeignKey(Location, related_name = 'checkin_location', blank = True, null = True)
    checkout_location = models.ForeignKey(Location, related_name = 'checkout_location', blank = True, null = True)

    def __unicode__(self):
        return u"%s %s" % (self.dg.user.username, self.status)
   

class ProductCategory(models.Model):
    category_name = models.CharField(max_length = 100)
    details = models.CharField(max_length = 500, blank = True, null = True)

    def __unicode__(self):
        return u"%s" % self.category_name

class Product(models.Model):

    # Mandatory Fields
    name = models.CharField(max_length = 100)
    description = models.CharField(max_length = 500, blank = True, null = True)
    cost = models.FloatField(default = 0.0)
    vendor = models.ForeignKey(Vendor, blank = True, null = True)
    timeslots = models.ManyToManyField(TimeSlot, blank = True)
    product_category = models.ForeignKey(ProductCategory, blank = True, null = True, on_delete=models.PROTECT)
    def __unicode__(self):
        return u"%s - %s" % (self.name, self.vendor)


class OrderItem(models.Model):
    product = models.ForeignKey(Product, blank = True, null = True, on_delete=models.PROTECT)
    quantity = models.FloatField(default = 1.0)
    cost = models.FloatField(default = 0.0)

    def __unicode__(self):
        return u"%s" % self.id
        
class ProofOfDelivery(models.Model):
    date_time = models.DateTimeField(auto_now_add = True)
    receiver_name = models.CharField(max_length = 100)
    signature = models.ForeignKey(Picture, related_name = 'pod_signature', blank = True, null = True)
    pictures = models.ManyToManyField(Picture, blank = True)

    def __unicode__(self):
        return u"%s" % self.id
                

class Order(models.Model):

    # Mandatory Fields =====
    vendor = models.ForeignKey(Vendor, on_delete = models.PROTECT)
    consumer = models.ForeignKey(Consumer, on_delete = models.PROTECT)

    order_items = models.ManyToManyField(OrderItem, blank = True)
    total_cost = models.FloatField(default = 0.0)

    pickup_datetime = models.DateTimeField()
    delivery_datetime = models.DateTimeField(blank = True, null = True)
    
    pickup_address = models.ForeignKey(Address, related_name='pickup_address', on_delete=models.PROTECT)
    delivery_address = models.ForeignKey(Address, related_name='delivery_address', on_delete=models.PROTECT)
    
    # Auto Generated Fields =====
    created_date_time = models.DateTimeField(auto_now_add = True)
    created_by_user = models.ForeignKey(User, related_name='order_created_by', on_delete=models.PROTECT)

    # Optional Fields =====
    notes = models.CharField(max_length = 500, blank = True)
    vendor_order_id = models.CharField(max_length = 100, blank = True)
    
    is_cod = models.BooleanField(blank = True, default = False)
    cod_amount = models.FloatField(default = 0.0)

    is_reverse_pickup = models.BooleanField(default = False)
    delivery_charges = models.FloatField(default = 0.0)
    is_recurring = models.BooleanField(blank = True, default = False)
    
    # Order Modified =====
    modified_by_user = models.ForeignKey(User, blank = True, related_name='order_modified_by', null = True, on_delete=models.PROTECT)
    modified_date_time = models.DateTimeField(blank = True, null = True)
    
    def __unicode__(self):
        return u"%s - %s - %s" % (self.id, self.vendor.store_name, self.consumer.full_name)


class DeliveryAction(models.Model):
    code = models.CharField(max_length=10, blank=True)
    title = models.CharField(max_length = 100)
    def __unicode__(self):
        return u"%s" % (self.title)


class DeliveryTransaction(models.Model):
    action = models.ForeignKey(DeliveryAction, on_delete=models.PROTECT)
    by_user = models.ForeignKey(User, blank = True, null = True)
    time_stamp = models.DateTimeField(blank = True, null = True)
    location = models.ForeignKey(Location, blank = True, null = True)
    remarks = models.CharField(max_length = 500, blank = True)
    def __unicode__(self):
        return u"%s" % (self.action)


class ProofOfBankDeposit(models.Model):
    created_by_user = models.ForeignKey(User, related_name='pobd_created_by_user', on_delete=models.PROTECT)
    created_time_stamp = models.DateTimeField(auto_now_add=True)
    updated_by_user = models.ForeignKey(User, blank=True, null=True, related_name='updated_by_user', on_delete=models.PROTECT)
    updated_time_stamp = models.DateTimeField(blank=True, null=True)
    receipt_number = models.CharField(max_length=100)
    receipt = models.ForeignKey(Picture, blank=True, null=True)
    total_cod = models.FloatField(default=0.0)

    NONE = 'NONE'
    VERIFIED = 'VERIFIED'
    DECLINED = 'DECLINED'

    PROOF_STATUS_CHOICES = (
            (NONE, 'NONE'),
            (VERIFIED, 'VERIFIED'),
            (DECLINED, 'DECLINED')
            )

    proof_status = models.CharField(max_length=30, choices=PROOF_STATUS_CHOICES, default=NONE)

    def __unicode__(self):
        return u"%s" % self.id


class CODAction(models.Model):
    code = models.CharField(max_length=10)
    title = models.CharField(max_length=100)

    def __unicode__(self):
        return u"%s" % self.title


class CODTransaction(models.Model):
    transaction = models.ForeignKey(CODAction, on_delete=models.PROTECT)
    created_by_user = models.ForeignKey(User, related_name='created_by_user')
    created_time_stamp = models.DateTimeField(auto_now_add=True)
    verified_by_user = models.ForeignKey(User, blank=True, null=True, related_name='verified_by_user')
    verified_time_stamp = models.DateTimeField(blank=True, null=True)
    location = models.ForeignKey(Location, blank=True, null=True)
    remarks = models.CharField(max_length=500, blank=True)

    INITIATED = 'INITIATED'
    VERIFIED = 'VERIFIED'
    DECLINED = 'DECLINED'

    TRANSACTION_STATUS_CHOICES = (
            (INITIATED, 'INITIATED'),
            (VERIFIED, 'VERIFIED'),
            (DECLINED, 'DECLINED')
            )

    transaction_status = models.CharField(max_length=30, choices=TRANSACTION_STATUS_CHOICES, default=INITIATED)

    transaction_uuid = models.CharField(max_length=500)
    dg_id = models.IntegerField(blank=True, null=True, auto_created=False)
    dg_tl_id = models.IntegerField(blank=True, null=True, auto_created=False)
    cod_amount = models.FloatField(default=0.0)
    deliveries = models.CommaSeparatedIntegerField(max_length=500)
    bank_deposit_proof = models.ForeignKey(ProofOfBankDeposit, blank=True, null=True, on_delete=models.PROTECT)
    vendor = models.ForeignKey(Vendor, blank=True, null=True, on_delete=models.PROTECT)
    utr_number = models.CharField(max_length=300, blank=True, null=True)
    salary_deduction = models.FloatField(default=0.0)

    def __unicode__(self):
        return u"%s - %s" % (self.id, self.transaction)


class OrderDeliveryStatus(models.Model):
    date = models.DateTimeField()
    order = models.ForeignKey(Order, related_name = 'order', blank = True, null = True, on_delete=models.PROTECT)
    
    pickedup_datetime = models.DateTimeField(blank = True, null = True)
    completed_datetime = models.DateTimeField(blank = True, null = True)

    pickup_guy = models.ForeignKey(DeliveryGuy, related_name = 'pickup_dg', blank = True, null = True, on_delete=models.PROTECT)
    delivery_guy = models.ForeignKey(DeliveryGuy, related_name = 'assigned_dg', blank = True, null = True, on_delete=models.PROTECT)
    
    rejection_reason = models.CharField(max_length = 500, blank = True)
    is_cod_collected = models.BooleanField(default = False)
    
    is_reported = models.BooleanField(default = False)
    reported_reason = models.CharField(max_length = 500, blank = True)
    reported_solution = models.CharField(max_length = 500, blank = True)
    
    ORDER_PLACED = 'ORDER_PLACED'
    QUEUED = 'QUEUED'
    REJECTED = 'REJECTED'
    PICKUPATTEMPTED = 'PICKUPATTEMPTED'
    INTRANSIT = 'INTRANSIT'
    DELIVERYATTEMPTED = 'DELIVERYATTEMPTED'
    DELIVERED = 'DELIVERED'
    CANCELLED = 'CANCELLED'
    OUTFORDELIVERY = 'OUTFORDELIVERY'
    
    ORDER_CHOICES = (
        (ORDER_PLACED, 'ORDER_PLACED'),
        (REJECTED, 'REJECTED'),
        (QUEUED, 'QUEUED'),
        (PICKUPATTEMPTED, 'PICKUPATTEMPTED'),
        (INTRANSIT, 'INTRANSIT'),
        (OUTFORDELIVERY, 'OUTFORDELIVERY'),
        (DELIVERYATTEMPTED, 'DELIVERYATTEMPTED'),
        (DELIVERED, 'DELIVERED'),
        (CANCELLED, 'CANCELLED'),
    )
    order_status = models.CharField(max_length = 50, choices = ORDER_CHOICES, default = QUEUED)

    DOOR_STEP = 'DOOR_STEP'
    SECURITY = 'SECURITY'
    RECEPTION = 'RECEPTION'
    CUSTOMER = 'CUSTOMER'
    NONE = 'NONE'
    DELIVERED_AT_CHOICES = (
        (DOOR_STEP, 'DOOR_STEP'),
        (SECURITY, 'SECURITY'),
        (RECEPTION, 'RECEPTION'),
        (CUSTOMER, 'CUSTOMER'),
        (NONE, 'NONE'),
    )
    delivered_at = models.CharField(max_length = 15, choices = DELIVERED_AT_CHOICES, default = NONE)
    
    pickup_proof = models.ForeignKey(ProofOfDelivery, related_name = 'pickup_pod', blank = True, null = True, on_delete=models.PROTECT)
    delivery_proof = models.ForeignKey(ProofOfDelivery, related_name = 'delivery_pod', blank = True, null = True, on_delete=models.PROTECT)

    cod_collected_amount = models.FloatField(default = 0.0)
    cod_remarks = models.CharField(max_length = 500, blank = True)
    delivery_transactions = models.ManyToManyField(DeliveryTransaction, blank = True)

    COD_NOT_AVAILABLE = 'COD_NOT_AVAILABLE'
    COD_COLLECTED = 'COD_COLLECTED'
    COD_TRANSFERRED_TO_TL = 'COD_TRANSFERRED_TO_TL'
    COD_BANK_DEPOSITED = 'COD_BANK_DEPOSITED'
    COD_VERIFIED = 'COD_VERIFIED'
    COD_TRANSFERRED_TO_CLIENT = 'COD_TRANSFERRED_TO_CLIENT'

    COD_CHOICES = (
        (COD_NOT_AVAILABLE,'COD_NOT_AVAILABLE'),
        (COD_COLLECTED, 'COD_COLLECTED'),
        (COD_TRANSFERRED_TO_TL, 'COD_TRANSFERRED_TO_TL'),
        (COD_BANK_DEPOSITED, 'COD_BANK_DEPOSITED'),
        (COD_VERIFIED, 'COD_VERIFIED'),
        (COD_TRANSFERRED_TO_CLIENT, 'COD_TRANSFERRED_TO_CLIENT')
    )
    cod_status = models.CharField(max_length=100, choices=COD_CHOICES, default=COD_NOT_AVAILABLE)
    cod_transactions = models.ManyToManyField(CODTransaction, blank=True)
    bank_deposit_proof = models.ForeignKey(ProofOfBankDeposit, blank=True, null=True, on_delete=models.PROTECT)


    def __unicode__(self):
        return u"%s - %s" % (self.id, self.order)