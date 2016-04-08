from django.contrib.auth.models import User, Group
from rest_framework import authentication
from rest_framework import viewsets
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated

from api_v3 import constants
from api_v3.utils import user_role, is_userexists, create_token, is_vendoragentexists, log_exception
from yourguy.models import VendorAgent, Vendor
from api_v3.utils import response_access_denied, response_with_payload, response_error_with_message, response_success_with_message, response_invalid_pagenumber, response_incomplete_parameters

def vendor_agent_list_dict(agent):
    vendor_agent_dict = {
        'vendor': agent.vendor.store_name,
        'agent': agent.user.first_name
    }
    return vendor_agent_dict


class VendorAgentViewSet(viewsets.ModelViewSet):
    """
    VendorAgent viewset that provides the standard actions
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = VendorAgent.objects.all()

    def list(self, request):
        role = user_role(request.user)
        if role == constants.VENDOR:
            vendor_agent = VendorAgent.objects.get(user=request.user)
            vendor_agents_of_vendor = VendorAgent.objects.filter(vendor=vendor_agent.vendor)
            vendoragents = []
            for agent in vendor_agents_of_vendor:
                vendor_agent_dict = vendor_agent_list_dict(agent)
                vendoragents.append(vendor_agent_dict)

            content = {"vendor_agents": vendor_agent_dict}
            return response_with_payload(content, None)
        else:
            return response_access_denied()

    def create(self, request):
        role = user_role(request.user)
        if (role == constants.VENDOR) or (role == constants.SALES):
            try:
                vendor_id = request.data['vendor_id']
                phone_number = request.data['phone_number']
                name = request.data.get('name')
                password = request.data['password']
            except APIException:
                params = ['vendor_id', 'phone_number', 'name', 'password']
                return response_incomplete_parameters(params)

            try:
                vendor = Vendor.objects.get(id=vendor_id)
            except APIException:
                error_message = 'Vendor with id doesnt exists'
                return response_error_with_message(error_message)

            if is_userexists(phone_number) is True:
                user = User.objects.get(username=phone_number)
                if is_vendoragentexists(user) is True:
                    error_message = 'Vendor Agent with same details exists'
                    return response_error_with_message(error_message)
                else:
                    vendor_agent = VendorAgent.objects.create(user=user)
            else:
                user = User.objects.create(username=phone_number, password=password, first_name=name)
                new_vendor_agent = VendorAgent.objects.create(user=user, vendor=vendor)

            # GROUP SETTING
            try:
                group = Group.objects.get(name=constants.VENDOR)
                group.user_set.add(user)
            except Exception as e:
                log_exception(e, 'Group settings failed for vendor agent')

            token = create_token(user, constants.VENDOR)
            return response_with_payload(token.key, None)
        else:
            return response_access_denied()