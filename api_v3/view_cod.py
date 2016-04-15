from datetime import datetime, timedelta
from django.utils.dateparse import parse_datetime
from django.db.models import Sum
from django.utils.decorators import method_decorator
from django.db.models import Q
from api_v3.utils import cod_actions, response_access_denied, get_object_or_404, \
    response_error_with_message, response_with_payload, response_incomplete_parameters, response_success_with_message, response_invalid_pagenumber
from api_v3 import constants
from yourguy.models import CODTransaction, DeliveryGuy, OrderDeliveryStatus, DeliveryTeamLead, ProofOfBankDeposit, \
    Picture, Employee, Vendor, VendorAgent
from rest_framework import authentication, viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from api_v3.utils import user_role, log_exception, paginate, send_sms, send_email, time_delta
from api_v3.push import send_push
import uuid
import pytz
from django.contrib.auth.decorators import user_passes_test

error_message_1 = 'This is a deactivated dg'
response_error_with_message(error_message_1)

error_message_2 = 'Not a delivery guy'
response_error_with_message(error_message_2)


def active_check(self):
    role = user_role(self)
    if role == constants.DELIVERY_GUY:
        dg = get_object_or_404(DeliveryGuy, user=self)
        if dg.is_active is True:
            return True
        else:
            return response_error_with_message(error_message_1)
    else:
        return response_error_with_message(error_message_2)


def send_cod_status_notification(dg, dg_tl, cod_amount, is_transaction_successful):
    try:
        if is_transaction_successful is True:
            data = {
                'message': 'Amount %d was transferred to %s successfully ' % (cod_amount, dg_tl.user.first_name),
                'type': 'cod_transfer_to_tl',
                'data': {
                    'is_transaction_successful': is_transaction_successful
                }
            }
            send_push(dg.device_token, data)
        else:
            data = {
                'message': 'Transfer of amount %d to %s was declined ' % (cod_amount, dg_tl.user.first_name),
                'type': 'cod_transfer_to_tl',
                'data': {
                    'is_transaction_successful': is_transaction_successful
                }
            }
            send_push(dg.device_token, data)
    except Exception as e:
        log_exception(e, 'Push notification not sent in send_cod_status_notification ')


def send_timeout_notification(dg, cod_amount, is_time_out, is_transaction_successful):
    try:
        data = {
            'message': 'Transfer to %s of amount %d timed out.' % (dg.user.first_name, cod_amount),
            'type': 'cod_transfer_to_tl',
            'data': {
                'is_time_out': is_time_out,
                'is_transaction_successful': is_transaction_successful
            }
        }
        send_push(dg.device_token, data)
    except Exception as e:
        log_exception(e, 'Push notification not sent in send_cod_status_notification ')


def create_cod_transaction(transaction, user, dg_id, dg_tl_id, cod_amount, transaction_uuid, delivery_ids):
    created_time_stamp = datetime.now()
    cod_transaction = CODTransaction.objects.create(transaction=transaction,
                                                    created_by_user=user,
                                                    created_time_stamp=created_time_stamp,
                                                    dg_id=dg_id, dg_tl_id=dg_tl_id,
                                                    cod_amount=cod_amount,
                                                    transaction_uuid=transaction_uuid,
                                                    deliveries=delivery_ids)
    cod_transaction.save()
    return cod_transaction


def add_cod_transaction_to_delivery(cod_transaction, delivery):
    delivery.cod_transactions.add(cod_transaction)
    delivery.save()


def dg_collections_dict(delivery_status):
    dg_collections = {
        'delivery_id': delivery_status.id,
        'cod_collected': delivery_status.cod_collected_amount,
        'delivery_date_time': delivery_status.completed_datetime,
        'customer': delivery_status.order.consumer.full_name,
        'vendor': delivery_status.order.vendor.store_name
    }

    return dg_collections


def dg_total_cod_amount_dict(delivery_status):
    dg_total_cod_amount = {
        'total_cod_amount': None,
        'dg_collections': []
    }
    return dg_total_cod_amount


def associated_dgs_collections_dict(dg, cod_transaction):
    associated_dgs_collections = {
        'dg_id': dg.id,
        'dg_name': dg.user.first_name,
        'cod_transferred': cod_transaction.cod_amount,
        'transferred_time': cod_transaction.verified_time_stamp,
        'delivery_ids': []
    }
    return associated_dgs_collections


def dg_tl_collections_dict():
    dg_tl_collections = {
        'total_cod_amount': None,
        'associated_dg_collections': [],
        'tls_collections': []
    }

    return dg_tl_collections


def associated_dgs_pending_cod_details(delivery_guy):
    associated_dgs_pending_cod_details_dict = {
        'dg_id': delivery_guy.id,
        'dg_name': delivery_guy.user.first_name,
        'cod_amount': None
    }
    return associated_dgs_pending_cod_details_dict


def cod_balance_calculation(dg):
    deliveries = []
    delivery_statuses = OrderDeliveryStatus.objects.filter(delivery_guy=dg,
                                                           cod_status=constants.COD_STATUS_COLLECTED)
    delivery_statuses_total = delivery_statuses.values('delivery_guy__user__username').\
        annotate(sum_of_cod_collected=Sum('cod_collected_amount'))
    balance_amount = 0
    if len(delivery_statuses_total) > 0:
        balance_amount = delivery_statuses_total[0]['sum_of_cod_collected']

    if dg.is_teamlead is True:
        try:
            dg_tl_id = dg.id
            delivery_guy_tl = DeliveryTeamLead.objects.get(delivery_guy=dg)
            associated_dgs = delivery_guy_tl.associate_delivery_guys.all()
            associated_dgs = associated_dgs.filter(is_active=True)
            for single_dg in associated_dgs:
                delivery_statuses = OrderDeliveryStatus.objects.filter(delivery_guy=single_dg,
                                                                        cod_status=constants.COD_STATUS_TRANSFERRED_TO_TL,
                                                                        cod_transactions__transaction_status=constants.VERIFIED,
                                                                        cod_transactions__dg_tl_id=dg_tl_id)
                for single in delivery_statuses:
                    deliveries.append(single.id)
                delivery_statuses = delivery_statuses.values('delivery_guy__user__username').annotate(sum_of_cod_collected=Sum('cod_collected_amount'))
                if len(delivery_statuses) > 0:
                    balance_amount = balance_amount + delivery_statuses[0]['sum_of_cod_collected']
        except Exception, e:
            pass
    return balance_amount

