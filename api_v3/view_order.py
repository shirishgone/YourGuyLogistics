import json
import time
from datetime import datetime
from itertools import chain

import pytz
from dateutil.rrule import rrule, WEEKLY
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from rest_framework import status, authentication, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api_v3 import constants
from api_v3.push import send_push
from api_v3.utils import log_exception, send_sms, ist_datetime, user_role, address_string, ist_day_start, ist_day_end, \
    paginate, is_correct_pincode, is_pickup_time_acceptable, timedelta, is_userexists, is_consumerexists, \
    is_consumer_has_same_address_already, days_in_int, send_email, is_today_date, is_vendor_has_same_address_already, \
    delivery_actions, ops_manager_for_dg, notification_type_for_code, ops_executive_for_pincode, address_with_location, \
    response_access_denied, response_incomplete_parameters

from yourguy.models import User, Vendor, DeliveryGuy, VendorAgent, Picture, ProofOfDelivery, OrderDeliveryStatus, \
    Consumer, Address, Order, Product, OrderItem, Notification, Location, DeliveryTransaction

from api_v3.cron_jobs import create_notif_for_no_ops_exec_for_pincode

def add_action_for_delivery(action, delivery, user, latitude, longitude, timestamp, remarks):
    delivery_transaction = DeliveryTransaction.objects.create(action=action, by_user=user,
        time_stamp=timestamp)
    if latitude is not None and longitude is not None:
        pickedup_location = Location.objects.create(latitude=latitude, longitude=longitude)
        delivery_transaction.location = pickedup_location
    if remarks is not None:
        delivery_transaction.remarks = remarks
    delivery_transaction.save()
    delivery.delivery_transactions.add(delivery_transaction)
    delivery.save()

def is_deliveryguy_assigned(delivery):
    if delivery.delivery_guy is not None:
        return True
    else:
        return False    

def notif_unassigned(delivery):
    pincode = delivery.order.delivery_address.pin_code
    ops_execs = ops_executive_for_pincode(pincode)
    if len(ops_execs) > 0:
        notification_type = notification_type_for_code(constants.NOTIFICATION_CODE_UNASSIGNED)
        for ops_manager in ops_execs:
            notification_message = constants.NOTIFICATION_MESSAGE_ORDER_PICKEUP_WITHOUT_DELIVERYGUY_ASSIGNED%(ops_manager.user.first_name, delivery.id, delivery.pickup_guy.user.first_name)
            new_notification = Notification.objects.create(notification_type = notification_type, 
                delivery_id = delivery.id, message = notification_message)
            ops_manager.notifications.add(new_notification)
            ops_manager.save()
    else:
        create_notif_for_no_ops_exec_for_pincode(pincode)

def send_reported_email(user, email_orders, reported_reason):
    subject = '%s Reported Issue'% (user.first_name)
    body = 'Hello,\n\n%s has reported an issue about the following orders. \n\nIssue: %s\n'% (user.first_name, reported_reason)
    for email_order in email_orders:
        string = '\nOrder no: %s | Client Name: %s | Customer Name: %s'% (email_order['delivery_id'], email_order['vendor'], email_order['customer_name'])
        body = body + string
    
    body = body + '\n\nThanks \n-YourGuy BOT'
    send_email(constants.EMAIL_REPORTED_ORDERS, subject, body)

def send_cod_discrepency_email(delivery_status, user):
    try:
        if float(delivery_status.order.cod_amount) > 0.0 and delivery_status.cod_collected_amount is not None and (float(delivery_status.cod_collected_amount) < float(delivery_status.order.cod_amount) or float(delivery_status.cod_collected_amount) > float(delivery_status.order.cod_amount) ):
            subject = 'COD discrepancy with order: %s' % delivery_status.id
            body = 'Hello Ops,'
            body = body + '\n\nThere is some discrepancy in COD collection for following order.'
            body = body + '\n\nOrder no: %s' % (delivery_status.id)
            body = body + '\nVendor: %s' % (delivery_status.order.vendor.store_name)
            body = body + '\nCustomer name: %s' % (delivery_status.order.consumer.user.first_name)
            body = body + '\nCOD to be collected: %s' % (delivery_status.order.cod_amount)
            body = body + '\nCOD collected: %s' % (delivery_status.cod_collected_amount)
            body = body + '\nDeliveryGuy: %s'% (user.first_name)
            body = body + '\nReason added: %s'% (delivery_status.cod_remarks)
            body = body + '\n\nPlease clear the discrepancy with the DeliveryBoy and Vendor soon.'
            body = body + '\n\n- Thanks \nYourGuy BOT'            
            send_email(constants.EMAIL_COD_DISCREPENCY, subject, body)
    except Exception as e:
        log_exception(e, 'order_delivered COD discrepancy email')

def retail_order_send_email(vendor, new_delivery_ids):
    client_name = vendor.store_name
    subject = '[Retail] New Orders placed by %s'% (client_name)
    delivery_ids = ' , '.join(str(delivery_id) for delivery_id in new_delivery_ids)
    body = 'Hello,\n\n%s has placed few orders.\n\nOrder Nos: %s \n\n Please check' % (client_name, delivery_ids)
    body = body + '\n\nThanks \n-YourGuy BOT'
    send_email(constants.RETAIL_EMAIL_ID, subject, body)

def can_update_delivery_status(delivery_status):
    if delivery_status.order_status == constants.ORDER_STATUS_PLACED or delivery_status.order_status == constants.ORDER_STATUS_QUEUED:
        return True
    else:
        return False

def fetch_consumer(consumer_phone_number, consumer_name, vendor):
    # CREATING USER & CONSUMER IF DOESNT EXISTS ------------------------
    if is_userexists(consumer_phone_number) is True:
        user = get_object_or_404(User, username=consumer_phone_number)
        if is_consumerexists(user) is True:
            consumer = get_object_or_404(Consumer, user=user)
        else:
            consumer = Consumer.objects.create(user=user)
            consumer.associated_vendor.add(vendor)
    else:
        user = User.objects.create(username=consumer_phone_number, first_name=consumer_name, password='')
        consumer = Consumer.objects.create(user=user)
        consumer.associated_vendor.add(vendor)
    # ---------------------------------------------------
    return consumer


def fetch_consumer_address(consumer, full_address, pincode, landmark):
    address = is_consumer_has_same_address_already(consumer, pincode)
    if address is None:
        address = Address.objects.create(pin_code=pincode)
        if full_address is not None:
            address.full_address = full_address
        if landmark is not None:
            address.landmark = landmark
        address.save()
        consumer.addresses.add(address)
    return address


def fetch_vendor_address(vendor, full_address, pincode, landmark):
    address = is_vendor_has_same_address_already(vendor, pincode)
    if address is None:
        address = Address.objects.create(pin_code=pincode)
        if full_address is not None:
            address.full_address = full_address
        if landmark is not None:
            address.landmark = landmark
        address.save()
        vendor.addresses.add(address)
    return address


def send_dg_notification(dg, delivery_ids):
    try:
        data = {
            'message': 'A new order has been assigned to you.',
            'type': 'order_assigned',
            'data': {
                'delivery_id': delivery_ids
            }
        }
        send_push(dg.device_token, data)
    except Exception as e:
        log_exception(e, 'Push notification not sent in order assignment')


def send_sms_to_dg_about_mass_orders(dg, delivery_ids):    
    try:
        message = 'New Orders are assigned to you. Order IDs: {}'.format(delivery_ids)
        send_sms(dg.user.username, message)
    except Exception as e:
        log_exception(e, 'Mass Order assignment SMS failed')


def send_sms_to_dg_about_order(date, dg, delivery_status):
    try:
        pickup_date_string = date.strftime("%b%d")
        ist_date_time = ist_datetime(delivery_status.order.pickup_datetime)
        pickup_time_string = ist_date_time.time().strftime("%I:%M%p")
        pickup_total_string = "%s,%s" % (pickup_date_string, pickup_time_string)
        message = 'New Order:{},Pickup:{},Client:{},Cust:{},{},{},COD:{}'.format(delivery_status.id,
                                                                                 pickup_total_string,
                                                                                 delivery_status.order.vendor.store_name,
                                                                                 delivery_status.order.consumer.user.first_name,
                                                                                 delivery_status.order.consumer.user.username,
                                                                                 delivery_status.order.delivery_address,
                                                                                 delivery_status.order.cod_amount)
        send_sms(dg.user.username, message)
    except Exception as e:
        log_exception(e, 'Order assignment Single SMS failed')

