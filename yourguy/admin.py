from django.contrib import admin

# Register your models here.
from yourguy.models import Address, Area,OrderItem, Order, OrderDeliveryStatus,Product, ProductCategory, DeliveryGuy, \
    DeliveryTeamLead, DGAttendance, Employee, Vendor, VendorAgent, Industry, VendorAccount, Consumer, ProofOfDelivery, \
    Picture, TimeSlot, Location, ServiceableCity, ServiceablePincode, NotificationType, Notification, DeliveryAction, \
    DeliveryTransaction, CODAction, CODTransaction, ProofOfBankDeposit


admin.site.register(TimeSlot)

admin.site.register(Address)
admin.site.register(Area)

class DeliveryGuyAdmin(admin.ModelAdmin):
	raw_id_fields = ['user','notifications','profile_picture']
admin.site.register(DeliveryGuy, DeliveryGuyAdmin)

admin.site.register(DGAttendance)

admin.site.register(Industry)

class VendorAdmin(admin.ModelAdmin):
    raw_id_fields = ['addresses','approved_by','pickup_boy']
admin.site.register(Vendor, VendorAdmin)


class VendorAgentAdmin(admin.ModelAdmin):
    raw_id_fields = ['user','notifications','profile_picture']
admin.site.register(VendorAgent, VendorAgentAdmin)

admin.site.register(VendorAccount)

class ConsumerAdmin(admin.ModelAdmin):
    raw_id_fields = ['addresses']
admin.site.register(Consumer, ConsumerAdmin)

class OrderAdmin(admin.ModelAdmin):
    raw_id_fields = ('vendor','consumer','order_items','pickup_address','delivery_address','created_by_user')
admin.site.register(Order, OrderAdmin)

class DeliveryStatusAdmin(admin.ModelAdmin):
    raw_id_fields = ('order','pickup_guy','delivery_guy','pickup_proof','delivery_proof', 'delivery_transactions')
admin.site.register(OrderDeliveryStatus, DeliveryStatusAdmin)

admin.site.register(Product)
admin.site.register(ProductCategory)
admin.site.register(OrderItem)

class EmployeeAdmin(admin.ModelAdmin):
    raw_id_fields = ['user','notifications','profile_picture']
admin.site.register(Employee, EmployeeAdmin)

admin.site.register(Picture)

class ProofOfDeliveryAdmin(admin.ModelAdmin):
	raw_id_fields = ['signature','pictures']
admin.site.register(ProofOfDelivery, ProofOfDeliveryAdmin)

admin.site.register(ServiceableCity)
admin.site.register(ServiceablePincode)

admin.site.register(DeliveryTeamLead)
admin.site.register(NotificationType)
admin.site.register(Notification)
admin.site.register(DeliveryAction)
admin.site.register(DeliveryTransaction)
admin.site.register(CODAction)
admin.site.register(CODTransaction)
admin.site.register(ProofOfBankDeposit)