def create_proof(bank_deposit_proof, user, cod_amount, bank_receipt_number):
    receipt = bank_deposit_proof
    total_cod = cod_amount
    try:
        proof = ProofOfBankDeposit.objects.create(created_by_user=user, total_cod=total_cod)
        proof.receipt = (Picture.objects.create(name=receipt))
        proof.receipt_number = bank_receipt_number

        proof.save()
    except Exception as e:
        error_message = 'Failed to create the bank deposit proof'
        return response_error_with_message(error_message)
    return proof


def all_bank_deposit_cod_transactions_list(cod_transaction):
    all_bank_deposit_cod_transactions_dict = {
        'created_by_user': cod_transaction.created_by_user.first_name,
        'created_time_stamp': cod_transaction.created_time_stamp.date(),
        'cod_amount': cod_transaction.cod_amount,
        'transaction_status': cod_transaction.transaction_status,
        'transaction_id': cod_transaction.transaction_uuid
    }
    return all_bank_deposit_cod_transactions_dict


def verified_bank_deposit_list(cod_transaction, delivery):
    verified_bank_deposit_dict = {
        'verified_time_stamp': cod_transaction.verified_time_stamp.date(),
        'transaction_status': cod_transaction.transaction_status,
        'transaction_id': cod_transaction.transaction_uuid,
        'cod_amount': delivery.cod_collected_amount,
        'vendor_id': delivery.order.vendor.id,
        'vendor_name': delivery.order.vendor.store_name,
        'delivery_id': delivery.id

    }
    return verified_bank_deposit_dict


def per_order_list(delivery):
    per_order_dict = {
        'cod_amount': delivery.cod_collected_amount,
        'vendor_id': delivery.order.vendor.id,
        'vendor_name': delivery.order.vendor.store_name,
        'delivery_id': delivery.id
    }
    return per_order_dict


def pagination_count_bank_deposit():
    pagination_count_dict = {
        'total_pages': None,
        'total_count': None,
        'all_transactions': []
    }
    return pagination_count_dict


def transaction_history(cod_transaction):
    transaction_history_dict = {
        'date': cod_transaction.created_time_stamp,
        'cod_amount': cod_transaction.cod_amount,
        'transaction_type': None,
        'transaction_status': cod_transaction.transaction_status,
        'salary_deduction': cod_transaction.salary_deduction
    }
    return transaction_history_dict


def vendor_transaction_history(cod_transaction):
    vendor_transaction_history_dict = {
        'date': cod_transaction.created_time_stamp.date(),
        'cod_amount': cod_transaction.cod_amount,
        'utr_number': cod_transaction.utr_number,
        'deliveries': []
    }
    return vendor_transaction_history_dict


def send_salary_deduction_email(first_name, orders, amount, pending_amount):
    subject = '%s Salary Deduction' % first_name
    body = 'Hello,\n\nThere has been a salary deduction for %s  \n\nOrder id: %s\nCOD Amount deposited: %d\nSalary Deduction amount: %.2f'%(first_name, orders, amount, pending_amount)
    body = body + '\n\nThanks \n-YourGuy BOT'
    send_email(constants.EMAIL_DG_SALARY_DEDUCTIONS, subject, body)


def search_cod_transactions(user, search_query):
    cod_action = cod_actions(constants.COD_BANK_DEPOSITED_CODE)
    cod_transactions_queryset = CODTransaction.objects.filter(transaction__title=cod_action)
    if search_query.isdigit():
        cod_transactions_queryset = cod_transactions_queryset.filter(
            Q(id=search_query) |
            Q(orderdeliverystatus__order__vendor__phone_number=search_query) |
            Q(orderdeliverystatus__order__vendor_order_id=search_query))
    else:
        cod_transactions_queryset = cod_transactions_queryset.filter(
            Q(orderdeliverystatus__order__vendor__store_name=search_query))
    return cod_transactions_queryset


