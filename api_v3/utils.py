import base64
from datetime import time, datetime, timedelta

import dateutil.relativedelta
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api_v3 import constants
from yourguy.models import Order, OrderDeliveryStatus, VendorAgent, Consumer


def address_string(address):
    try:
        if len(address.full_address) > 1:
            address_string = address.full_address + ', ' + address.pin_code
        else:
            address_string = address.flat_number + ',' + address.building + ',' + address.street + ','
            if address.area is not None:
                address_string = address_string + address.area.area_name
        return address_string
    except Exception as e:
        print(e)


def is_correct_pincode(pincode):
    if pincode.isdigit() and len(pincode) == 6:
        return True
    else:
        return False


def is_vendor_has_same_address_already(vendor, pincode):
    try:
        addresses = vendor.addresses.all()
        for address in addresses:
            if address.pin_code == pincode:
                return address
        return None
    except Exception as e:
        return None


def is_consumer_has_same_address_already(consumer, pincode):
    try:
        addresses = consumer.addresses.all()
        for address in addresses:
            if address.pin_code == pincode:
                return address
        return None
    except Exception as e:
        return None


def is_userexists(username):
    if User.objects.filter(username=username).count():
        return True
    else:
        return False


def is_consumerexists(user):
    if Consumer.objects.filter(user=user).count():
        return True
    else:
        return False


def is_groupexists(name):
    if Group.objects.filter(name=name).count():
        return True
    else:
        return False


def assign_usergroup_with_name(user, group_name):
    try:
        group = Group.objects.get(name=group_name)
        group.user_set.add(user)
        return True
    except:
        return False


def assign_usergroup(user):
    if is_groupexists(user_role(user)):
        role = user_role(user)
        return assign_usergroup_with_name(user, role)
    else:
        return False


def time_delta():
    return timedelta(hours=5, minutes=30)


def ist_day_start(date):
    ist_timedelta = time_delta()
    day_start = datetime.combine(date, time()).replace(hour=0, minute=0, second=0)
    return day_start - ist_timedelta


def ist_day_end(date):
    ist_timedelta = time_delta()
    day_end = datetime.combine(date, time()).replace(hour=23, minute=59, second=59)
    return day_end - ist_timedelta


def ist_datetime(datetime):
    ist_timedelta = time_delta()
    return datetime + ist_timedelta


def days_in_int(by_day):
    day_values = {'MO': 0, 'TU': 1, 'WE': 2, 'TH': 3, 'FR': 4, 'SA': 5, 'SU': 6}
    int_days = []
    for day in by_day:
        int_days.append(day_values[day])
    return int_days


def is_today_date(date):
    today = datetime.now()
    if today.date() == date.date():
        return True
    else:
        return False


def create_token(user, user_role):
    if Token.objects.filter(user=user).count():
        token = get_object_or_404(Token, user=user)
    else:
        full_string = '%s:%s' % (user.username, user_role)
        token_string = base64.b64encode(full_string)
        token = Token.objects.create(user=user, key=token_string)
    return token


def user_role(user):
    token = Token.objects.get(user=user)
    token_string = base64.b64decode(token.key)
    role = token_string.split(':').pop()
    if role == constants.VENDOR:
        return constants.VENDOR
    elif role == constants.CONSUMER:
        return constants.CONSUMER
    elif role == constants.OPERATIONS:
        return constants.OPERATIONS
    elif role == constants.SALES:
        return constants.SALES
    elif role == constants.DELIVERY_GUY:
        return constants.DELIVERY_GUY
    else:
        return None


def log_exception(e, message):
    subject = 'Error has occurred.'
    body = message, e
    send_email(constants.EMAIL_ERRORS, subject, body)


def send_email(to_mail_ids, subject, body):
    try:
        send_mail(subject, body, constants.FROM_MAIL_ID, to_mail_ids, fail_silently=False)
    except Exception as e:
        pass


def send_sms(phonenumber, message):
    url = constants.SMS_URL.format(mobile_number=phonenumber, message_text=message)
    try:
        print
        "Test server doesnt send sms"
    except Exception as e:
        send_email('SMS error', 'problem sending SMS \nplease check {} {}'.format(phonenumber, message),
                   constants.FROM_MAIL_ID, ['tech@yourguy.in'], fail_silently=False)


def is_vendoragentexists(user):
    if VendorAgent.objects.filter(user=user).count():
        return True
    else:
        return False


def paginate(list, page):
    paginator = Paginator(list, constants.PAGINATION_PAGE_SIZE)  # Show 25 contacts per page
    try:
        result = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        result = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        result = paginator.page(paginator.num_pages)

    return result.object_list


def is_pickup_time_acceptable(datetime):
    if time(0, 0) <= datetime.time() <= time(16, 30):
        return True
    else:
        return False


def inform_dgs_about_orders_assigned():
    # FETCH ALL ORDERS ASSIGNED TO DGs
    date = datetime.today()
    day_start = ist_day_start(date)
    day_end = ist_day_end(date)
    try:
        delivery_status_queryset = OrderDeliveryStatus.objects.filter(delivery_guy__isnull=False, date__gte=day_start,
                                                                      date__lte=day_end).annotate('delivery_guy')
    except Exception as e:
        print(e)


