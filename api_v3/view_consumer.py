from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from rest_framework import authentication, status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api_v3 import constants
from api_v3.utils import user_role, paginate, is_userexists, is_consumerexists
from yourguy.models import Consumer, VendorAgent


def create_consumer(username, phone_number, address):
    # FETCH USER WITH PHONE NUMBER -------------------------------
    if is_userexists(phone_number) is False:
        user = User.objects.create(username=phone_number, first_name=username, password='')
    else:
        user = get_object_or_404(User, username=phone_number)
    # -------------------------------------------------------------

    if is_consumerexists(user) is False:
        consumer = Consumer.objects.create(user=user)
        consumer.addresses.add(address)
        consumer.save()
    else:
        consumer = get_object_or_404(Consumer, user=user)

    return consumer


def consumer_list_dict(consumer):
    consumer_dict = {
        'id': consumer.id,
        'name': consumer.user.first_name,
        'phone_number': consumer.user.username
    }
    return consumer_dict


def consumer_detail_dict(consumer):
    consumer_dict = {
        'id': consumer.id,
        'name': consumer.user.first_name,
        'phone_number': consumer.user.username,
        "addresses": []
    }

    all_addresses = consumer.addresses.all()
    for address in all_addresses:
        adr_dict = {
            "id": address.id,
            "full_address": address.full_address,
            "landmark": address.landmark,
            "pin_code": address.pin_code
        }
        consumer_dict['addresses'].append(adr_dict)

    return consumer_dict


class ConsumerViewSet(viewsets.ModelViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Consumer.objects.all()

    def destroy(self, request, pk):
        role = user_role(request.user)
        if role == constants.VENDOR:
            vendor_agent = get_object_or_404(VendorAgent, user=request.user)
            vendor = vendor_agent.vendor
            consumer = get_object_or_404(Consumer, pk=pk)
            consumer.associated_vendor.remove(vendor)

            content = {
                'description': 'Customer removed.'
            }
            return Response(content, status=status.HTTP_200_OK)

        else:
            content = {
                'description': 'You don\'t have permissions to remove the customer.'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        consumer = get_object_or_404(Consumer, id=pk)
        role = user_role(request.user)
        if role == constants.VENDOR:
            vendor_agent = get_object_or_404(VendorAgent, user=request.user)
            all_associated_vendors = consumer.associated_vendor.all()
            is_consumer_associated_to_vendor = False
            for vendor in all_associated_vendors:
                if vendor.id == vendor_agent.vendor.id:
                    is_consumer_associated_to_vendor = True
                    break
            if is_consumer_associated_to_vendor:
                detail_dict = consumer_detail_dict(consumer)
                content = {
                    "data": detail_dict
                }
                return Response(content, status=status.HTTP_200_OK)
            else:
                content = {
                    'error': 'You don\'t have permissions to view this consumer.'
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            content = {
                'error': 'You don\'t have permissions to view this consumer.'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        page = self.request.QUERY_PARAMS.get('page', None)
        search_query = request.QUERY_PARAMS.get('search', None)
        addresses_required = False

        if page is not None:
            page = int(page)
        else:
            page = 1

        role = user_role(request.user)
        if role == constants.VENDOR:
            vendor_agent = get_object_or_404(VendorAgent, user=request.user)
            total_consumers_of_vendor = Consumer.objects.filter(associated_vendor=vendor_agent.vendor).order_by(
                Lower('user__first_name'))

            # SEARCH KEYWORD FILTERING -------------------------------------------------
            if search_query is not None:
                total_consumers_of_vendor = total_consumers_of_vendor.filter(
                    Q(user__first_name__icontains=search_query) | Q(user__username=search_query))
                addresses_required = True
            # --------------------------------------------------------------------------

            # FETCH ADDRESSES OF CUSTOMER ----------------------------------------------
            if addresses_required:
                total_consumers_of_vendor = total_consumers_of_vendor.prefetch_related('addresses')
            # --------------------------------------------------------------------------

            # PAGINATE -----------------------------------------------------------------
            total_customers_count = len(total_consumers_of_vendor)
            total_pages = int(total_customers_count / constants.PAGINATION_PAGE_SIZE) + 1

            if page > total_pages or page <= 0:
                content = {
                    "error": "Invalid page number"
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            else:
                customers = paginate(total_consumers_of_vendor, page)

            result = []
            for consumer in customers:
                if addresses_required:
                    consumer_dict = consumer_detail_dict(consumer)
                else:
                    consumer_dict = consumer_list_dict(consumer)
                result.append(consumer_dict)

            content = {
                "data": result, "total_pages": total_pages
            }
            return Response(content, status=status.HTTP_200_OK)
        else:
            content = {
                'error': 'You don\'t have permissions to view all Consumers'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