def is_user_permitted_to_cancel_order(user, order):
    is_permissible = False
    role = user_role(user)
    if role == constants.VENDOR:
        vendor_agent = get_object_or_404(VendorAgent, user=user)
        vendor = vendor_agent.vendor
        if order.vendor == vendor:
            is_permissible = True
    elif (role == constants.OPERATIONS) or (role == constants.DELIVERY_GUY):
        is_permissible = False
    return is_permissible

def is_user_permitted_to_update_order(user, order):
    is_permissible = False
    role = user_role(user)
    if role == constants.VENDOR:
        is_permissible = False
    elif (role == constants.OPERATIONS) or (role == constants.DELIVERY_GUY):
        is_permissible = True
    return is_permissible

def is_user_permitted_to_edit_order(user, order):
    is_permissible = False
    role = user_role(user)
    if role == constants.VENDOR:
        vendor_agent = get_object_or_404(VendorAgent, user=user)
        vendor = vendor_agent.vendor
        if order.vendor == vendor:
            is_permissible = True
    elif (role == constants.OPERATIONS) or (role == constants.DELIVERY_GUY):
        is_permissible = False
    return is_permissible

def can_update_order(delivery_status, status):
    if status == constants.ORDER_STATUS_INTRANSIT:
        if delivery_status.order_status == constants.ORDER_STATUS_QUEUED:
            return True
        else:
            return False
    elif status == constants.ORDER_STATUS_DELIVERED:
        if delivery_status.order_status == constants.ORDER_STATUS_INTRANSIT:
            return True
        else:
            return False
    elif status == constants.ORDER_STATUS_PICKUP_ATTEMPTED:
        if delivery_status.order_status == constants.ORDER_STATUS_QUEUED:
            return True
        else:
            return False
    elif status == constants.ORDER_STATUS_CANCELLED:
        if delivery_status.order_status == constants.ORDER_STATUS_QUEUED:
            return True
        else:
            return False
    elif status == constants.ORDER_STATUS_DELIVERY_ATTEMPTED:
        if delivery_status.order_status == constants.ORDER_STATUS_INTRANSIT:
            return True
        else:
            return False
    else:
        return False


def delivery_status_of_the_day(order, date):
    delivery_item = None
    for delivery_status in order.delivery_status.all():
        if date.date() == delivery_status.date.date():
            delivery_item = delivery_status
            break
    return delivery_item


def create_proof(proof_dict):
    try:
        if proof_dict is not None:
            receiver_name = proof_dict['receiver_name']
            signature_name = proof_dict['signature']
            pictures = proof_dict['image_names']

            signature = Picture.objects.create(name=signature_name)
            proof = ProofOfDelivery.objects.create(receiver_name=receiver_name, signature=signature)
            for picture in pictures:
                proof.pictures.add(Picture.objects.create(name=picture))
                proof.save()
            return proof
    except Exception as e:
        log_exception(e, 'create_proof')
        return None

# UPDATE DELIVERY STATUS -----------------------------------------------------------
def update_delivery_status_delivery_attempted(delivery_status, dg_remarks, attempted_datetime):
    delivery_status.order_status = constants.ORDER_STATUS_DELIVERY_ATTEMPTED
    delivery_status.completed_datetime = attempted_datetime
    if dg_remarks is not None:
        delivery_status.cod_remarks = dg_remarks
    delivery_status.save()


def update_delivery_status_pickup_attempted(delivery_status, dg_remarks, attempted_datetime):
    delivery_status.order_status = constants.ORDER_STATUS_PICKUP_ATTEMPTED
    delivery_status.pickedup_datetime = attempted_datetime
    if dg_remarks is not None:
        delivery_status.cod_remarks = dg_remarks
    delivery_status.save()


def update_delivery_status_pickedup(delivery_status, pickedup_datetime, proof, dg_remarks):
    delivery_status.order_status = constants.ORDER_STATUS_INTRANSIT
    delivery_status.pickedup_datetime = pickedup_datetime
    if proof is not None:
        delivery_status.pickup_proof = proof
    if dg_remarks is not None:
        delivery_status.cod_remarks = dg_remarks
    delivery_status.save()


def update_delivery_status_delivered(delivery_status, delivered_at, delivered_datetime, proof, delivery_remarks, cod_collected_amount):
    delivery_status.order_status = constants.ORDER_STATUS_DELIVERED
    delivery_status.delivered_at = delivered_at
    delivery_status.completed_datetime = delivered_datetime
    if proof is not None:
        delivery_status.delivery_proof = proof
    if delivery_remarks is not None:
        delivery_status.cod_remarks = delivery_remarks
    if cod_collected_amount is not None:
        delivery_status.cod_collected_amount = float(cod_collected_amount)
        delivery_status.is_cod_collected = True
    delivery_status.save()


# ---------------------------------------------------------------------------
# Dictionary methods used in other functions

def common_params(delivery_status):
    res_order = {}
    
    if delivery_status.order.pickup_datetime is not None:
        new_pickup_datetime = datetime.combine(delivery_status.date, delivery_status.order.pickup_datetime.time())
        res_order['pickup_datetime'] = pytz.utc.localize(new_pickup_datetime)
    else:
        res_order['pickup_datetime'] = None
    
    if delivery_status.order.delivery_datetime is not None:
        new_delivery_datetime = datetime.combine(delivery_status.date,
                                                 delivery_status.order.delivery_datetime.time())
        res_order['delivery_datetime'] = pytz.utc.localize(new_delivery_datetime)    
    else:
        res_order['delivery_datetime'] = None

    if delivery_status.pickup_guy is not None:
        res_order['pickupguy_id'] = delivery_status.pickup_guy.id
        res_order['pickupguy_name'] = delivery_status.pickup_guy.user.first_name
        res_order['pickupguy_phonenumber'] = delivery_status.pickup_guy.user.username
    else:
        res_order['pickupguy_id'] = None
        res_order['pickupguy_name'] = None
        res_order['pickupguy_phonenumber'] = None

    if delivery_status.delivery_guy is not None:
        res_order['deliveryguy_id'] = delivery_status.delivery_guy.id
        res_order['deliveryguy_name'] = delivery_status.delivery_guy.user.first_name
        res_order['deliveryguy_phonenumber'] = delivery_status.delivery_guy.user.username
    else:
        res_order['deliveryguy_id'] = None
        res_order['deliveryguy_name'] = None
        res_order['deliveryguy_phonenumber'] = None

    order_items_array = []
    for order_item in delivery_status.order.order_items.all():
        order_item_obj = dict()
        order_item_obj['product_name'] = order_item.product.name
        order_item_obj['quantity'] = order_item.quantity
        order_item_obj['cost'] = order_item.cost
        order_items_array.append(order_item_obj)

    res_order['order_items'] = order_items_array
    return res_order

def delivery_guy_app(delivery_status):
    if delivery_status is not None:

        res_order = {
            'id': delivery_status.id,
            'pickup_address': address_with_location(delivery_status.order.pickup_address),
            'delivery_address': address_with_location(delivery_status.order.delivery_address),
            'status': delivery_status.order_status,
            'is_reverse_pickup': delivery_status.order.is_reverse_pickup,
            'is_reported': delivery_status.is_reported,
            'reported_reason': delivery_status.reported_reason,
            'cod_amount': delivery_status.order.cod_amount,
            'cod_collected_amount': delivery_status.cod_collected_amount,
            'customer_name': delivery_status.order.consumer.user.first_name,
            'customer_phonenumber': delivery_status.order.consumer.user.username,
            'vendor_name': delivery_status.order.vendor.store_name,
            'delivered_at': delivery_status.delivered_at,
            'pickedup_datetime': delivery_status.pickedup_datetime,
            'completed_datetime': delivery_status.completed_datetime,
            'notes': delivery_status.order.notes,
            'vendor_order_id': delivery_status.order.vendor_order_id,
            'vendor_phonenumber': delivery_status.order.vendor.phone_number,
            'total_cost': delivery_status.order.total_cost,
            'cod_remarks': delivery_status.cod_remarks,
            'delivery_charges': delivery_status.order.delivery_charges
        }
        res_order.update(common_params(delivery_status))
        return res_order
    else:
        return None


