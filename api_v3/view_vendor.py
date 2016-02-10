from datetime import datetime
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from rest_framework import authentication
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.exceptions import APIException

from api_v3 import constants
from api_v3.utils import user_role, send_email, send_sms, is_userexists, create_token, paginate
from api_v3.view_address import create_address
from api_v3.views import IsAuthenticatedOrWriteOnly
from yourguy.models import Vendor, VendorAgent, User, Industry
from django.db.models import Q
import json

from api_v3.utils import response_access_denied, response_with_payload, response_error_with_message, response_success_with_message, response_invalid_pagenumber, response_incomplete_parameters

def vendor_detail_dict(vendor):
    vendor_dict = {
        'id': vendor.id,
        'name': vendor.store_name,
        'email': vendor.email,
        'phone_number': vendor.phone_number,
        'alternate_phone_number': vendor.alternate_phone_number,
        'is_retail': vendor.is_retail,
        'website_url': vendor.website_url,
        'notes': vendor.notes,
        'is_verified': vendor.verified,
        "addresses": []
    }

    all_addresses = vendor.addresses.all()
    for address in all_addresses:
        adr_dict = {
            "id": address.id,
            "full_address": address.full_address,
            "pin_code": address.pin_code
        }
        if address.landmark is not None:
            adr_dict['landmark'] = address.landmark
        vendor_dict['addresses'].append(adr_dict)

    return vendor_dict


def vendor_list_dict(vendor):
    vendor_dict = {
        'id': vendor.id,
        'name': vendor.store_name,
        'is_verified': vendor.verified,
        'is_retail': vendor.is_retail
    }
    return vendor_dict


