from django.contrib import admin

# Register your models here.
from models import Address, Area, OrderItem, Order, OrderDeliveryStatus, DeliveryGuy, DGAttendance, Employee, Industry, Vendor, VendorAgent, VendorAccount, Consumer, Group, UserGroup, Suggestion, Message, Account, Product, ProductCategory

admin.site.register(Address)
admin.site.register(Area)

admin.site.register(DeliveryGuy)
admin.site.register(DGAttendance)

admin.site.register(Industry)
admin.site.register(Vendor)
admin.site.register(VendorAgent)
admin.site.register(VendorAccount)

admin.site.register(Consumer)

admin.site.register(Order)
admin.site.register(OrderDeliveryStatus)

admin.site.register(Product)
admin.site.register(ProductCategory)
admin.site.register(OrderItem)
admin.site.register(Employee)

# admin.site.register(UserGroup)
# admin.site.register(Group)
# admin.site.register(Suggestion)
# admin.site.register(Message)
# admin.site.register(Account)