def assign_dg():
    # FETCH ALL TODAY ORDERS
    date = datetime.today()
    day_start = ist_day_start(date)
    day_end = ist_day_end(date)

    unassigned_order_ids = ''

    delivery_status_queryset = OrderDeliveryStatus.objects.filter(date__gte=day_start, date__lte=day_end,
                                                                  delivery_guy=None)
    # FILTER BY ORDER STATUS
    delivery_status_queryset = delivery_status_queryset.filter(
        Q(order_status=constants.ORDER_STATUS_PLACED) | Q(order_status=constants.ORDER_STATUS_QUEUED) | Q(
            order_status=constants.ORDER_STATUS_INTRANSIT))
    # --------------------------------------------------------------------
    for delivery_status in delivery_status_queryset.all():
        try:
            order = get_object_or_404(Order, delivery_status=delivery_status)

            # CUSTOMER AND VENDOR FILTERING
            vendor = order.vendor
            consumer = order.consumer

            previous_delivery_statuses = OrderDeliveryStatus.objects.filter(delivery_guy__isnull=False,
                                                                            order__consumer=consumer,
                                                                            order__vendor=vendor)
            # FILTER LAST 2 MONTHS ORDERS
            two_months_previous_date = day_start - dateutil.relativedelta.relativedelta(months=1)
            previous_delivery_statuses = previous_delivery_statuses.filter(date__gte=two_months_previous_date,
                                                                           date__lte=day_start)
            # FILTERING BY PICKUP TIME RANGE
            pickup_hour = int(order.pickup_datetime.hour)
            previous_delivery_statuses = previous_delivery_statuses.filter(
                Q(order__pickup_datetime__hour=pickup_hour - 1) | Q(order__pickup_datetime__hour=pickup_hour) | Q(
                    order__pickup_datetime__hour=pickup_hour + 1))

            # FILTERING BY PICKUP TIME RANGE
            try:
                latest_assigned_delivery = previous_delivery_statuses.latest('date')
                if latest_assigned_delivery is not None:
                    req_delivery_guy = latest_assigned_delivery.delivery_guy
                    delivery_status.delivery_guy = req_delivery_guy
                    delivery_status.save()
            except Exception as e:
                unassigned_order_ids = unassigned_order_ids + "\n %s - %s - %s" % (
                    vendor.store_name, order.id, consumer.user.first_name)
                pass

        except Exception as e:
            print(e)

    # SEND AN EMAIL SAYING CANT FIND APPROPRIATE DELIVERY GUY FOR THIS ORDER. PLEASE ASSIGN MANUALLY
    today_string = datetime.now().strftime("%Y %b %d")
    email_subject = 'Unassigned orders for %s' % today_string

    email_body = "Good Morning Guys, \nUnassigned Orders: %s \nPlease assign manually. \n\n- Team YourGuy" % (
        unassigned_order_ids)
    send_email(constants.EMAIL_UNASSIGNED_ORDERS, email_subject, email_body)
    return


@api_view(['GET'])
def is_recurring_var_setting(request):
    if request.user.is_staff is False:
        content = {
            'error': 'insufficient permissions',
            'description': 'Only admin can access this method'
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    else:
        all_orders = Order.objects.all()
        for order in all_orders:
            if len(order.delivery_status.all()) > 1:
                order.is_recurring = True
                order.save()

        content = {'data': 'All done'}
        return Response(content, status=status.HTTP_200_OK)


@api_view(['GET'])
def delivery_status_update(request):
    if request.user.is_staff is False:
        content = {
            'error': 'insufficient permissions',
            'description': 'Only admin can access this method'
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    else:
        all_delivery_statuses = OrderDeliveryStatus.objects.all()
        for delivery_status in all_delivery_statuses:
            if delivery_status.delivered_at == 'ATTEMPTED':
                delivery_status.delivered_at = 'DELIVERYATTEMPTED'
                delivery_status.save()
            elif delivery_status.delivered_at == 'DOOR_STEP' or delivery_status.delivered_at == 'SECURITY' or delivery_status.delivered_at == 'RECEPTION' or delivery_status.delivered_at == 'CUSTOMER':
                print
                'dont change'
            else:
                delivery_status.delivered_at = 'NONE'
                delivery_status.save()

        content = {'data': 'All done'}
        return Response(content, status=status.HTTP_200_OK)


@api_view(['GET'])
def attach_order_to_deliverystatus(request):
    all_delivery_status = OrderDeliveryStatus.objects.filter(order=None)
    for delivery_status in all_delivery_status:
        try:
            order_id = delivery_status.order_id_in_order_table
            order = get_object_or_404(Order, pk=order_id)
            delivery_status.order = order
            delivery_status.save()
        except Exception as e:
            pass

    content = {'data': 'Done attaching orders'}
    return Response(content, status=status.HTTP_200_OK)


@api_view(['GET'])
def fill_order_ids(request):
    all_orders = Order.objects.all().prefetch_related('delivery_status')
    for order in all_orders:
        all_deliveries = order.delivery_status.all()
        for delivery_status in all_deliveries:
            delivery_status.order_id = order.id
            delivery_status.save()

    content = {'data': 'Done saving addresses'}
    return Response(content, status=status.HTTP_200_OK)
