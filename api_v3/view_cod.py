from datetime import datetime
from django.db.models import Sum
from api_v3.utils import cod_actions, response_access_denied, get_object_or_404, \
    response_error_with_message, response_with_payload, response_incomplete_parameters, response_success_with_message
from api_v3 import constants
from yourguy.models import CODTransaction, DeliveryGuy, OrderDeliveryStatus, DeliveryTeamLead
from rest_framework import authentication, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated
from api_v3.utils import user_role
import uuid
import pytz


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


def associated_dgs_collections_dict(dg):
    associated_dgs_collections = {
        'dg_id': dg.id,
        'dg_name': dg.user.first_name,
        'cod_transferred': None,
        'transferred_time': None
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
    dg_tl_id = dg.id
    delivery_statuses = OrderDeliveryStatus.objects.filter(delivery_guy=dg,
                                                           cod_status=constants.COD_STATUS_COLLECTED)
    delivery_statuses_total = delivery_statuses.values('delivery_guy__user__username').\
        annotate(sum_of_cod_collected=Sum('cod_collected_amount'))
    balance_amount = None
    if len(delivery_statuses_total) > 0:
        balance_amount = delivery_statuses_total[0]['sum_of_cod_collected']
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
    return balance_amount


class CODViewSet(viewsets.ViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @list_route(methods=['GET'])
    def cod_balance(self, request):
        role = user_role(request.user)
        if role == constants.DELIVERY_GUY:
            dg = get_object_or_404(DeliveryGuy, user=request.user)
            if dg.is_active is True:
                balance_amount = cod_balance_calculation(dg)
                if balance_amount is None:
                    balance_amount = 0
                else:
                    pass
                return response_with_payload(balance_amount, None)
            else:
                error_message = 'This is a deactivated dg'
                return response_error_with_message(error_message)
        else:
            return response_access_denied()


    # for dg tl, order object if he is the assigned dg(order id, cod amount collected, customer name, vendor name, delivery date time)
    # dg object of his associated dg who has transferred the cod(dg id, dg name, transaction date time,
    # for dg, filter OrderDeliveryStatus for cod status(this is cumulative cod not yet transferred to tl)
    # for each order(order id, cod amount collected, customer name, vendor name, delivery date time)
    @list_route(methods=['GET'])
    def collections(self, request):
        role = user_role(request.user)
        if role == constants.DELIVERY_GUY:
            dg = get_object_or_404(DeliveryGuy, user=request.user)
            if dg.is_active is True:
                if dg.is_teamlead is True:
                    dg_tl_id = dg.id
                    deliveries = []
                    tl_collections = []
                    asso_dg_collections = []
                    dg_tl_collections = dg_tl_collections_dict()
                    delivery_statuses = OrderDeliveryStatus.objects.filter(delivery_guy=dg,
                                                                           cod_status=constants.COD_STATUS_COLLECTED)
                    for single in delivery_statuses:
                        dg_collections = dg_collections_dict(single)
                        tl_collections.append(dg_collections)
                    dg_tl_collections['tls_collections'] = tl_collections

                    balance_amount = cod_balance_calculation(dg)

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
                            associated_dgs_collections = associated_dgs_collections_dict(single_dg)
                            associated_dgs_collections['cod_transferred'] = delivery_statuses[0]['sum_of_cod_collected']
                            cod_action = cod_actions(constants.COD_TRANSFERRED_TO_TL_CODE)
                            cod_transaction = CODTransaction.objects.filter(transaction__title=cod_action,
                                                                            transaction_status=constants.VERIFIED,
                                                                            cod_amount=delivery_statuses[0]['sum_of_cod_collected'],
                                                                            deliveries__in=deliveries)
                            if len(cod_transaction) > 0 and cod_transaction[0].verified_time_stamp is not None:
                                associated_dgs_collections['transferred_time'] = cod_transaction[0].verified_time_stamp
                            else:
                                associated_dgs_collections['transferred_time'] = None

                            asso_dg_collections.append(associated_dgs_collections)
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
                        dg_total_cod_amount['dg_collections'] = dg_entire_collections
                        return response_with_payload(dg_total_cod_amount, None)
                    else:
                        error_message = 'No COD collection pending to transfer to TL'
                        return response_error_with_message(error_message)
            else:
                error_message = 'This is a deactivated dg'
                return response_error_with_message(error_message)
        else:
            return response_access_denied()

    @list_route(methods=['POST'])
    def qr_code(self, request):
        role = user_role(request.user)
        if role == constants.DELIVERY_GUY:
            dg = get_object_or_404(DeliveryGuy, user=request.user)
            dg_id = dg.id
            if dg.is_active is True and dg.is_teamlead is False:
                try:
                    dg_tl_id = request.data['dg_tl_id']
                    cod_amount = request.data['cod_amount']
                    delivery_ids = request.data['delivery_ids']
                except Exception as e:
                    params = ['dg_tl_id', 'cod_amount', 'order_ids']
                    return response_incomplete_parameters(params)
                transaction_uuid = uuid.uuid4()
                cod_action = cod_actions(constants.COD_TRANSFERRED_TO_TL_CODE)
                cod_transaction = create_cod_transaction(cod_action, request.user, dg_id, dg_tl_id, cod_amount, transaction_uuid, delivery_ids)
                for delivery_id in delivery_ids:
                    delivery_status = get_object_or_404(OrderDeliveryStatus, pk=delivery_id)
                    add_cod_transaction_to_delivery(cod_transaction, delivery_status)
                content = {'transaction_id': transaction_uuid}
                return response_with_payload(content, None)
            else:
                error_message = 'This is a deactivated dg OR a DG TL'
                return response_error_with_message(error_message)
        else:
            return response_access_denied()

    @list_route(methods=['GET'])
    def associated_dgs_collections(self, request):
        all_associated_dgs = []
        role = user_role(request.user)
        if role == constants.DELIVERY_GUY:
            delivery_guy = get_object_or_404(DeliveryGuy, user=request.user)
            if delivery_guy.is_teamlead is True and delivery_guy.is_active is True:
                try:
                    delivery_guy_tl = DeliveryTeamLead.objects.get(delivery_guy=delivery_guy)
                    associated_dgs = delivery_guy_tl.associate_delivery_guys.all()
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