class CODViewSet(viewsets.ViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @list_route(methods=['GET'])
    @method_decorator(user_passes_test(active_check))
    def cod_balance(self, request):
        role = user_role(request.user)
        if role == constants.DELIVERY_GUY:
            dg = get_object_or_404(DeliveryGuy, user=request.user)
            # if dg.is_active is True:
            balance_amount = cod_balance_calculation(dg)
            if balance_amount is None:
                balance_amount = 0
            else:
                pass
            return response_with_payload(balance_amount, None)
            # else:
            #     error_message = 'This is a deactivated dg'
            #     return response_error_with_message(error_message)
        else:
            return response_access_denied()


    # for dg tl, order object if he is the assigned dg(order id, cod amount collected, customer name, vendor name, delivery date time)
    # dg object of his associated dg who has transferred the cod(dg id, dg name, transaction date time,
    # for dg, filter OrderDeliveryStatus for cod status(this is cumulative cod not yet transferred to tl)
    # for each order(order id, cod amount collected, customer name, vendor name, delivery date time)
    @list_route(methods=['GET'])
    @method_decorator(user_passes_test(active_check))
    def collections(self, request):
        role = user_role(request.user)
        if role == constants.DELIVERY_GUY:
            dg = get_object_or_404(DeliveryGuy, user=request.user)
            # if dg.is_active is True:
            if dg.is_teamlead is True:
                dg_tl_id = dg.id
                tl_collections = []
                asso_dg_collections = []
                dg_tl_collections = dg_tl_collections_dict()
                delivery_statuses = OrderDeliveryStatus.objects.filter(delivery_guy=dg,
                                                                       cod_status=constants.COD_STATUS_COLLECTED)
                for single in delivery_statuses:
                    dg_collections = dg_collections_dict(single)
                    tl_collections.append(dg_collections)
                    tl_collections.sort(key=lambda item: item['delivery_date_time'], reverse=True)
                dg_tl_collections['tls_collections'] = tl_collections

                balance_amount = cod_balance_calculation(dg)
                delivery_guy_tl = DeliveryTeamLead.objects.get(delivery_guy=dg)
                associated_dgs = delivery_guy_tl.associate_delivery_guys.all()
                associated_dgs = associated_dgs.filter(is_active=True)
                for single_dg in associated_dgs:
                    # ------------------------------------
                    deliveries = []
                    delivery_statuses = OrderDeliveryStatus.objects.filter(delivery_guy=single_dg,
                                                                           cod_status=constants.COD_STATUS_TRANSFERRED_TO_TL,
                                                                           cod_transactions__transaction_status=constants.VERIFIED,
                                                                           cod_transactions__dg_tl_id=dg_tl_id)
                    for single in delivery_statuses:
                        deliveries.append(single.id)
                    cod_action = cod_actions(constants.COD_TRANSFERRED_TO_TL_CODE)
                    cod_transaction = CODTransaction.objects.filter(transaction__title=cod_action,
                                                                    transaction_status=constants.VERIFIED,
                                                                    dg_id=single_dg.id,
                                                                    dg_tl_id=dg_tl_id)
                    result_transactions = []
                    
                    for single_delivery in deliveries:
                        first_qx = '%s,'%(single_delivery)
                        second_qx = ',%s'%(single_delivery)
                        third_qx = ',%s,'%(single_delivery)
                        fourth_qx = '%s'%(single_delivery)
                        fifth_qx = '[%s]'%(single_delivery)
                        sixth_qx = "'%s'" %(single_delivery)
                        temp_transactions = cod_transaction.filter(Q(deliveries__startswith=first_qx) | Q(deliveries__endswith=second_qx)
                                                                   | Q(deliveries__contains=third_qx) | Q(deliveries__exact=fourth_qx) |
                                                                   Q(deliveries__exact=fifth_qx) | Q(deliveries__contains=sixth_qx))
                        result_transactions.extend(temp_transactions)

                    result_transactions = list(set(result_transactions))
                    for transaction in result_transactions:
                        associated_dgs_collections = associated_dgs_collections_dict(single_dg, transaction)
                        delivery_ids = eval(transaction.deliveries)
                        associated_dgs_collections['delivery_ids'] = delivery_ids
                        asso_dg_collections.append(associated_dgs_collections)
                        asso_dg_collections.sort(key=lambda item: item['transferred_time'], reverse=True)
                dg_tl_collections['total_cod_amount'] = balance_amount
                dg_tl_collections['associated_dg_collections'] = asso_dg_collections
                return response_with_payload(dg_tl_collections, None)
            else:
                dg_entire_collections = []
                delivery_statuses = OrderDeliveryStatus.objects.filter(delivery_guy=dg,
                                                                       cod_status=constants.COD_STATUS_COLLECTED)
                delivery_statuses_total = delivery_statuses.values('delivery_guy__user__username').\
                    annotate(sum_of_cod_collected=Sum('cod_collected_amount'))
                if len(delivery_statuses) > 0 and len(delivery_statuses_total) > 0:
                    dg_total_cod_amount = dg_total_cod_amount_dict(delivery_statuses_total[0])
                    dg_total_cod_amount['total_cod_amount'] = delivery_statuses_total[0]['sum_of_cod_collected']

                    for single in delivery_statuses:
                        dg_collections = dg_collections_dict(single)
                        dg_entire_collections.append(dg_collections)
                        dg_entire_collections.sort(key=lambda item: item['delivery_date_time'], reverse=True)
                    dg_total_cod_amount['dg_collections'] = dg_entire_collections
                    return response_with_payload(dg_total_cod_amount, None)
                else:
                    success_message = 'No COD collection pending to transfer to TL'
                    return response_success_with_message(success_message)
            # else:
            #     error_message = 'This is a deactivated dg'
            #     return response_error_with_message(error_message)
        else:
            return response_access_denied()

    @list_route(methods=['POST'])
    @method_decorator(user_passes_test(active_check))
    def qr_code(self, request):
        role = user_role(request.user)
        balance_amount = 0
        if role == constants.DELIVERY_GUY:
            dg = get_object_or_404(DeliveryGuy, user=request.user)
            dg_id = dg.id
            if dg.is_teamlead is False:
                try:
                    dg_tl_id = request.data['dg_tl_id']
                    cod_amount = request.data['cod_amount']
                    delivery_ids = request.data['delivery_ids']
                except Exception as e:
                    params = ['dg_tl_id', 'cod_amount', 'delivery_ids']
                    return response_incomplete_parameters(params)
                try:
                    for delivery_id in delivery_ids:
                        delivery_status = get_object_or_404(OrderDeliveryStatus, pk=delivery_id)
                        balance_amount = balance_amount + delivery_status.cod_collected_amount
                    if balance_amount == cod_amount:
                        transaction_uuid = uuid.uuid4()
                        cod_action = cod_actions(constants.COD_TRANSFERRED_TO_TL_CODE)
                        cod_transaction = create_cod_transaction(cod_action, request.user, dg_id, dg_tl_id, cod_amount, transaction_uuid, delivery_ids)
                        for delivery_id in delivery_ids:
                            delivery_status = get_object_or_404(OrderDeliveryStatus, pk=delivery_id)
                            add_cod_transaction_to_delivery(cod_transaction, delivery_status)
                        return response_with_payload(transaction_uuid, None)
                    else:
                        error_message = 'cod amount does not match with the total cod collection from all the deliveries selected'
                        return response_error_with_message(error_message)
                except Exception as e:
                    error_message = 'Order not found'
                    return response_error_with_message(error_message)
            else:
                error_message = 'This is a deactivated dg OR a DG TL'
                return response_error_with_message(error_message)
        else:
            return response_access_denied()

    @list_route(methods=['GET'])
    @method_decorator(user_passes_test(active_check))
    def associated_dgs_collections(self, request):
        all_associated_dgs = []
        role = user_role(request.user)
        if role == constants.DELIVERY_GUY:
            delivery_guy = get_object_or_404(DeliveryGuy, user=request.user)
            # and delivery_guy.is_active is True
            if delivery_guy.is_teamlead is True:
                try:
                    delivery_guy_tl = DeliveryTeamLead.objects.get(delivery_guy=delivery_guy)
                    associated_dgs = delivery_guy_tl.associate_delivery_guys.all()
                    associated_dgs = associated_dgs.order_by('user__first_name')
                    associated_dgs = associated_dgs.filter(is_active=True)
                    for single in associated_dgs:
                        delivery_statuses = OrderDeliveryStatus.objects.filter(delivery_guy=single,
                                                                               cod_status=constants.COD_STATUS_COLLECTED)
                        delivery_statuses_total = delivery_statuses.values('delivery_guy__user__username').\
                            annotate(sum_of_cod_collected=Sum('cod_collected_amount'))
                        associated_guys_detail_dict = associated_dgs_pending_cod_details(single)
                        if len(delivery_statuses) > 0:
                            associated_guys_detail_dict['cod_amount'] = delivery_statuses_total[0]['sum_of_cod_collected']
                        else:
                            associated_guys_detail_dict['cod_amount'] = 0
                        all_associated_dgs.append(associated_guys_detail_dict)
                    return response_with_payload(all_associated_dgs, None)
                except Exception as e:
                    error_message = 'No such Delivery Team Lead exists'
                    return response_error_with_message(error_message)
            else:
                error_message = 'This is not a DG team lead or this is a deactivated DG team lead'
                return response_error_with_message(error_message)
        else:
            return response_access_denied()

    @list_route(methods=['PUT'])
    @method_decorator(user_passes_test(active_check))
    def verify_transfer_to_tl(self, request):
        deliveries_list = []
        role = user_role(request.user)
        if role == constants.DELIVERY_GUY:
            delivery_guy = get_object_or_404(DeliveryGuy, user=request.user)
            # and delivery_guy.is_active is True
            if delivery_guy.is_teamlead is True:
                try:
                    transaction_uuid = request.data['transaction_id']
                    is_accepted = request.data['is_accepted']
                except Exception as e:
                    params = ['transaction_id', 'is_accepted']
                    return response_incomplete_parameters(params)
                try:
                    cod_transaction = CODTransaction.objects.get(transaction_uuid=transaction_uuid)
                except Exception as e:
                    error_message = 'No such transaction id found'
                    return response_error_with_message(error_message)

                dg_tl_id = cod_transaction.dg_tl_id
                if delivery_guy.id == dg_tl_id:
                    current_time = datetime.now(pytz.utc)
                    if cod_transaction.created_time_stamp is not None and cod_transaction.created_time_stamp < current_time:
                        time_diff = (current_time - cod_transaction.created_time_stamp)
                        total_seconds_worked = int(time_diff.total_seconds())
                        minutes = total_seconds_worked/60
                        dg = DeliveryGuy.objects.get(id=cod_transaction.dg_id)
                        if minutes < 5:
                            if is_accepted is True:
                                cod_transaction.verified_by_user = request.user
                                cod_transaction.verified_time_stamp = current_time
                                cod_transaction.transaction_status = constants.VERIFIED
                                cod_transaction.save()

                                deliveries = cod_transaction.deliveries
                                deliveries = eval(deliveries)
                                for single in deliveries:
                                    delivery = OrderDeliveryStatus.objects.get(id=single)
                                    delivery.cod_status = constants.COD_STATUS_TRANSFERRED_TO_TL
                                    delivery.save()
                                    cod_collected_transaction = delivery.cod_transactions.filter(transaction__title='CODCollected')
                                    if len(cod_collected_transaction) > 0:
                                        cod_transaction.transaction_status = constants.VERIFIED
                                        cod_transaction.save()
                                send_cod_status_notification(dg, delivery_guy, cod_transaction.cod_amount, is_accepted)
                                success_message = 'Transfer to TL verified'
                                return response_success_with_message(success_message)
                            else:
                                cod_transaction.verified_by_user = request.user
                                cod_transaction.verified_time_stamp = current_time
                                cod_transaction.transaction_status = constants.DECLINED
                                cod_transaction.save()
                                send_cod_status_notification(dg, delivery_guy, cod_transaction.cod_amount, is_accepted)
                                success_message = 'Transfer to TL declined'
                                return response_success_with_message(success_message)
                        else:
                            is_time_out = True
                            is_accepted = False
                            send_timeout_notification(dg, cod_transaction.cod_amount, is_time_out, is_accepted)
                            send_timeout_notification(delivery_guy, cod_transaction.cod_amount, is_time_out, is_accepted)
                            error_message = 'Transfer to TL transaction timed out'
                            return response_error_with_message(error_message)
                    else:
                        error_message = 'Transaction does not have an initiated time'
                        return response_error_with_message(error_message)
                else:
                    error_message = 'Transaction does not belong to this dg tl'
                    return response_error_with_message(error_message)
            else:
                error_message = 'This is not a DG team lead or this is a deactivated DG team lead'
                return response_error_with_message(error_message)
        else:
            return response_access_denied()

    # For DG or DG TL, Client sends delivery ids
    #  use this to cross check cod_amount accuracy
    @list_route(methods=['POST'])
    @method_decorator(user_passes_test(active_check))
    def bank_deposit_proof(self, request):
        role = user_role(request.user)
        if role == constants.DELIVERY_GUY:
            delivery_guy = get_object_or_404(DeliveryGuy, user=request.user)
            if delivery_guy.is_teamlead is True:
                dg_tl_id = delivery_guy.id
                dg_id = None
            else:
                dg_id = delivery_guy.id
                dg_tl_id = None
            cod_amount_calc = 0
            try:
                delivery_ids = request.data['delivery_ids']
                cod_amount = request.data['cod_amount']
                bank_deposit_proof = request.data['bank_deposit_proof']
                bank_receipt_number = request.data['bank_receipt_number']
            except Exception as e:
                params = ['delivery_ids', 'cod_amount', 'bank_deposit_proof', 'bank_receipt_number']
                return response_incomplete_parameters(params)

            try:
                for delivery_id in delivery_ids:
                    delivery = get_object_or_404(OrderDeliveryStatus, pk=delivery_id)
                    cod_amount_calc = cod_amount_calc + delivery.cod_collected_amount

                if cod_amount == cod_amount_calc:
                    transaction_uuid = uuid.uuid4()
                    cod_action = cod_actions(constants.COD_BANK_DEPOSITED_CODE)
                    proof = create_proof(bank_deposit_proof, request.user, cod_amount, bank_receipt_number)
                    cod_transaction = create_cod_transaction(cod_action, request.user, dg_id, dg_tl_id, cod_amount, transaction_uuid, delivery_ids)
                    cod_transaction.bank_deposit_proof = proof
                    cod_transaction.save()
                    for delivery_id in delivery_ids:
                        delivery_status = get_object_or_404(OrderDeliveryStatus, pk=delivery_id)
                        delivery_status.cod_status = constants.COD_STATUS_BANK_DEPOSITED
                        delivery_status.save()
                        add_cod_transaction_to_delivery(cod_transaction, delivery_status)
                    success_message = 'Bank Deposit transaction initiated successfully'
                    return response_success_with_message(success_message)
                else:
                    error_message = 'cod amount does not match with the total cod collection from all the deliveries selected'
                    return response_error_with_message(error_message)
            except Exception as e:
                error_message = 'Order not found'
                return response_error_with_message(error_message)
        else:
            return response_access_denied()


    # This api is to pull out all the bank deposit transactions(initiated)
    # dict of created by user, created date, receipt, current transaction status,
    # Implement pagination, give count of pages
    # give count of total bank deposit transactions
    @list_route(methods=['GET'])
    def bank_deposits_list(self, request):
        page = request.QUERY_PARAMS.get('page', '1')
        filter_dg_id = request.QUERY_PARAMS.get('dg_id', None)
        filter_start_date = request.QUERY_PARAMS.get('start_date', None)
        filter_end_date = request.QUERY_PARAMS.get('end_date', None)
        role = user_role(request.user)
        if role == constants.ACCOUNTS:
            bank_deposit_list = []
            accounts = get_object_or_404(Employee, user=request.user)
            cod_action = cod_actions(constants.COD_BANK_DEPOSITED_CODE)
            all_bank_deposit_cod_transactions = CODTransaction.objects.filter(transaction__title=cod_action, transaction_status=constants.INITIATED)
            if len(all_bank_deposit_cod_transactions) > 0:
                # DG FILTERING (optional)
                if filter_dg_id is not None:
                    dg = get_object_or_404(DeliveryGuy, pk = filter_dg_id)
                    if dg is not None:
                        all_bank_deposit_cod_transactions = all_bank_deposit_cod_transactions.filter(created_by_user=dg.user).distinct()

                # DATE FILTERING (optional)
                if filter_start_date is not None and filter_end_date is not None:
                    filter_start_date = parse_datetime(filter_start_date)
                    filter_start_date = filter_start_date + time_delta()
                    filter_start_date = filter_start_date.replace(day=filter_start_date.day, month=filter_start_date.month, year=filter_start_date.year, hour=00, minute=00, second=00)

                    filter_end_date = parse_datetime(filter_end_date)
                    filter_end_date = filter_end_date + time_delta()
                    filter_end_date = filter_end_date.replace(day=filter_end_date.day, month=filter_end_date.month, year=filter_end_date.year, hour=23, minute=59, second=00)
                    all_bank_deposit_cod_transactions = all_bank_deposit_cod_transactions.filter(created_time_stamp__gte=filter_start_date,
                                             created_time_stamp__lte=filter_end_date)
                # PAGINATION  ----------------------------------------------------------------
                total_bank_deposit_count = len(all_bank_deposit_cod_transactions)
                page = int(page)
                total_pages = int(total_bank_deposit_count / constants.PAGINATION_PAGE_SIZE) + 1
                if page > total_pages or page <= 0:
                    return response_invalid_pagenumber()
                else:
                    all_bank_deposit_cod_transactions = paginate(all_bank_deposit_cod_transactions, page)
                # ----------------------------------------------------------------------------
                for single in all_bank_deposit_cod_transactions:
                    all_bank_deposit_cod_transactions_dict = all_bank_deposit_cod_transactions_list(single)
                    all_bank_deposit_cod_transactions_dict['receipt_number'] = single.bank_deposit_proof.receipt_number
                    if single.bank_deposit_proof is not None:
                        pic = ProofOfBankDeposit.objects.get(id=single.bank_deposit_proof.id)
                        if pic.receipt is not None:
                            all_bank_deposit_cod_transactions_dict['receipt'] = pic.receipt.name
                        else:
                            all_bank_deposit_cod_transactions_dict['receipt'] = None
                    bank_deposit_list.append(all_bank_deposit_cod_transactions_dict)
                    bank_deposit_list.sort(key=lambda item: item['created_time_stamp'], reverse=True)
                pagination_count_dict = pagination_count_bank_deposit()
                pagination_count_dict['total_pages'] = total_pages
                pagination_count_dict['total_count'] = total_bank_deposit_count
                pagination_count_dict['all_transactions'] = bank_deposit_list
                return response_with_payload(pagination_count_dict, None)
            else:
                error_message = 'No Bank Deposit COD transaction found.'
                return response_error_with_message(error_message)
        else:
            return response_access_denied()

    # Api for particular bank deposit transaction to be approved/declined by accounts
    # Accounts should be mentioning some money under pending salary deduction, for this DG(in case of declined)
    # also send sms to dg with this salary deduction, send email notify to accounts and operations regarding this
    # update all the associated orders and proof for this transaction as well
    @list_route(methods=['PUT'])
    def verify_bank_deposit(self, request):
        role = user_role(request.user)
        current_time = datetime.now(pytz.utc)
        if role == constants.ACCOUNTS:
            accounts = get_object_or_404(Employee, user=request.user)
            try:
                transaction_id = request.data['transaction_id']
                is_accepted = request.data['is_accepted']
                pending_salary_deduction = request.data.get('pending_salary_deduction')
            except Exception as e:
                params = ['transaction_id', 'is_accepted', 'pending_salary_deduction(optional)']
                return response_incomplete_parameters(params)
            try:
                bank_deposit = CODTransaction.objects.get(transaction_uuid=transaction_id)
            except Exception as e:
                error_message = 'No such Bank Deposit COD transaction found.'
                return response_error_with_message(error_message)
            if bank_deposit.transaction_status == constants.INITIATED:
                if is_accepted is True:
                    receipt_number = bank_deposit.bank_deposit_proof.receipt_number
                    if receipt_number is not None:
                        bank_deposit.bank_deposit_proof.proof_status = constants.VERIFIED
                        bank_deposit.bank_deposit_proof.updated_by_user = request.user
                        bank_deposit.bank_deposit_proof.updated_time_stamp = current_time
                        bank_deposit.bank_deposit_proof.save()
                    else:
                        error_message = 'No Receipt found.'
                        return response_error_with_message(error_message)

                    bank_deposit.verified_by_user = request.user
                    bank_deposit.verified_time_stamp = current_time
                    bank_deposit.transaction_status = constants.VERIFIED
                    bank_deposit.save()
                    success_message = 'Bank Deposit transaction verified successfully'
                    return response_success_with_message(success_message)
                else:
                    receipt_number = bank_deposit.bank_deposit_proof.receipt_number
                    if receipt_number is not None:
                        bank_deposit.bank_deposit_proof.proof_status = constants.DECLINED
                        bank_deposit.bank_deposit_proof.updated_by_user = request.user
                        bank_deposit.bank_deposit_proof.updated_time_stamp = current_time
                        bank_deposit.bank_deposit_proof.save()
                    else:
                        error_message = 'No Receipt found.'
                        return response_error_with_message(error_message)

                    bank_deposit.verified_by_user = request.user
                    bank_deposit.verified_time_stamp = current_time
                    bank_deposit.transaction_status = constants.DECLINED
                    bank_deposit.save()
                    # Salary deduction will be applied to the person initiating the bank deposit cod transaction and not the DG associated the order directly
                    transaction_initiated_by = bank_deposit.created_by_user
                    dg = DeliveryGuy.objects.get(user__username=transaction_initiated_by)
                    current_deduction = dg.pending_salary_deduction
                    if pending_salary_deduction is not None:
                        bank_deposit.salary_deduction = pending_salary_deduction
                        bank_deposit.save()
                        dg.pending_salary_deduction = current_deduction + pending_salary_deduction
                        dg.save()
                        dg_phone_number = dg.user.username
                        deliveries = bank_deposit.deliveries
                        deliveries = eval(deliveries)
                        orders = str(deliveries).strip('[]')
                        orders = str(orders).strip('u')
                        message = 'Dear %s, with respect to your bank deposit of orders %s, ' \
                                  'there is a %.2f Rs deduction in your next month\'s salary, as you have deposited less' \
                                  % (dg.user.first_name, orders, pending_salary_deduction)
                        send_sms(dg_phone_number, message)
                        send_salary_deduction_email(dg.user.first_name, orders, bank_deposit.cod_amount, pending_salary_deduction)
                    success_message = 'Bank Deposit transaction declined successfully'
                    return response_success_with_message(success_message)
            else:
                error_message = 'This bank deposit transaction is already updated'
                return response_error_with_message(error_message)
        else:
            return response_access_denied()

    # api to retrieve all verified bank deposit transactions
    # also send vendor id in the response
    # implement filter by dates(start date and end date)
    # implement filter by vendor_id
    # implement pagination and return count of such transactions
    # when accounts transfers to client, change the transaction
    @list_route(methods=['GET'])
    def verified_bank_deposits_list(self, request):
        role = user_role(request.user)
        page = request.QUERY_PARAMS.get('page', 1)
        search_query = request.QUERY_PARAMS.get('search', None)
        filter_vendor_id = request.QUERY_PARAMS.get('vendor_id', None)
        filter_start_date = request.QUERY_PARAMS.get('start_date', None)
        filter_end_date = request.QUERY_PARAMS.get('end_date', None)
        if role == constants.ACCOUNTS or role == constants.SALES:
            all_transactions = []
            emp = get_object_or_404(Employee, user=request.user)
            cod_action = cod_actions(constants.COD_BANK_DEPOSITED_CODE)
            verified_bank_deposits = CODTransaction.objects.filter(Q(transaction__title=cod_action, transaction_status=constants.VERIFIED) |
                                                                   Q(transaction__title=cod_action, transaction_status=constants.DECLINED))
            verified_bank_deposits = verified_bank_deposits.filter(orderdeliverystatus__cod_status=constants.COD_STATUS_BANK_DEPOSITED).distinct()
            if len(verified_bank_deposits) > 0:
                # DATE FILTERING (optional)
                if filter_start_date is not None and filter_end_date is not None:
                    filter_start_date = parse_datetime(filter_start_date)
                    filter_start_date = filter_start_date + time_delta()
                    filter_start_date = filter_start_date.replace(day=filter_start_date.day, month=filter_start_date.month, year=filter_start_date.year, hour=00, minute=00, second=00)

                    filter_end_date = parse_datetime(filter_end_date)
                    filter_end_date = filter_end_date + time_delta()
                    filter_end_date = filter_end_date.replace(day=filter_end_date.day, month=filter_end_date.month, year=filter_end_date.year, hour=23, minute=59, second=00)
                    verified_bank_deposits = verified_bank_deposits.filter(verified_time_stamp__gte=filter_start_date,
                                                                           verified_time_stamp__lte=filter_end_date)

                # SEARCH KEYWORD FILTERING (optional)
                if search_query is not None:
                    verified_bank_deposits = search_cod_transactions(request.user, search_query)

                total_verified_bank_deposits_count = len(verified_bank_deposits)
                page = int(page)
                total_pages = int(total_verified_bank_deposits_count / constants.PAGINATION_PAGE_SIZE) + 1
                if page > total_pages or page <= 0:
                    return response_invalid_pagenumber()
                else:
                    verified_bank_deposits = paginate(verified_bank_deposits, page)

                # For filtered queryset as well as non filtered queryset
                # populate dictionary data with date, transaction id, transaction status
                for single_bd in verified_bank_deposits:
                    deliveries = single_bd.deliveries
                    deliveries = eval(deliveries)
                    for single_delivery in deliveries:
                        delivery = OrderDeliveryStatus.objects.get(id=single_delivery)
                        verified_bank_deposit_dict = verified_bank_deposit_list(single_bd, delivery)
                        all_transactions.append(verified_bank_deposit_dict)
                        all_transactions.sort(key=lambda item: item['verified_time_stamp'], reverse=True)
                if filter_vendor_id is not None:
                    vendor = get_object_or_404(Vendor, pk=filter_vendor_id)
                    if vendor is not None:
                        all_transactions = filter(lambda record: record['vendor_name'] == vendor.store_name, all_transactions)
                        total_verified_bank_deposits_count = len(all_transactions)
                pagination_count_dict = pagination_count_bank_deposit()
                pagination_count_dict['total_pages'] = total_pages
                pagination_count_dict['total_count'] = total_verified_bank_deposits_count
                pagination_count_dict['all_transactions'] = all_transactions
                return response_with_payload(pagination_count_dict, None)
            else:
                total_verified_bank_deposits_count = len(verified_bank_deposits)
                total_pages = int(total_verified_bank_deposits_count / constants.PAGINATION_PAGE_SIZE) + 1
                pagination_count_dict = pagination_count_bank_deposit()
                pagination_count_dict['total_pages'] = total_pages
                pagination_count_dict['total_count'] = total_verified_bank_deposits_count
                pagination_count_dict['all_transactions'] = all_transactions
                return response_with_payload(pagination_count_dict, None)
        else:
            return response_access_denied()

    # Client sends list of delivery_ids, total_cod_amount transferred to client, vendor id, utr number
    # Validations implememted:
    # 1. If the delivery_ids belong to the Vendor
    # 2. Checking the cod total is same as the cod transferred
    @list_route(methods=['POST'])
    def transfer_to_client(self, request):
        role = user_role(request.user)
        cod_amount_calc = 0
        if role == constants.ACCOUNTS:
            try:
                delivery_id_list = request.data['delivery_ids']
                total_cod_transferred = request.data['total_cod_transferred']
                vendor_id = request.data['vendor_id']
                utr_number = request.data['utr_number']
            except Exception as e:
                params = ['delivery_ids', 'total_cod_transferred', 'vendor_id', 'utr_number']
                return response_incomplete_parameters(params)

            vendor = get_object_or_404(Vendor, pk=vendor_id)

            for single in delivery_id_list:
                delivery = OrderDeliveryStatus.objects.get(id=single)
                if delivery.order.vendor == vendor:
                    pass
                else:
                    error_message = 'This order does not belong to the choosen Vendor'
                    return response_error_with_message(error_message)
                cod_amount_calc = cod_amount_calc + delivery.cod_collected_amount

            if cod_amount_calc == total_cod_transferred:
                transaction_uuid = uuid.uuid4()
                cod_action = cod_actions(constants.COD_TRANSFERRED_TO_CLIENT_CODE)
                cod_transferred_to_client = create_cod_transaction(cod_action, request.user, None, None,
                                                                   total_cod_transferred, transaction_uuid, delivery_id_list)
                cod_transferred_to_client.vendor = vendor
                cod_transferred_to_client.utr_number = utr_number
                cod_transferred_to_client.save()

                for single in delivery_id_list:
                    delivery = OrderDeliveryStatus.objects.get(id=single)
                    delivery.cod_status = constants.COD_STATUS_TRANSFERRED_TO_CLIENT
                    add_cod_transaction_to_delivery(cod_transferred_to_client, delivery)
                    delivery.save()
                success_message = 'COD Transfer to Client is successful'
                return response_success_with_message(success_message)
            else:
                error_message = 'Total cod amount from the select orders does not match with the total_cod_transferred'
                return response_error_with_message(error_message)
        else:
            return response_access_denied()

    # Transaction History api
    # Return the transactions history for a particular DG
    # Implement Pagination
    @list_route(methods=['GET'])
    @method_decorator(user_passes_test(active_check))
    def dg_transaction_history(self, request):
        role = user_role(request.user)
        page = request.QUERY_PARAMS.get('page', None)
        if role == constants.DELIVERY_GUY:
            all_transactions = []
            delivery_guy = get_object_or_404(DeliveryGuy, user=request.user)
            history = CODTransaction.objects.filter(created_by_user=delivery_guy.user)
            history = history.filter(Q(transaction__code=constants.COD_TRANSFERRED_TO_TL_CODE) |
                                     Q(transaction__code=constants.COD_BANK_DEPOSITED_CODE))

            if len(history) > 0:
                total_history_count = len(history)
                # PAGINATION  ----------------------------------------------------------------
                if page is not None:
                    page = int(page)
                else:
                    page = 1
                total_pages = int(total_history_count / constants.PAGINATION_PAGE_SIZE) + 1
                if page > total_pages or page <= 0:
                    return response_invalid_pagenumber()
                else:
                    history = paginate(history, page)

                for single in history:
                    transaction_history_dict = transaction_history(single)
                    if single.transaction.code == constants.COD_TRANSFERRED_TO_TL_CODE:
                        transaction_history_dict['transaction_type'] = "Transfer to TL"
                    elif single.transaction.code == constants.COD_BANK_DEPOSITED_CODE:
                        transaction_history_dict['transaction_type'] = "Bank Deposit"
                    else:
                        pass
                    all_transactions.append(transaction_history_dict)
                    all_transactions.sort(key=lambda item: item['date'], reverse=True)
                pagination_count_dict = pagination_count_bank_deposit()
                pagination_count_dict['total_pages'] = total_pages
                pagination_count_dict['total_count'] = total_history_count
                pagination_count_dict['all_transactions'] = all_transactions
                return response_with_payload(pagination_count_dict, None)
            else:
                error_message = 'No transactions found'
                return response_error_with_message(error_message)
        else:
            return response_access_denied()

    @list_route(methods=['GET'])
    def vendor_transaction_history(self, request):
        role = user_role(request.user)
        page = request.QUERY_PARAMS.get('page', None)
        search_query = request.QUERY_PARAMS.get('search', None)
        filter_vendor_id = request.QUERY_PARAMS.get('vendor_id', None)
        filter_start_date = request.QUERY_PARAMS.get('start_date', None)
        filter_end_date = request.QUERY_PARAMS.get('end_date', None)
        if role == constants.ACCOUNTS or role == constants.SALES:
            all_transactions = []
            history = CODTransaction.objects.filter(transaction__code=constants.COD_TRANSFERRED_TO_CLIENT_CODE)
            if len(history) > 0:
                # DATE FILTERING (optional)
                if filter_start_date is not None and filter_end_date is not None:
                    filter_start_date = parse_datetime(filter_start_date)
                    filter_start_date = filter_start_date + time_delta()
                    filter_start_date = filter_start_date.replace(day=filter_start_date.day, month=filter_start_date.month, year=filter_start_date.year, hour=00, minute=00, second=00)

                    filter_end_date = parse_datetime(filter_end_date)
                    filter_end_date = filter_end_date + time_delta()
                    filter_end_date = filter_end_date.replace(day=filter_end_date.day, month=filter_end_date.month, year=filter_end_date.year, hour=23, minute=59, second=00)
                    history = history.filter(created_time_stamp__gte=filter_start_date,
                                             created_time_stamp__lte=filter_end_date)
                # VENDOR FILTERING (optional)
                if filter_vendor_id is not None:
                    vendor = get_object_or_404(Vendor, pk=filter_vendor_id)
                    if vendor is not None:
                        history = history.filter(orderdeliverystatus__order__vendor=vendor).distinct()

                # SEARCH KEYWORD FILTERING (optional)
                if search_query is not None:
                    history = search_cod_transactions(request.user, search_query)

                total_history_count = len(history)

                # PAGINATION  ----------------------------------------------------------------
                if page is not None:
                    page = int(page)
                else:
                    page = 1

                total_pages = int(total_history_count / constants.PAGINATION_PAGE_SIZE) + 1
                if page > total_pages or page <= 0:
                    return response_invalid_pagenumber()
                else:
                    history = paginate(history, page)

                for single in history:
                    deliveries_list = []
                    vendor_transaction_history_dict = vendor_transaction_history(single)
                    deliveries = single.deliveries
                    deliveries = eval(deliveries)
                    for single_delivery in deliveries:
                        delivery = OrderDeliveryStatus.objects.get(id=single_delivery)
                        per_order_dict = per_order_list(delivery)
                        deliveries_list.append(per_order_dict)
                    vendor_transaction_history_dict['deliveries'] = deliveries_list
                    all_transactions.append(vendor_transaction_history_dict)
                    all_transactions.sort(key=lambda item: item['date'], reverse=True)
                pagination_count_dict = pagination_count_bank_deposit()
                pagination_count_dict['total_pages'] = total_pages
                pagination_count_dict['total_count'] = total_history_count
                pagination_count_dict['all_transactions'] = all_transactions
                return response_with_payload(pagination_count_dict, None)
            else:
                error_message = 'No transactions found'
                return response_error_with_message(error_message)
        else:
            return response_access_denied()