def webapp_list(delivery_status):
    if delivery_status is not None:

        res_order = {
            'id': delivery_status.id,
            'pickup_address': address_string(delivery_status.order.pickup_address),
            'delivery_address': address_string(delivery_status.order.delivery_address),
            'status': delivery_status.order_status,
            'is_recurring': delivery_status.order.is_recurring,
            'is_reported': delivery_status.is_reported,
            'reported_reason': delivery_status.reported_reason,
            'cod_amount': delivery_status.order.cod_amount,
            'cod_collected_amount': delivery_status.cod_collected_amount,
            'customer_name': delivery_status.order.consumer.user.first_name,
            'vendor_name': delivery_status.order.vendor.store_name,
            'delivered_at': delivery_status.delivered_at,
            'is_reverse_pickup': delivery_status.order.is_reverse_pickup
        }
        res_order.update(common_params(delivery_status))
        return res_order
    else:
        return None

def dg_created_orders(delivery):
    result = {
    'id': delivery.id,
    'customer_name': delivery.order.consumer.user.first_name
    }
    return result

def webapp_details(delivery_status):
    if delivery_status.order.pickup_datetime is not None:
        new_pickup_datetime = datetime.combine(delivery_status.date, delivery_status.order.pickup_datetime.time())
        new_pickup_datetime = pytz.utc.localize(new_pickup_datetime)
    else:
        new_pickup_datetime = None

    if delivery_status.order.delivery_datetime is not None:
        new_delivery_datetime = datetime.combine(delivery_status.date, delivery_status.order.delivery_datetime.time())
        new_delivery_datetime = pytz.utc.localize(new_delivery_datetime)
    else:
        new_delivery_datetime = None

    res_order = {
        'id': delivery_status.id,
        'pickup_datetime': new_pickup_datetime,
        'delivery_datetime': new_delivery_datetime,
        'pickup_address': address_string(delivery_status.order.pickup_address),
        'delivery_address': address_string(delivery_status.order.delivery_address),
        'status': delivery_status.order_status,
        'customer_name': delivery_status.order.consumer.user.first_name,
        'is_reported': delivery_status.is_reported,
        'reported_reason': delivery_status.reported_reason,
        'vendor_id': delivery_status.order.vendor.id,
        'vendor_name': delivery_status.order.vendor.store_name,
        'vendor_order_id': delivery_status.order.vendor_order_id,
        'cod_amount': delivery_status.order.cod_amount,
        'customer_phonenumber': delivery_status.order.consumer.user.username,
        'notes': delivery_status.order.notes,
        'total_cost': delivery_status.order.total_cost
    }
    res_order.update(delivery_status)
    return res_order


def search_order(user, search_query):
    role = user_role(user)
    delivery_status_queryset = []
    if role == constants.VENDOR:
        vendor_agent = get_object_or_404(VendorAgent, user=user)
        vendor = vendor_agent.vendor
        delivery_status_queryset = OrderDeliveryStatus.objects.filter(order__vendor=vendor)
        if search_query.isdigit():
            delivery_status_queryset = delivery_status_queryset.filter(
                Q(id=search_query) |
                Q(order__consumer__user__username=search_query) |
                Q(order__vendor_order_id=search_query))
        else:
            delivery_status_queryset = delivery_status_queryset.filter(
                Q(order__consumer__user__first_name__icontains=search_query) |
                Q(order__vendor_order_id=search_query))

    elif role == constants.OPERATIONS or role == constants.SALES:
        if search_query.isdigit():
            delivery_status_queryset = OrderDeliveryStatus.objects.filter(
                Q(id=search_query) |
                Q(order__consumer__user__username=search_query) |
                Q(order__vendor_order_id=search_query))
        else:
            delivery_status_queryset = OrderDeliveryStatus.objects.filter(
                Q(order__consumer__user__first_name__icontains=search_query) |
                Q(order__vendor_order_id=search_query))
    else:
        pass
    return delivery_status_queryset