class VendorViewSet(viewsets.ModelViewSet):
    """
    Vendor viewset that provides the standard actions
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticatedOrWriteOnly]
    queryset = Vendor.objects.all()

    def destroy(self, request):
        return response_access_denied()

    def retrieve(self, request, pk=None):
        vendor = get_object_or_404(Vendor, id=pk)
        role = user_role(request.user)
        can_respond = False

        if role == constants.VENDOR:
            vendor_agent = get_object_or_404(VendorAgent, user=request.user)
            if vendor.id == vendor_agent.vendor.id:
                can_respond = True
            else:
                can_respond = False
        else:
            can_respond = True

        if can_respond:
            vendor_detail = vendor_detail_dict(vendor)
            content = {'data': vendor_detail}
            return response_with_payload(content, None)
        else:
            return response_access_denied()

    def list(self, request):
        role = user_role(request.user)
        is_verified = request.QUERY_PARAMS.get('is_verified', None)
        search = request.QUERY_PARAMS.get('search', None)
        page = request.QUERY_PARAMS.get('page', '1')

        if (role == constants.SALES) or (role == constants.OPERATIONS):
            all_vendors = Vendor.objects.all().order_by(Lower('store_name'))
            if search is not None:
                all_vendors = all_vendors.filter(Q(store_name__icontains=search))

            if is_verified is not None:
                is_verified = json.loads(is_verified.lower())
                if is_verified is True:
                    all_vendors = all_vendors.filter(verified=True)
                else:
                    all_vendors = all_vendors.filter(verified=False)
            # PAGINATION  ----------------------------------------------------------------
            total_vendor_count = len(all_vendors)
            page = int(page)
            total_pages = int(total_vendor_count / constants.PAGINATION_PAGE_SIZE) + 1
            if page > total_pages or page <= 0:
                return response_invalid_pagenumber()
            else:
                result_vendors = paginate(all_vendors, page)
            # ----------------------------------------------------------------------------

            result = []
            for vendor in result_vendors:
                vendor_dict = vendor_list_dict(vendor)
                result.append(vendor_dict)

            response_content = {
                "data": result,
                "total_pages": total_pages,
                "total_vendor_count": total_vendor_count
            }
            return response_with_payload(response_content, None)
        elif role == constants.VENDOR:
            vendor_agent = get_object_or_404(VendorAgent, user=request.user)
            vendor_detail = vendor_detail_dict(vendor_agent.vendor)
            content = {'data': vendor_detail}
            return response_with_payload(content, None)
        else:
            return response_access_denied()

    @detail_route(methods=['post'])
    def request_vendor_account(self, request, pk=None):
        try:
            store_name = request.data['store_name']
            phone_number = request.data['phone_number']
            email = request.data['email']
            full_address = request.data['full_address']
            pin_code = request.data['pin_code']
            landmark = request.data.get('landmark')
        except APIException:
            parameters = ['store_name', 'phone_number', 'email', 'full_address', 'pin_code', 'landmark(optional)']
            return response_incomplete_parameters(parameters)

        # CHECK IF THE VENDOR HAS ALREADY REQUESTED FOR AN ACCOUNT
        existing_vendors = Vendor.objects.filter(phone_number=phone_number)
        existing_users = User.objects.filter(username=phone_number)
        if len(existing_vendors) > 0 or len(existing_users) > 0:
            error_message = 'Vendor with similar details already exists'
            return response_error_with_message(error_message)

        # CREATING NEW VENDOR
        new_vendor = Vendor.objects.create(store_name=store_name, email=email, phone_number=phone_number)
        new_address = create_address(full_address, pin_code, landmark)
        new_vendor.addresses.add(new_address)
        new_vendor.save()

        # SEND EMAIL TO SALES
        try:
            approval_link = 'http://app.yourguy.in/#/home/vendor/{}'.format(new_vendor.id)
            subject = 'YourGuy: New Vendor Account Request'
            body = constants.VENDOR_ACCOUNT_REQUESTED_MESSAGE_SALES.format(store_name, phone_number, email,
                                                                           full_address, pin_code, approval_link)
            send_email(constants.SALES_EMAIL, subject, body)
        except Exception as e:
            pass

        success_message = 'Thank you! We have received your request. Our sales team will contact you soon.'
        return response_success_with_message(success_message)

    @detail_route(methods=['put'])
    def approve(self, request, pk):
        role = user_role(request.user)
        vendor = get_object_or_404(Vendor, pk=pk)
        notes = request.data.get('notes')
        is_retail = request.data.get('is_retail')
        industry_ids = request.data.get('industry_ids')
        approved_by = request.user
        # pricing = request.data.get('pricing')
        # pan = request.data.get('pan')
        if role == constants.SALES:
            try:
                username = vendor.phone_number
                password = vendor.store_name.replace(" ", "")
                password = password.lower()

                if is_userexists(username):
                    user = get_object_or_404(User, username=username)
                    user.set_password(password)
                    user.save()
                else:
                    user = User.objects.create_user(username=username, password=password)

                token = create_token(user, constants.VENDOR)
                vendor_agent = VendorAgent.objects.create(user=user, vendor=vendor)

                vendor.verified = True

                if notes is not None:
                    vendor.notes = notes

                if is_retail is not None:
                    vendor.is_retail = is_retail

                if approved_by is not None:
                    vendor.approved_by = approved_by

                try:
                    if industry_ids is not None:
                        for industry_id in industry_ids:
                            industry = get_object_or_404(Industry, pk=industry_id)
                            vendor.industries.add(industry)
                except Exception as e:
                    pass

                vendor.save()
            except Exception as e:
                error_message = 'An error occurred creating the account. Please try again'
                return response_error_with_message(error_message)

            subject = 'YourGuy: Account created for {}'.format(vendor.store_name)
            customer_message = constants.VENDOR_ACCOUNT_APPROVED_MESSAGE.format(vendor.phone_number, password)
            customer_emails = [vendor.email]
            send_email(customer_emails, subject, customer_message)
            send_sms(vendor.phone_number, customer_message)

            sales_message = constants.VENDOR_ACCOUNT_APPROVED_MESSAGE_SALES.format(vendor.store_name)
            send_email(constants.SALES_EMAIL, subject, sales_message)

            success_message = 'Your account credentials has been sent via email and SMS.'
            return response_success_with_message(success_message)
        else:
            return response_access_denied()