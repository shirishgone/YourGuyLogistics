VENDOR = 'vendor'
CONSUMER = 'consumer'
OPERATIONS = 'operations'
SALES = 'sales'
DELIVERY_GUY = 'deliveryguy'

OPS_PHONE_NUMBER = '+919820252216'
FROM_MAIL_ID = 'hi@yourguy.in'
TO_EMAIL_IDS = ['tech@yourguy.in','alay@yourguy.in', 'sameet@yourguy.in', 'winston@yourguy.in']

GCM_PUSH_API_KEY = 'AIzaSyBTWgr5O4ooWYoFTryEii2xkyP9qRahWPo'
GCM_SENDER_ID = '943077519707'

URL_EXPIRY_TIME = 300 #300 seconds

SALES_EMAIL = ['sameet@yourguy.in', 'winston@yourguy.in']

EMAIL_SIGNATURE = "- \n Team YourGuy \nhttp://www.yourguy.in"

SMS_URL = "http://api.smscountry.com/SMSCwebservice_bulk.aspx?User=yourguy&passwd=yourguydotin&mobilenumber={mobile_number}&message={message_text}&sid=YOURGY&mtype=N&DR=Y"

ORDER_PLACED_MESSAGE_OPS = 'A New order with order id {} has been placed by {}, please assign a DG.'
ORDER_PLACED_MESSAGE_CLIENT = 'Your order with order id {} has been placed and will be processed soon - Team YourGuy'
ORDER_DELIVERED_MESSAGE_CLIENT = 'Your order has been {} to {} at {} - Team YourGuy'
ORDER_APPROVED_MESSAGE_CLIENT = 'Your order for {} has been approved & QUEUED for delivery - Team YourGuy'
ORDER_REJECTED_MESSAGE_CLIENT = 'Your order for {} has been rejected because of {} - Team YourGuy'
ORDER_RESCHEDULED_MESSAGE_CLIENT = 'Your order for {} with order no {} has been rescheduled to {} - Team YourGuy'
ORDER_CANCELLED_MESSAGE_CLIENT = 'Your order for {} with order no {} has been cancelled - Team YourGuy'

VENDOR_ACCOUNT_REQUESTED_MESSAGE_SALES = "A New Vendor has requested for an account. \nPlease find the below details: \nStore Name:{} \nPhone Number: {} \nEmail: {} \nAddress : {}, {}, {}, {} \nApproval link:{}"
VENDOR_ACCOUNT_APPROVED_MESSAGE = 'Your account has been approved. \n http://app.yourguy.in \nPlease login using following credentials: \nUsername:{} \nPassword:{} - Team YourGuy'
VENDOR_ACCOUNT_APPROVED_MESSAGE_SALES = 'YourGuy: An account has been created for {} and credentials are sent via SMS and Email.'

ORDER_STATUS_PLACED = 'ORDER_PLACED'
ORDER_STATUS_QUEUED = 'QUEUED'
ORDER_STATUS_REJECTED = 'REJECTED'
ORDER_STATUS_OUTFORPICKUP = 'OUTFORPICKUP'
ORDER_STATUS_INTRANSIT = 'INTRANSIT'
ORDER_STATUS_OUTFORDELIVERY = 'OUTFORDELIVERY'
ORDER_STATUS_DELIVERED = 'DELIVERED'
ORDER_STATUS_ATTEMPTED = 'ATTEMPTED'
ORDER_STATUS_NOT_DELIVERED = 'NOT_DELIVERED'
ORDER_STATUS_CANCELLED = 'CANCELLED'


DG_STATUS_WORKING = 'WORKING'
DG_STATUS_LEAVE = 'LEAVE'
DG_STATUS_UNKNOWN = 'UNKNOWN'
DG_STATUS_AVAILABLE = 'AVAILABLE'
DG_STATUS_UN_AVAILABLE = 'UN_AVAILABLE'
DG_STATUS_BUSY = 'BUSY'