class OrderViewSet(viewsets.ViewSet):
    """
    Order viewset that provides the standard actions
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def destroy(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, pk=None):
        delivery_status = get_object_or_404(OrderDeliveryStatus, id=pk)

        # VENDOR PERMISSION CHECK ---------------------------------------------
        role = user_role(request.user)
        if role == constants.VENDOR:
            vendor_agent = get_object_or_404(VendorAgent, user=request.user)
            vendor = vendor_agent.vendor
            if delivery_status.order.vendor.id != vendor.id:
                return response_access_denied()                

        result = delivery_guy_app(delivery_status)
        return Response(result, status=status.HTTP_200_OK)

    def list(self, request):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `consumer_id` or 'vendor_id' query parameter in the URL.
        """
        vendor_id = request.QUERY_PARAMS.get('vendor_id', None)
        dg_phone_number = request.QUERY_PARAMS.get('dg_username', None)
        page = request.QUERY_PARAMS.get('page', None)
        date_string = request.QUERY_PARAMS.get('date', None)
        search_query = request.QUERY_PARAMS.get('search', None)
        filter_order_status = request.QUERY_PARAMS.get('order_status', None)
        filter_time_start = request.QUERY_PARAMS.get('time_start', None)
        filter_time_end = request.QUERY_PARAMS.get('time_end', None)
        is_cod = request.QUERY_PARAMS.get('is_cod', None)
        delivery_ids = request.QUERY_PARAMS.get('delivery_ids', None)

        # ORDER STATUS CHECK --------------------------------------------------
        order_statuses = []
        if filter_order_status is not None:
            order_statuses = filter_order_status.split(',')

        for order_status in order_statuses:
            if order_status == constants.ORDER_STATUS_PLACED \
                    or order_status == constants.ORDER_STATUS_QUEUED \
                    or order_status == constants.ORDER_STATUS_INTRANSIT \
                    or order_status == constants.ORDER_STATUS_PICKUP_ATTEMPTED \
                    or order_status == constants.ORDER_STATUS_DELIVERED \
                    or order_status == constants.ORDER_STATUS_DELIVERY_ATTEMPTED \
                    or order_status == constants.ORDER_STATUS_CANCELLED \
                    or order_status == constants.ORDER_STATUS_REJECTED:
                pass
            else:
                content = {
                    'error': 'Incorrect order_status',
                    'description': 'Options: QUEUED, INTRANSIT, PICKUPATTEMPTED, DELIVERED, DELIVERYATTEMPTED, CANCELLED'
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        # -------------------------------------------------------------------------

        # DATE FILTERING ----------------------------------------------------------
        if date_string is not None:
            date = parse_datetime(date_string)
        else:
            date = datetime.today()

        day_start = ist_day_start(date)
        day_end = ist_day_end(date)

        delivery_status_queryset = OrderDeliveryStatus.objects.filter(date__gte=day_start, date__lte=day_end)
        # --------------------------------------------------------------------------

        role = user_role(request.user)

        # DELIVERY GUY FILTERING ---------------------------------------------------
        delivery_guy = None
        if role == constants.DELIVERY_GUY:
            delivery_guy = get_object_or_404(DeliveryGuy, user=request.user)
            delivery_status_queryset = delivery_status_queryset.filter(Q(delivery_guy=delivery_guy) |
                                                                       Q(pickup_guy=delivery_guy))

        else:
            if dg_phone_number is not None:
                if dg_phone_number.isdigit():
                    user = get_object_or_404(User, username=dg_phone_number)
                    delivery_guy = get_object_or_404(DeliveryGuy, user=user)
                    delivery_status_queryset = delivery_status_queryset.filter(
                        Q(delivery_guy=delivery_guy) |
                        Q(pickup_guy=delivery_guy))
                elif dg_phone_number == 'UNASSIGNED_DELIVERY':
                    delivery_status_queryset = delivery_status_queryset.filter(Q(delivery_guy=None))
                elif dg_phone_number == 'UNASSIGNED_PICKUP':
                    delivery_status_queryset = delivery_status_queryset.filter(Q(pickup_guy=None))
                elif dg_phone_number == 'UNASSIGNED':
                    delivery_status_queryset = delivery_status_queryset.filter(Q(pickup_guy=None) &
                                                                               Q(delivery_guy=None))
        # --------------------------------------------------------------------------

        # VENDOR FILTERING ---------------------------------------------------------
        vendor = None
        if role == constants.VENDOR:
            vendor_agent = get_object_or_404(VendorAgent, user=request.user)
            vendor = vendor_agent.vendor
        else:
            if vendor_id is not None:
                vendor = get_object_or_404(Vendor, pk=vendor_id)

        if vendor is not None:
            delivery_status_queryset = delivery_status_queryset.filter(order__vendor=vendor)
        # ----------------------------------------------------------------------------

        # COD FILTERING --------------------------------------------------------------
        if is_cod is not None:
            is_cod_bool = json.loads(is_cod.lower())
            if is_cod_bool is True:
                delivery_status_queryset = delivery_status_queryset.filter(order__cod_amount__gt=0)
            else:
                delivery_status_queryset = delivery_status_queryset.filter(order__cod_amount=0)
        # ----------------------------------------------------------------------------

        # TIME SLOT FILTERING --------------------------------------------------------
        if filter_time_end is not None and filter_time_start is not None:
            filter_time_start = parse_datetime(filter_time_start)
            filter_time_end = parse_datetime(filter_time_end)
            delivery_status_queryset = delivery_status_queryset.filter(order__pickup_datetime__gte=filter_time_start,
                                                                       order__pickup_datetime__lte=filter_time_end)
        # ----------------------------------------------------------------------------

        # ORDER STATUS FILTERING ---------------------------------------------------
        if len(order_statuses) > 0:
            delivery_status_queryset = delivery_status_queryset.filter(order_status__in = order_statuses)
        # --------------------------------------------------------------------------

        # SEARCH KEYWORD FILTERING ---------------------------------------------------
        if search_query is not None:
            delivery_status_queryset = search_order(request.user, search_query)
        # ----------------------------------------------------------------------------

        # SPECIFIC ORDER IDs-----------------------------------------------------------
        if delivery_ids is not None:
            delivery_ids_array = delivery_ids.split(',')
            delivery_status_queryset = OrderDeliveryStatus.objects.filter(id__in=delivery_ids_array)
        # ----------------------------------------------------------------------------

        total_orders_count = len(delivery_status_queryset)
        unassigned_orders_count = delivery_status_queryset.filter(Q(pickup_guy = None) & Q(delivery_guy = None)).count()
        pending_orders_count = delivery_status_queryset.filter(Q(order_status = constants.ORDER_STATUS_INTRANSIT) | Q(order_status = constants.ORDER_STATUS_QUEUED)).count()

        if role == constants.DELIVERY_GUY:
            delivery_statuses = delivery_status_queryset
            result = []
            for single_delivery in delivery_statuses:
                delivery_status_dict = delivery_guy_app(single_delivery)
                if delivery_status_dict is not None:
                    result.append(delivery_status_dict)

            response_content = {
                "data": result,
                "total_pages": 1,
                "total_orders": total_orders_count
            }
            return Response(response_content, status=status.HTTP_200_OK)

        else:
            # PAGINATION  ----------------------------------------------------------------
            if page is not None:
                page = int(page)
            else:
                page = 1

            total_pages = int(total_orders_count / constants.PAGINATION_PAGE_SIZE) + 1
            if page > total_pages or page <= 0:
                response_content = {
                    "error": "Invalid page number"
                }
                return Response(response_content, status=status.HTTP_400_BAD_REQUEST)
            else:
                delivery_statuses = paginate(delivery_status_queryset, page)
            # ----------------------------------------------------------------------------

            # UPDATING DELIVERY STATUS OF THE DAY  ---------------------------------------
            result = []
            for single_delivery_status in delivery_statuses:
                delivery_status = webapp_list(single_delivery_status)
                if delivery_status is not None:
                    result.append(delivery_status)

            response_content = {
                "data": result,
                "total_pages": total_pages,
                "total_orders": total_orders_count,
                "unassigned_orders_count":unassigned_orders_count,
                "pending_orders_count":pending_orders_count
            }

            return Response(response_content, status=status.HTTP_200_OK)

    def create(self, request):
        role = user_role(self.request.user)
        if role == 'vendor':
            vendor_agent = get_object_or_404(VendorAgent, user=self.request.user)
            vendor = vendor_agent.vendor
        else:
            return response_access_denied()            
        
        # PARSING REQUEST PARAMS ------------------------
        try:
            order_date = request.data['order_date']
            timeslots = request.data['timeslots']

            product_id = request.data['product_id']
            product = get_object_or_404(Product, pk=product_id)

            consumers = request.data['consumers']

            vendor_address_id = request.data['vendor_address_id']
            vendor_address = get_object_or_404(Address, pk=vendor_address_id)
            is_reverse_pickup = request.data['is_reverse_pickup']
            
            cod_amount = request.data.get('cod_amount')
            notes = request.data.get('notes')
            vendor_order_id = request.data.get('vendor_order_id')
            total_cost = request.data.get('total_cost')

        except Exception as e:
            parameters = ['order_date', 'timeslots', 'customers', 'product_id', 'recurring', 'vendor_address_id', 'is_reverse_pickup', 'cod_amount(optional)', 'notes(optional)', 'total_cost(optional)', 'vendor_order_id(optional)']
            return response_incomplete_parameters([parameters])
        # ---------------------------------------------------

        # TIMESLOT PARSING -----------------------------------
        order_datetime = parse_datetime(order_date)
        try:
            timeslot_start = timeslots['timeslot_start']
            timeslot_end = timeslots['timeslot_end']
        except Exception as e:
            parameters = ['timeslot_start', 'timeslot_end']
            return response_incomplete_parameters([parameters])
        # ---------------------------------------------------

        # CREATING DATES OF DELIVERY ------------------------
        delivery_dates = []
        try:
            recurring = request.data['recurring']
            try:
                start_date_string = recurring['start_date']
                end_date_string = recurring['end_date']
                by_day = recurring['by_day']

                if start_date_string is not None:
                    start_date = parse_datetime(start_date_string)
                    end_date = parse_datetime(end_date_string)
                    int_days = days_in_int(by_day)

                    rule_week = rrule(WEEKLY, dtstart=start_date, until=end_date, byweekday=int_days)
                    delivery_dates = list(rule_week)

                # ACCEPTING ADDITIONAL DATES PARAM IN RECURRING ----------------
                additional_dates = recurring.get('additional_dates')
                if additional_dates is not None:
                    for additional_date in additional_dates:
                        delivery_dates.append(parse_datetime(additional_date))
                # ---------------------------------------------------

                if len(delivery_dates) <= 0:
                    content = {
                        'error': 'Incomplete dates',
                        'description': 'Please check the dates'
                    }
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                content = {
                    'error': 'Incomplete parameters',
                    'description': 'start_date, end_date, by_day should be mentioned for recurring events'
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except:
            delivery_dates.append(order_datetime)
        # --------------------------------------------------------------

        # CREATING NEW ORDER FOR EACH CUSTOMER -------------------------
        if len(consumers) == 0:
            content = {
                'status': 'No customers. Please provide customer details [id, address_id]'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        # --------------------------------------------------------------

        # CREATING NEW ORDER FOR EACH CUSTOMER -------------------------
        time_obj = time.strptime(timeslot_start, "%H:%M:%S")
        pickup_datetime = order_datetime.replace(hour=time_obj.tm_hour, minute=time_obj.tm_min)

        if is_pickup_time_acceptable(pickup_datetime) is False:
            content = {
                'error': 'Pickup date or time not acceptable',
                'description': 'Pickup time can only be between 5.30AM to 10.00PM and past dates are not allowed'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if vendor.is_hyper_local is True:
            delivery_timedelta = timedelta(hours = 1, minutes = 0)
            delivery_datetime = pickup_datetime + delivery_timedelta
        else:                                    
            delivery_timedelta = timedelta(hours = 4, minutes = 0)
            delivery_datetime = pickup_datetime + delivery_timedelta
        # --------------------------------------------------------------

        new_delivery_ids = []
        for cons in consumers:

            consumer_id = cons['id']
            consumer_address_id = cons['address_id']

            consumer = get_object_or_404(Consumer, pk=consumer_id)
            consumer_address = get_object_or_404(Address, pk=consumer_address_id)

            if is_reverse_pickup:
                pickup_adr = consumer_address
                delivery_adr = vendor_address
            else:
                pickup_adr = vendor_address
                delivery_adr = consumer_address

            try:
                new_order = Order.objects.create(created_by_user=request.user,
                                                 vendor=vendor,
                                                 consumer=consumer,
                                                 pickup_address=pickup_adr,
                                                 delivery_address=delivery_adr,
                                                 pickup_datetime=pickup_datetime,
                                                 delivery_datetime=delivery_datetime,
                                                 is_reverse_pickup=is_reverse_pickup)

            except Exception as e:
                print(e)
                content = {
                    'error': ' Error placing new order'
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            # ---------------------------------------------------

            # ADDING OPTIONAL ATTRIBUTES TO NEW ORDER CREATED ------------------
            if notes is not None:
                new_order.notes = notes

            if cod_amount is not None and float(cod_amount) > 0:
                new_order.is_cod = True
                new_order.cod_amount = float(cod_amount)

            if vendor_order_id is not None:
                new_order.vendor_order_id = vendor_order_id

            if total_cost is not None:
                new_order.total_cost = total_cost

            for date in delivery_dates:
                delivery_status = OrderDeliveryStatus.objects.create(date=date, order=new_order)
                new_delivery_ids.append(delivery_status.id)

            if len(delivery_dates) > 1:
                new_order.is_recurring = True

            # ORDER ITEMS ----------------------------------------
            order_item = OrderItem.objects.create(product=product, quantity=1)
            new_order.order_items.add(order_item)
            # -------------------------------------------------------------

            new_order.save()
        # -------------------------------------------------------------
        # SEND MAIL TO RETAIL TEAM, IF ITS A RETAIL ORDER
        if vendor.is_retail is True and len(new_delivery_ids)> 0:
            retail_order_send_email(vendor, new_delivery_ids)
        # -------------------------------------------------------------

        # FINAL RESPONSE ----------------------------------------------
        if len(new_delivery_ids) > 0:
            content = {
                'status': 'orders added',
                'delivery_ids': new_delivery_ids
            }
            return Response(content, status=status.HTTP_201_CREATED)
        else:
            content = {
                'status': 'There is some problem adding orders, please try again.'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
            # -------------------------------------------------------------

    @detail_route(methods=['post'])
    def upload_excel(self, request, pk):
        # VENDOR ONLY ACCESS CHECK ------------------------------------
        role = user_role(self.request.user)
        if role == constants.VENDOR:
            vendor_agent = get_object_or_404(VendorAgent, user = self.request.user)
            vendor = vendor_agent.vendor
        else:
            return response_access_denied()            
        try:
            pickup_address_id = request.data['pickup_address_id']
            orders = request.data['orders']
        except Exception as e:
            content = {
                'error': 'Incomplete params. pickup_address_id, orders'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        new_delivery_ids = []
        for single_order in orders:
            try:
                pickup_datetime = single_order['pickup_datetime']
                vendor_order_id = single_order['vendor_order_id']

                # Optional ------------------------------------
                cod_amount = single_order.get('cod_amount')
                
                # Customer details ------------------------------------
                consumer_name = single_order['customer_name']
                consumer_phone_number = single_order['customer_phone_number']
                
                # Delivery address ------------------------------------
                delivery_full_address = single_order['customer_full_address']
                delivery_pin_code = single_order['customer_pincode']
                delivery_landmark = single_order.get('customer_landmark')
                
                is_reverse_pickup = single_order.get('is_reverse_pickup')
                is_reverse_pickup = is_reverse_pickup.lower()
                if is_reverse_pickup == 'false':
                    is_reverse_pickup = False
                else:
                    is_reverse_pickup = True    

                total_cost = single_order.get('total_cost')
                notes = single_order.get('notes')

                # PINCODE IS INTEGER CHECK -----------------------------
                if is_correct_pincode(delivery_pin_code) is False:
                    content = {'error':'Incorrect pin_code', 
                    'description':'Pincode should be an integer with 6 digits.'}
                    return Response(content, status = status.HTTP_400_BAD_REQUEST)
            
            except Exception, e:
                content = {
                'error':'Incomplete params', 
                'description':'pickup_datetime, customer_name, customer_phone_number, pickup address id , delivery address'
                }
                return Response(content, status = status.HTTP_400_BAD_REQUEST)

            try:
                pickup_datetime = parse_datetime(pickup_datetime)
                if is_pickup_time_acceptable(pickup_datetime) is False:
                    content = {
                    'error':'Pickup date or time not acceptable', 
                    'description':'Pickup time can only be between 5.30AM to 10.00PM and past dates are not allowed'
                    }
                    return Response(content, status = status.HTTP_400_BAD_REQUEST)

                if vendor.is_hyper_local is True:
                    delivery_timedelta = timedelta(hours = 1, minutes = 0)
                    delivery_datetime = pickup_datetime + delivery_timedelta
                else:                                    
                    delivery_timedelta = timedelta(hours = 4, minutes = 0)
                    delivery_datetime = pickup_datetime + delivery_timedelta

            except Exception, e:
                content = {'error':'Error parsing dates'}
                return Response(content, status = status.HTTP_400_BAD_REQUEST)
            
            try:
                if is_userexists(consumer_phone_number) is True:
                    user = get_object_or_404(User, username = consumer_phone_number)
                    if is_consumerexists(user) is True:
                        consumer = get_object_or_404(Consumer, user = user)
                    else:
                        consumer = Consumer.objects.create(user = user)
                        consumer.associated_vendor.add(vendor)
                else:
                    user = User.objects.create(username = consumer_phone_number, first_name = consumer_name, password = '')
                    consumer = Consumer.objects.create(user = user)
                    consumer.associated_vendor.add(vendor)
                
                # ADDRESS CHECK ----------------------------------
                try:
                    if is_reverse_pickup is True:
                        pickup_address = fetch_consumer_address(consumer, delivery_full_address, delivery_pin_code, delivery_landmark)
                        delivery_address = get_object_or_404(Address, pk = pickup_address_id)                
                    else:
                        pickup_address = get_object_or_404(Address, pk = pickup_address_id)
                        delivery_address = fetch_consumer_address(consumer, delivery_full_address, delivery_pin_code, delivery_landmark)
                except:
                    content = {'error':' Error parsing addresses'}
                    return Response(content, status = status.HTTP_400_BAD_REQUEST)
                # -------------------------------------------------------

                # CREATE NEW ORDER --------------------------------------
                new_order = Order.objects.create(created_by_user = request.user, 
                                                vendor = vendor, 
                                                consumer = consumer, 
                                                pickup_address = pickup_address, 
                                                delivery_address = delivery_address, 
                                                pickup_datetime = pickup_datetime, 
                                                delivery_datetime = delivery_datetime,
                                                vendor_order_id = vendor_order_id)
                
                if cod_amount is not None and float(cod_amount) > 0:
                    new_order.is_cod = True
                    new_order.cod_amount = float(cod_amount)
                
                if notes is not None:
                    new_order.notes = notes
                
                if total_cost is not None:
                    new_order.total_cost = total_cost  
                
                new_order.save()
                delivery_status = OrderDeliveryStatus.objects.create(date = pickup_datetime, order = new_order)
                new_delivery_ids.append(delivery_status.id)
            except Exception as e:
                content = {
                'error':'Unable to create orders with the given details'
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # SEND MAIL TO RETAIL TEAM, IF ITS A RETAIL ORDER
        if vendor.is_retail is True and len(new_delivery_ids)> 0:
            retail_order_send_email(vendor, new_delivery_ids)
        # -------------------------------------------------------------

        content = {
        'message':'Your Orders has been placed.'
        }
        return Response(content, status = status.HTTP_201_CREATED)

    @list_route(methods=['put'])
    def cancel(self, request, pk = None):
        try:
            delivery_ids = request.data['delivery_ids']
        except Exception as e:
            content = {'error': 'delivery_ids is a mandatory parameter.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        
        timestamp = datetime.now()
        for delivery_id in delivery_ids:
            delivery_status = get_object_or_404(OrderDeliveryStatus, pk=delivery_id)
            if is_user_permitted_to_cancel_order(request.user, delivery_status.order) is False:
                content = {'error': "You don\'t have permissions to cancel this order."}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            if can_update_order(delivery_status, constants.ORDER_STATUS_CANCELLED):
                delivery_status.order_status = constants.ORDER_STATUS_CANCELLED
                delivery_status.save()
                action = delivery_actions(constants.CANCELLED_CODE)
                add_action_for_delivery(action, delivery_status, request.user, None, None, timestamp, None)
            else:
                content = {'error': "Can\'t update this."}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)                            
        content = {'description': 'Order has been canceled'}
        return Response(content, status=status.HTTP_200_OK)

    @list_route(methods=['put'])
    def report(self, request, pk=None):
        try:
            delivery_ids = request.data['delivery_ids']
            reported_reason = request.data['reported_reason']
            timestamp = datetime.now()
            latitude = request.data.get('latitude')
            longitude = request.data.get('longitude')
        except Exception as e:
            content = {'error': 'delivery_ids, reported_reason are mandatory parameters'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        role = user_role(request.user)
        if role == constants.DELIVERY_GUY:
            email_orders = []
            for delivery_id in delivery_ids:
                delivery_status = get_object_or_404(OrderDeliveryStatus, pk=delivery_id)
                delivery_status.is_reported = True
                delivery_status.reported_reason = reported_reason
                delivery_status.save()

                action = delivery_actions(constants.REPORTED_CODE)
                add_action_for_delivery(action, delivery_status, request.user, latitude, longitude, timestamp, reported_reason)
                order_detail = {
                    'delivery_id': delivery_status.id,
                    'vendor': delivery_status.order.vendor.store_name,
                    'customer_name': delivery_status.order.consumer.user.first_name
                }
                email_orders.append(order_detail)
            
            # INFORM OPERATIONS -------------------
            try:
                delivery_guy = get_object_or_404(DeliveryGuy, user = request.user)
                ops_managers = ops_manager_for_dg(delivery_guy)
                if ops_managers.count() == 0:
                    send_reported_email(delivery_guy.user, email_orders, reported_reason)
                else:
                    delivery_ids = ','.join(str(v) for v in delivery_ids)
                    notification_message = constants.NOTIFICATION_MESSAGE_REPORTED%(request.user.first_name, reported_reason, delivery_ids)
                    notification_type = notification_type_for_code(constants.NOTIFICATION_CODE_REPORTED)
                    new_notification = Notification.objects.create(notification_type = notification_type, message = notification_message, delivery_id = delivery_ids)
                    for ops_manager in ops_managers:
                        ops_manager.notifications.add(new_notification)
                        ops_manager.save()
            except Exception as e:
                send_reported_email(delivery_guy.user, email_orders, reported_reason)
            # -----------------------------------------------------------------------
            content = {'data': 'Successfully reported'}
            return Response(content, status=status.HTTP_200_OK)
        else:
            content = {'error': 'You don\'t have permissions to report about the orders'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['put'])
    def multiple_pickup_attempted(self, request, pk=None):
        try:
            delivery_ids = request.data['delivery_ids']
            remarks = request.data.get('remarks')
            latitude = request.data.get('latitude')
            longitude = request.data.get('longitude')
            attempted_datetime = request.data.get('attempted_datetime')
        except Exception as e:
            content = {'error': 'delivery_ids is mandatory parameters and attempted_datetime, remarks, latitude, longitude are optional'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        
        if attempted_datetime is not None:
            try:
                attempted_datetime = parse_datetime(attempted_datetime)    
            except Exception as e:
                log_exception(e, 'parsing date in multiple_pickup_attempted')
                content = {'error': 'Parsing error for pickedup_datetime or date'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            attempted_datetime = datetime.now()            
        
        for delivery_id in delivery_ids:
            try:
                delivery_status = get_object_or_404(OrderDeliveryStatus, pk=delivery_id)
                if is_user_permitted_to_update_order(request.user, delivery_status.order) is False:
                    content = {'error': 'You don\'t have permissions to update this order.'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
                if can_update_order(delivery_status, constants.ORDER_STATUS_PICKUP_ATTEMPTED):
                    update_delivery_status_pickup_attempted(delivery_status, remarks, attempted_datetime)
                    action = delivery_actions(constants.PICKUP_ATTEMPTED_CODE)
                    add_action_for_delivery(action, delivery_status, request.user, latitude, longitude, attempted_datetime, remarks)
                else:
                    content = {'error': 'Order already processed cant attempt the pickup now'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                log_exception(e, 'multiple_pickup_attempted')
                content = {
                    'error': 'Order update failed',
                    'data': {'delivery_id': delivery_id}
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

        content = {'data': 'Orders attempted'}
        return Response(content, status=status.HTTP_200_OK)


    @list_route(methods=['put'])
    def multiple_pickups(self, request, pk=None):
        try:
            delivery_ids = request.data['delivery_ids']
            pickedup_datetime_string = request.data.get('pickedup_datetime')
            latitude = request.data.get('latitude')
            longitude = request.data.get('longitude')
        except Exception as e:
            content = {'error': 'delivery_ids is a mandatory and pickedup_datetime, latitude and longitude are optional'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        
        if pickedup_datetime_string is not None:
            try:
                pickedup_datetime = parse_datetime(pickedup_datetime_string)     
            except Exception, e:
                content = {'error': 'pickedup_datetime should be UTC in following format 2015-11-23T09:32:56.000'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            pickedup_datetime = datetime.now()
        
        for delivery_id in delivery_ids:
            try:
                delivery_status = get_object_or_404(OrderDeliveryStatus, pk=delivery_id)
                if is_user_permitted_to_update_order(request.user, delivery_status.order) is False:
                    content = {'error': "You don\'t have permissions to update this order."}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)

                if can_update_order(delivery_status, constants.ORDER_STATUS_INTRANSIT):
                    update_delivery_status_pickedup(delivery_status, pickedup_datetime, None, None)
                    action = delivery_actions(constants.PICKEDUP_CODE)
                    add_action_for_delivery(action, delivery_status, request.user, latitude, longitude, pickedup_datetime, None)
                else:
                    content = {'error': 'Can\'t update as the order is not queued'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                log_exception(e, 'multiple_pickup_attempted')
                content = {
                    'error': 'delivery update failed',
                    'data': {'delivery_id': delivery_id}
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        content = {'data': 'delivery attempted'}
        return Response(content, status=status.HTTP_200_OK)

    @detail_route(methods=['put'])
    def picked_up(self, request, pk):
        delivery_status = get_object_or_404(OrderDeliveryStatus, pk=pk)
        if is_user_permitted_to_update_order(request.user, delivery_status.order) is False:
            content = {'error': 'You don\'t have permissions to update this order.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        pop_dict = request.data.get('pop')
        remarks = request.data.get('remarks')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        # PICKEDUP DATE TIME --------------------------------------------------------
        pickedup_datetime_string = request.data.get('pickedup_datetime')
        if pickedup_datetime_string is not None:
            pickedup_datetime = parse_datetime(pickedup_datetime_string)
        else:
            pickedup_datetime = datetime.now()
        # ----------------------------------------------------------------------------
        
        is_order_updated = False
        is_order_picked_up = False
        if can_update_order(delivery_status, constants.ORDER_STATUS_INTRANSIT):
            new_pop = None
            if pop_dict is not None:
                new_pop = create_proof(pop_dict)

            update_delivery_status_pickedup(delivery_status, pickedup_datetime, new_pop, remarks)
            action = delivery_actions(constants.PICKEDUP_CODE)
            add_action_for_delivery(action, delivery_status, request.user, latitude, longitude, pickedup_datetime, remarks)
            is_order_updated = True
        else:
            content = {'error': 'Delivery can\'t be processed'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        
        if is_order_updated:
            if is_deliveryguy_assigned(delivery_status) is False:
                notif_unassigned(delivery_status)
            if delivery_status.order.is_reverse_pickup is True:
                end_consumer_phone_number = delivery_status.order.consumer.user.username
                message = 'Dear %s, we have picked your order behalf of %s - Team YourGuy' % (
                    delivery_status.order.consumer.user.first_name, delivery_status.order.vendor.store_name)
                send_sms(end_consumer_phone_number, message)
            content = {'description': 'Delivery has been updated'}
            return Response(content, status=status.HTTP_200_OK)
        else:    
            content = {'error': 'Delivery update failed'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['put'])
    def pickup_attempted(self, request, pk=None):
        delivery_status = get_object_or_404(OrderDeliveryStatus, pk=pk)
        if is_user_permitted_to_update_order(request.user, delivery_status.order) is False:
            content = {'error': "You don\'t have permissions to update this order."}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        remarks = request.data.get('remarks')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        # PICKEDUP DATE TIME --------------------------------------------------------
        attempted_datetime = request.data.get('attempted_datetime')
        if attempted_datetime is not None:
            attempted_datetime = parse_datetime(attempted_datetime)
        else:
            attempted_datetime = datetime.now()
        # ----------------------------------------------------------------------------        
        
        is_order_updated = False
        if can_update_order(delivery_status, constants.ORDER_STATUS_PICKUP_ATTEMPTED):
            update_delivery_status_pickup_attempted(delivery_status, remarks, attempted_datetime)
            action = delivery_actions(constants.PICKUP_ATTEMPTED_CODE)
            add_action_for_delivery(action, delivery_status, request.user, latitude, longitude, attempted_datetime, remarks)
            is_order_updated = True
        else:
            content = {'error': 'Delivery can\'t be processed'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if is_order_updated:
            content = {'description': 'Delivery updated'}
            return Response(content, status=status.HTTP_200_OK)
        else:
            content = {'error': 'Delivery update failed'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
    
    @detail_route(methods=['put'])
    def delivery_attempted(self, request, pk):
        delivery_status = get_object_or_404(OrderDeliveryStatus, pk=pk)
        if is_user_permitted_to_update_order(request.user, delivery_status.order) is False:
            content = {'error': 'You don\'t have permissions to update this order.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude') 
        remarks = request.data.get('remarks')       

        # DELIVERED DATE TIME ---------------------------------------------
        attempted_datetime = request.data.get('attempted_datetime')
        if attempted_datetime is not None:
            attempted_datetime = parse_datetime(attempted_datetime)
        else:
            attempted_datetime = datetime.now()
        # ----------------------------------------------------------------
        
        if can_update_order(delivery_status, constants.ORDER_STATUS_DELIVERY_ATTEMPTED):
            update_delivery_status_delivery_attempted(delivery_status, delivery_remarks, delivered_datetime)
            action = delivery_actions(constants.DELIVERY_ATTEMPTED_CODE)
            add_action_for_delivery(action, delivery_status, request.user, latitude, longitude, attempted_datetime, remarks)
            content = {'description': 'Delivery updated'}
            return Response(content, status=status.HTTP_200_OK)
        else:
            content = {'error': 'Delivery has already been processed, now you cant update the status.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['put'])
    def delivered(self, request, pk):
        delivery_status = get_object_or_404(OrderDeliveryStatus, pk=pk)
        if is_user_permitted_to_update_order(request.user, delivery_status.order) is False:
            content = {'error': 'You don\'t have permissions to update this order.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # REQUEST PARAMETERS ---------------------------------------------
        cod_collected_amount = request.data.get('cod_collected_amount')
        remarks = request.data.get('remarks')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        # ----------------------------------------------------------------

        # DELIVERED DATE TIME ---------------------------------------------
        delivered_datetime_string = request.data.get('delivered_datetime')
        if delivered_datetime_string is not None:
            delivered_datetime = parse_datetime(delivered_datetime_string)
        else:
            delivered_datetime = datetime.now()
        # ----------------------------------------------------------------
        delivered_at = request.data['delivered_at']
        if delivered_at == 'DOOR_STEP' \
                or delivered_at == 'SECURITY' \
                or delivered_at == 'RECEPTION' \
                or delivered_at == 'CUSTOMER':
            pass
        else:
            content = {
                'error': 'delivered_at value is missing or wrong.',
                'Options': 'DOOR_STEP, SECURITY, RECEPTION, CUSTOMER'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        
        if can_update_order(delivery_status, constants.ORDER_STATUS_DELIVERED):
            pod_dict = request.data.get('pod')
            new_pod = None
            if pod_dict is not None:
                new_pod = create_proof(pod_dict)
            update_delivery_status_delivered(delivery_status, delivered_at, delivered_datetime, new_pod, remarks, cod_collected_amount)
            action = delivery_actions(constants.DELIVERED_CODE)
            add_action_for_delivery(action, delivery_status, request.user, latitude, longitude, delivered_datetime, remarks)
            if cod_collected_amount is not None and float(cod_collected_amount) > 0.0:
                end_consumer_phone_number = delivery_status.order.consumer.user.username
                message = 'Dear %s, we have received the payment of %srs behalf of %s - Team YourGuy' % (delivery_status.order.consumer.user.first_name, cod_collected_amount, delivery_status.order.vendor.store_name)
                send_sms(end_consumer_phone_number, message)

            if float(delivery_status.order.cod_amount) > 0.0 and cod_collected_amount is not None and (float(cod_collected_amount) < float(delivery_status.order.cod_amount) or float(cod_collected_amount) > float(delivery_status.order.cod_amount)):
                try:
                    delivery_guy = get_object_or_404(DeliveryGuy, user = request.user)
                    ops_managers = ops_manager_for_dg(delivery_guy)
                    if ops_managers.count() == 0:
                        send_cod_discrepency_email(delivery_status, request.user)
                    else:
                        notification_type = notification_type_for_code(constants.NOTIFICATION_CODE_COD_DISPRENCY)
                        notification_message = constants.NOTIFICATION_MESSAGE_COD_DISCREPENCY%(request.user.first_name, delivery_status.cod_collected_amount, delivery_status.order.cod_amount, delivery_status.id)
                        new_notification = Notification.objects.create(notification_type = notification_type, delivery_id = pk, message = notification_message)
                        for ops_manager in ops_managers:
                            ops_manager.notifications.add(new_notification)
                            ops_manager.save()

                except Exception as e:
                    send_cod_discrepency_email(delivery_status, request.user)
            content = {'description': 'Delivery updated'}
            return Response(content, status=status.HTTP_200_OK)
        else:
            content = {'error': 'Delivery can\'t be updated.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['put'])
    def assign_orders(self, request, pk=None):
        try:
            dg_id = request.data['dg_id']
            delivery_ids = request.data['delivery_ids']
            assignment_type = request.data['assignment_type']
        except Exception as e:
            content = {'error': 'dg_id, delivery_ids, assignment_type are Mandatory'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        delivery_count = len(delivery_ids)
        if delivery_count > 50:
            content = {'error': 'Cant assign more than 50 orders at a time.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if assignment_type == 'pickup' or assignment_type == 'delivery':
            pass
        else:
            content = {'error': 'assignment_type can only be either pickup or delivery'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        is_orders_assigned = False
        dg = get_object_or_404(DeliveryGuy, id=dg_id)

        todays_delivery_ids = []
        for delivery_id in delivery_ids:
            delivery_status = get_object_or_404(OrderDeliveryStatus, id=delivery_id)
            order = delivery_status.order

            current_datetime = datetime.now()
            if current_datetime.date() > delivery_status.date.date():
                content = {'error': 'Cant assign orders of previous dates'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            if order.is_recurring is True:
                # FETCHING ALL RECURRING ORDERS FOR ASSIGNMENT ------------------------
                today_datetime = current_datetime.replace(hour=0, minute=0, second=0)
                recurring_delivery_statuses = OrderDeliveryStatus.objects.filter(order=order, date__gte=today_datetime)
                for recurring_delivery_status in recurring_delivery_statuses:
                    if is_user_permitted_to_update_order(request.user, recurring_delivery_status.order) is False:
                        content = {'error': 'You don\'t have permissions to update this order.'}
                        return Response(content, status=status.HTTP_400_BAD_REQUEST)

                    # Final Assignment -------------------------------------------
                    if assignment_type == 'pickup':
                        recurring_delivery_status.pickup_guy = dg
                    else:
                        recurring_delivery_status.delivery_guy = dg
                    recurring_delivery_status.save()
                    action = delivery_actions(constants.ASSIGNED_CODE)
                    add_action_for_delivery(action, recurring_delivery_status, request.user, None, None, datetime.now(), None)

                    is_orders_assigned = True
            else:
                if is_user_permitted_to_update_order(request.user, delivery_status.order) is False:
                    content = {'error': 'You don\'t have permissions to update this order.'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)

                # Final Assignment -------------------------------------------
                if assignment_type == 'pickup':
                    delivery_status.pickup_guy = dg
                else:
                    delivery_status.delivery_guy = dg
                delivery_status.save()
                action = delivery_actions(constants.ASSIGNED_CODE)
                add_action_for_delivery(action, delivery_status, request.user, None, None, datetime.now(), None)
                is_orders_assigned = True
                # -------------------------------------------------------------
            
            if is_today_date(delivery_status.date):
                todays_delivery_ids.append(delivery_status.id)
        
        # INFORM DG THROUGH SMS AND NOTIF IF ITS ONLY TODAYS DELIVERY -----
        try:
            if len(todays_delivery_ids) == 1:
                delivery_status = get_object_or_404(OrderDeliveryStatus, id=todays_delivery_ids[0])
                today = datetime.now()
                send_sms_to_dg_about_order(today, dg, delivery_status)
            else:
                send_sms_to_dg_about_mass_orders(dg, todays_delivery_ids)
        except Exception as e:
            log_exception(e, 'SMS to DG about delivery assignment')
        
        content = {'description': 'Order assigned'}
        return Response(content, status=status.HTTP_200_OK)

    @list_route(methods=['put'])
    def add_deliveries(self, request, pk=None):
        role = user_role(request.user)
        if role is not constants.DELIVERY_GUY:
            return response_access_denied()
        else:
            delivery_boy = get_object_or_404(DeliveryGuy, user=request.user)

        # INPUT PARAMETERS CHECK --------------------------------------------
        try:
            vendor_id = request.data['vendor_id']
            deliveries = request.data['deliveries']
        except Exception as e:
            content = {
                'error': 'Missing input parameters',
                'description': 'vendor_id, deliveries [consumer_phonenumber, consumer_name, pincode]'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        # --------------------------------------------------------------------

        # FETCH VENDOR DETAILS --------------------------------------------
        try:
            vendor = get_object_or_404(Vendor, pk=vendor_id)
        except Exception as e:
            content = {'error': 'Cant find vendor with supplied vendor_id'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        all_vendor_addresses = vendor.addresses.all()
        if len(all_vendor_addresses) > 0:
            vendor_address = all_vendor_addresses[0]
        else:
            content = {'error': 'Cant find vendor address'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        # ------------------------------------------------------------------

        # PICK UP AND DELVIERY DATE TIMES ---------------------------------
        pickup_datetime = datetime.now()
        if is_pickup_time_acceptable(pickup_datetime) is False:
            content = {
            'error':'Pickup date or time not acceptable', 
            'description':'Pickup time can only be between 5.30AM to 10.00PM and past dates are not allowed'
            }
            return Response(content, status = status.HTTP_400_BAD_REQUEST)            
        
        if vendor.is_hyper_local is True:
            delivery_timedelta = timedelta(hours = 1, minutes = 0)
            delivery_datetime = pickup_datetime + delivery_timedelta
        else:                                    
            delivery_timedelta = timedelta(hours = 4, minutes = 0)
            delivery_datetime = pickup_datetime + delivery_timedelta
        # ------------------------------------------------------------------

        created_orders = []
        for delivery in deliveries:
            try:
                consumer_name = delivery['consumer_name']
                consumer_phonenumber = delivery['consumer_phonenumber']
                pincode = delivery['pincode']
            except Exception as e:
                content = {'error': 'consumer_name, consumer_phonenumber, pincode are mandatory parameters'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            # FETCH CUSTOMER or CREATE NEW CUSTOMER ----------------
            consumer = fetch_consumer(consumer_phonenumber, consumer_name, vendor)
            consumer_address = fetch_consumer_address(consumer, None, pincode, None)
            # ------------------------------------------------------

            extra_note = 'Additional delivery added by the boy: %s' % delivery_boy.user.first_name
            # CREATE NEW ORDER --------------------------------------
            new_order = Order.objects.create(created_by_user=request.user,
                                             vendor=vendor,
                                             consumer=consumer,
                                             pickup_address=vendor_address,
                                             delivery_address=consumer_address,
                                             pickup_datetime=pickup_datetime,
                                             delivery_datetime=delivery_datetime,
                                             notes=extra_note)

            delivery_status = OrderDeliveryStatus.objects.create(date=pickup_datetime, order=new_order)
            created_orders.append(dg_created_orders(delivery_status))

            # ASSIGN PICKUP AS SAME BOY -------------------------------------------
            delivery_status.pickup_guy = delivery_boy
            if vendor.is_hyper_local is True:
                delivery_status.delivery_guy = delivery_boy
            delivery_status.save()
            # ---------------------------------------------------------------------

        # SEND AN EMAIL ABOUT ADDITIONAL ORDERS TO VENDOR AND OPS/SALES -----------
        email_ids = constants.EMAIL_ADDITIONAL_ORDERS
        email_ids.append(vendor.email)
        today_date = datetime.now()
        subject = 'YourGuy: Extra orders picked up for today: %s' % today_date.strftime('%B %d, %Y')
        body = 'Hi %s,' % vendor.store_name
        body = body + '\n\nWe have picked up following additional orders from you today: %s \n' % today_date.strftime(
            '%B %d, %Y')
        for order in created_orders:
            body = body + '\nOrder no: %s, Customer name: %s' % (order['id'], order['customer_name'])
        body = body + '\n\nIf there are any discrepancies, ' \
                      'please raise a ticket with order no. on the app - Feedback tab.'
        body = body + '\n' + constants.COMPLAINTS_URL
        body = body + '\n\n-Thanks \nYourGuy BOT'
        send_email(email_ids, subject, body)
        # --------------------------------------------------------------------------

        content = {
            'data': created_orders,
            'message': 'Orders placed Successfully'
        }
        return Response(content, status=status.HTTP_201_CREATED)

    @detail_route(methods=['put'])
    def reschedule(self, request, pk):
        try:
            new_date_string = request.data['new_date']
            new_date = parse_datetime(new_date_string)
        except Exception as e:
            parameters = ['new_date']
            return response_incomplete_parameters(parameters)

        delivery_status = get_object_or_404(OrderDeliveryStatus, id=pk)
        current_datetime = datetime.now()
        if current_datetime.date() > new_date.date():
            content = {
                'error': 'Reschedule Failed',
                'description': 'You can\'t prepone the delivery to previous dates.'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if is_user_permitted_to_edit_order(request.user, delivery_status.order):
            if can_update_delivery_status(delivery_status):
                delivery_status.date = new_date
                delivery_status.save()
                action = delivery_actions(constants.RESCHEDULED_CODE)
                add_action_for_delivery(action, delivery_status, request.user, None, None, datetime.now(), None)
                content = {'description': 'Reschedule successful'}
                return Response(content, status=status.HTTP_200_OK)
            else:
                content = {'error': 'The order has already been processed, now you can\'t update the status.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            return response_access_denied()