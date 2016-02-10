from datetime import datetime
from dateutil.rrule import rrule, DAILY
import pytz
from django.db.models import Q
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from rest_framework import status, authentication, viewsets
from rest_framework.decorators import api_view
from rest_framework.decorators import detail_route, list_route
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api_v3 import constants
from api_v3.utils import paginate, user_role, ist_day_start, ist_day_end, is_userexists, create_token, assign_usergroup
from yourguy.models import DeliveryGuy, DGAttendance, Location, OrderDeliveryStatus, User, Employee, DeliveryTeamLead, \
    ServiceablePincode, Picture

from api_v3.utils import response_access_denied, response_with_payload, response_error_with_message, response_success_with_message, response_invalid_pagenumber, response_incomplete_parameters

def dg_list_dict(delivery_guy, attendance, no_of_assigned_orders, no_of_executed_orders, worked_hours):
    dg_list_dict = {
        'id': delivery_guy.id,
        'name': delivery_guy.user.first_name + delivery_guy.user.last_name,
        'phone_number': delivery_guy.user.username,
        'app_version': delivery_guy.app_version,
        'status': delivery_guy.status,
        'employee_code': delivery_guy.employee_code,
        'no_of_assigned_orders': no_of_assigned_orders,
        'no_of_executed_orders': no_of_executed_orders,
        'worked_hours': worked_hours
    }
    if attendance is not None:
        dg_list_dict['check_in'] = attendance.login_time
        dg_list_dict['check_out'] = attendance.logout_time
    else:
        dg_list_dict['check_in'] = None
        dg_list_dict['check_out'] = None

    return dg_list_dict


def dg_details_dict(delivery_guy):
    dg_detail_dict = {
        'id': delivery_guy.id,
        'employee_code': delivery_guy.employee_code,
        'name': "%s %s" % (delivery_guy.user.first_name, delivery_guy.user.last_name),
        'phone_number': delivery_guy.user.username,
        'app_version': delivery_guy.app_version,
        'status': delivery_guy.status,
        'shift_start_datetime': delivery_guy.shift_start_datetime,
        'shift_end_datetime': delivery_guy.shift_end_datetime,
        'current_load': delivery_guy.current_load,
        'capacity': delivery_guy.capacity,
        'battery_percentage': delivery_guy.battery_percentage,
        'last_connected_time': delivery_guy.last_connected_time,
        'assignment_type': delivery_guy.assignment_type,
        'transportation_mode': delivery_guy.transportation_mode,
        'profile_picture': '',
        'pincode': [],
        'ops_managers': [],
        'team_leads': []
    }
    return dg_detail_dict


def dg_attendance_list_dict(dg_attendance):
    dg_attendance_dict = {
        'id': dg_attendance.dg.user.id,
        'employee_code': dg_attendance.dg.employee_code,
        'name': dg_attendance.dg.user.first_name,
        'date': dg_attendance.date,
        'status': dg_attendance.status,
        'login_time': dg_attendance.login_time,
        'logout_time': dg_attendance.logout_time,
        'shift_start_datetime': dg_attendance.dg.shift_start_datetime,
        'shift_end_datetime': dg_attendance.dg.shift_end_datetime
    }

    return dg_attendance_dict


def download_attendance_excel_dict(dg):
    download_attendance_dict = {
        'name': dg.user.first_name,
        'attendance': []
    }
    return download_attendance_dict


def attendance_datewise_dict():
    datewise_dict = {
            'date': '',
            'worked_hrs': ''
        }
    return datewise_dict

class DGViewSet(viewsets.ModelViewSet):
    """
    DeliveryGuy viewset that provides the standard actions
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = DeliveryGuy.objects.all()

    def destroy(self, request, pk=None):
        return response_access_denied()

    def retrieve(self, request, pk=None):
        role = user_role(request.user)
        if role == constants.VENDOR:
            return response_access_denied()
        else:
            delivery_guy = get_object_or_404(DeliveryGuy, id=pk)
            detail_dict = dg_details_dict(delivery_guy)

            # only return pincodes for dg team lead
            if delivery_guy.is_teamlead is True:
                try:
                    delivery_guy_tl = DeliveryTeamLead.objects.get(delivery_guy=delivery_guy)
                except Exception as e:
                    error_message = 'No such Delivery Team Lead exists'
                    return response_error_with_message(error_message)

                if delivery_guy_tl.serving_pincodes is not None:
                    pincodes = delivery_guy_tl.serving_pincodes.all()
                    for single_pincode in pincodes:
                        detail_dict['pincode'].append(single_pincode.pincode)

            if delivery_guy.profile_picture is not None:
                detail_dict['profile_picture'] = delivery_guy.profile_picture.name

            if delivery_guy.is_teamlead is False:
                associated_tl = DeliveryTeamLead.objects.filter(
                    associate_delivery_guys__user__username=delivery_guy.user.username)
                if not associated_tl:
                    for single_tl in associated_tl:
                        detail_dict['team_leads'].append('%s' % (single_tl.delivery_guy.user.first_name))

            associated_ops_mngr = Employee.objects.filter(
                associate_delivery_guys__user__username=delivery_guy.user.username)
            if not associated_ops_mngr:
                for single_ops_mngr in associated_ops_mngr:
                    detail_dict['ops_managers'].append('%s' % (single_ops_mngr.user.first_name))

            content = {'data': detail_dict}
            return response_with_payload(content, None)

    def list(self, request):
        page = self.request.QUERY_PARAMS.get('page', None)
        role = user_role(request.user)
        search_query = request.QUERY_PARAMS.get('search', None)
        date_string = self.request.QUERY_PARAMS.get('date', None)
        attendance_status = self.request.QUERY_PARAMS.get('attendance_status', None)

        # SEARCH KEYWORD FILTERING ---------------------------------------------------
        if date_string is not None:
            date = parse_datetime(date_string)
        else:
            date = datetime.today()

        day_start = ist_day_start(date)
        day_end = ist_day_end(date)
        now = datetime.now(pytz.utc)
        # ---------------------------------------------------------------------------

        if page is not None:
            page = int(page)
        else:
            page = 1

        # ATTENDANCE FILTERING ------------------------------------------------------
        if attendance_status is not None:
            if attendance_status == 'ALL' or attendance_status == 'ONLY_CHECKEDIN' or attendance_status == 'NOT_CHECKEDIN' \
                    or attendance_status == 'CHECKEDIN_AND_CHECKEDOUT':
                pass
            else:
                error_message = 'Wrong attendance_status. Options: ALL or ONLY_CHECKEDIN or NOT_CHECKEDIN'
                return response_error_with_message(error_message)
        # ---------------------------------------------------------------------------

        if role == constants.VENDOR:
            return response_access_denied()
        else:
            all_dgs = DeliveryGuy.objects.order_by('user__first_name')

            # SEARCH KEYWORD FILTERING ---------------------------------------------------
            if search_query is not None:
                if search_query.isdigit():
                    all_dgs = all_dgs.filter(Q(user__username__icontains=search_query))
                else:
                    all_dgs = all_dgs.filter(Q(user__first_name__icontains=search_query) |
                                             Q(employee_code=search_query) |
                                             Q(app_version=search_query))
            # ---------------------------------------------------------------------------
            # FILTERING BY ATTENDANCE STATUS ---------------------------------------------------
            final_dgs = []
            if attendance_status is not None:
                if attendance_status == 'ONLY_CHECKEDIN' or attendance_status == 'NOT_CHECKEDIN' \
                        or attendance_status == 'CHECKEDIN_AND_CHECKEDOUT':
                    for delivery_guy in all_dgs:
                        try:
                            attendance = DGAttendance.objects.filter(dg=delivery_guy, date__year=date.year,
                                                                     date__month=date.month, date__day=date.day).latest(
                                'date')
                        except Exception as e:
                            attendance = None

                        if attendance_status == 'NOT_CHECKEDIN' and attendance == None:
                            final_dgs.append(delivery_guy)
                        elif attendance_status == 'ONLY_CHECKEDIN' and attendance is not None and attendance.logout_time == None:
                            final_dgs.append(delivery_guy)
                        else:
                            final_dgs.append(delivery_guy)
                else:
                    final_dgs = all_dgs
            else:
                final_dgs = all_dgs
            # ---------------------------------------------------------------------------

            # PAGINATE ---------------------------------------------------------------------------
            total_dg_count = len(final_dgs)
            total_pages = int(total_dg_count / constants.PAGINATION_PAGE_SIZE) + 1

            if page > total_pages or page <= 0:
                return response_invalid_pagenumber()
            else:
                result_dgs = paginate(final_dgs, page)

            # -------------------------------------------------------------------------------------
            delivery_statuses_today = OrderDeliveryStatus.objects.filter(date__gte=day_start, date__lte=day_end)
            assigned_orders_today = delivery_statuses_today.filter(
                Q(order_status=constants.ORDER_STATUS_QUEUED) |
                Q(order_status=constants.ORDER_STATUS_INTRANSIT) |
                Q(order_status=constants.ORDER_STATUS_PICKUP_ATTEMPTED) |
                Q(order_status=constants.ORDER_STATUS_DELIVERY_ATTEMPTED) |
                Q(order_status=constants.ORDER_STATUS_DELIVERED)
            )
            assigned_orders_today = assigned_orders_today.exclude(delivery_guy=None)
            executed_orders_today = delivery_statuses_today.filter(order_status=constants.ORDER_STATUS_DELIVERED)
            executed_orders_today = executed_orders_today.exclude(delivery_guy=None)

            # Attendance for the DG of the day -----------------------------------------------------
            result = []
            for delivery_guy in result_dgs:
                try:
                    attendance = DGAttendance.objects.filter(dg=delivery_guy, date__year=date.year,
                                                             date__month=date.month, date__day=date.day).latest('date')
                except Exception as e:
                    attendance = None

                # append cod, executed, assigned for that dg
                no_of_assigned_orders = assigned_orders_today.filter(delivery_guy=delivery_guy).count()
                no_of_executed_orders = executed_orders_today.filter(delivery_guy=delivery_guy).count()
                worked_hours = 0

                if attendance is not None:
                    if attendance.login_time is not None:
                        worked_hours = (now - attendance.login_time)
                        total_seconds_worked = int(worked_hours.total_seconds())
                        hours, remainder = divmod(total_seconds_worked, 60 * 60)
                        minutes, seconds = divmod(remainder, 60)

                        worked_hours = "%d:%d:%d" % (hours, minutes, seconds)

                result.append(
                    dg_list_dict(delivery_guy, attendance, no_of_assigned_orders, no_of_executed_orders, worked_hours))

            content = {
                "data": result,
                "total_pages": total_pages,
                "total_dg_count": total_dg_count
            }
            return response_with_payload(content, None)

    # boolean is_teamlead will be sent if the create dg api is used to create a team lead
    # also only servicable pincodes will be considered for team lead creation
    def create(self, request):
        role = user_role(request.user)
        if role == constants.OPERATIONS_MANAGER:

            try:
                phone_number = request.data['phone_number']
                password = request.data['password']
                name = request.data['name']
                serviceable_pincodes = request.data.get('serviceable_pincodes')
                shift_start_datetime = request.data.get('shift_start_datetime')
                shift_end_datetime = request.data.get('shift_end_datetime')
                transportation_mode = request.data.get('transportation_mode')
                ops_manager_ids = request.data.get('ops_manager_ids')
                team_lead_ids = request.data.get('team_lead_ids')
                profile_picture = request.data.get('profile_pic_name')
                is_teamlead = request.data.get('is_teamlead')

            except Exception as e:
                params = ['phone_number', 'password', 'name', 'serviceable_pincodes(optional)', 'shift_start_datetime(optional)', 'shift_end_datetime(optional)', 'transportation_mode(optional)', 'ops_manager_ids(optional)', 'team_lead_ids(optional)', 'profile_picture(optional)', 'is_teamlead(optional)']
                return response_incomplete_parameters(params)
        else:
            return response_access_denied()
        
        # CHECK IF USER EXISTS  -----------------------------------
        if is_userexists(phone_number):
            error_message = 'User with same phone number already exists'
            return response_error_with_message(error_message)
        # ---------------------------------------------------------------
        user = User.objects.create_user(username=phone_number, password=password, first_name=name)
        user.save()

        token = create_token(user, constants.DELIVERY_GUY)
        delivery_guy = DeliveryGuy.objects.create(user=user)
        assign_usergroup(user)

        delivery_guy.is_active = True
        delivery_guy.save()

        # If new dg being created is a tl, then need to create an object of DeliveryTeamLead model for the same dg and set flag to true in dg
        if is_teamlead:
            delivery_guy_tl = DeliveryTeamLead.objects.create(delivery_guy=delivery_guy)
            delivery_guy_tl.save()
            delivery_guy.is_teamlead = True
            if serviceable_pincodes is not None:
                for single_serviceable_pincode in serviceable_pincodes:
                    single_pincode = single_serviceable_pincode
                    pincode = ServiceablePincode.objects.get(pincode=single_pincode)
                    delivery_guy_tl.serving_pincodes.add(pincode)
                    delivery_guy_tl.save()

        if shift_start_datetime is not None:
            delivery_guy.shift_start_datetime = shift_start_datetime

        if shift_end_datetime is not None:
            delivery_guy.shift_end_datetime = shift_end_datetime

        if transportation_mode is not None:
            delivery_guy.transportation_mode = transportation_mode

        if ops_manager_ids is not None:
            for single_ops_manager_id in ops_manager_ids:
                ops_manager_id = single_ops_manager_id
                ops_manager = get_object_or_404(Employee, id=ops_manager_id)
                ops_manager.associate_delivery_guys.add(delivery_guy)
                ops_manager.save()

        if team_lead_ids is not None and delivery_guy.is_teamlead is False:
            for single_team_lead_id in team_lead_ids:
                team_lead_id = single_team_lead_id
                team_lead = get_object_or_404(DeliveryTeamLead, id=team_lead_id)
                team_lead.associate_delivery_guys.add(delivery_guy)
                team_lead.save()

        if profile_picture is not None:
            profile_pic = Picture.objects.create(name=profile_picture)
            delivery_guy.profile_picture = profile_pic

        delivery_guy.save()
        content = {'auth_token': token.key}
        return response_with_payload(content, None)

    # Workflows handled are edit dg, edit dg tl
    # req param being sent is is_teamlead flag, check this flag and do a get object or 404 with this data,
    #   if returned, then modifying existing dg tl cases
    #   else create new dg tl object with this dg and add related data
    @detail_route(methods=['put'])
    def edit_dg_details(self, request, pk=None):
        try:
            role = user_role(request.user)
            name = request.data.get('name')
            serviceable_pincodes = request.data.get('serviceable_pincodes')
            shift_start_datetime = request.data.get('shift_start_datetime')
            shift_end_datetime = request.data.get('shift_end_datetime')
            transportation_mode = request.data.get('transportation_mode')
            ops_manager_ids = request.data.get('ops_manager_ids')
            team_lead_ids = request.data.get('team_lead_ids')
            profile_picture = request.data.get('profile_pic_name')
            is_teamlead = request.data.get('is_teamlead')

        except Exception as e:
            params = ['name(optional)', 'serviceable_pincodes(optional)', 'shift_start_datetime(optional)', 'shift_end_datetime(optional)', 'transportation_mode(optional)', 'ops_manager_ids(optional)', 'team_lead_ids(optional)', 'profile_picture(optional)', 'is_teamlead(optional)']
            return response_incomplete_parameters(params)
        
        if role == constants.OPERATIONS or role == constants.OPERATIONS_MANAGER:
            delivery_guy = get_object_or_404(DeliveryGuy, id=pk)

            if delivery_guy.is_active:
                if name is not None:
                    delivery_guy.user.first_name = name
                    delivery_guy.user.save()
                # Here filter on dg tl instead of using get /get_404 to avoid exception
                if is_teamlead is True:
                    if serviceable_pincodes is not None:
                        for single_serviceable_pincodes in serviceable_pincodes:
                            single_pincode = single_serviceable_pincodes
                            pincode = ServiceablePincode.objects.get(pincode=single_pincode)
                            delivery_guy_tl = DeliveryTeamLead.objects.all().filter(delivery_guy=delivery_guy)
                            if not delivery_guy_tl:
                                delivery_guy_tl = DeliveryTeamLead.objects.create(delivery_guy=delivery_guy)
                                delivery_guy_tl.serving_pincodes.add(pincode)
                                delivery_guy_tl.save()
                            else:
                                for single_tl in delivery_guy_tl:
                                    single_tl.serving_pincodes.add(pincode)
                                    single_tl.save()

                if shift_start_datetime is not None:
                    delivery_guy.shift_start_datetime = shift_start_datetime

                if shift_end_datetime is not None:
                    delivery_guy.shift_end_datetime = shift_end_datetime

                if transportation_mode is not None:
                    delivery_guy.transportation_mode = transportation_mode

                if ops_manager_ids is not None:
                    for single_ops_manager_id in ops_manager_ids:
                        ops_manager_id = single_ops_manager_id
                        ops_manager = get_object_or_404(Employee, id=ops_manager_id)
                        ops_manager.associate_delivery_guys.add(delivery_guy)
                        ops_manager.save()

                if team_lead_ids is not None and delivery_guy.is_teamlead is False:
                    for single_team_lead_id in team_lead_ids:
                        team_lead_id = single_team_lead_id
                        team_lead = get_object_or_404(DeliveryTeamLead, id=team_lead_id)
                        team_lead.associate_delivery_guys.add(delivery_guy)
                        team_lead.save()

                if profile_picture is not None:
                    profile_pic = Picture.objects.create(name=profile_picture)
                    delivery_guy.profile_picture = profile_pic

                delivery_guy.save()
                success_message = 'Delivery guy updated.'
                return response_success_with_message(success_message)
            else:
                error_message = 'You can only edit active delivery guys'
                return response_error_with_message()

    @detail_route(methods=['put'])
    def deactivate(self, request, pk=None):
        role = user_role(request.user)
        try:
            deactivate_reason = request.data['deactivate_reason']
        except Exception as e:
            params = ['deactivate_reason']
            return response_incomplete_parameters(params)
        
        if role == constants.OPERATIONS:
            delivery_guy = get_object_or_404(DeliveryGuy, id=pk)
            if delivery_guy.is_active is True:
                delivery_guy.is_active = False
                deactivated_date = datetime.now()
                delivery_guy.deactivated_date = deactivated_date
                delivery_guy.save()
                content = {
                    'delivery_guy': '%s %s is deactivated' % (delivery_guy.user.first_name,
                                                              delivery_guy.user.last_name),
                    'deactivate_reason': deactivate_reason,
                    'deactivated_date': deactivated_date
                }
                return response_with_payload(content, None)
            else:
                error_message = 'This delivery boy had already been deactivated'
                return response_error_with_message(error_message)
        else:
            return response_access_denied()

    @detail_route(methods=['put'])
    def check_in(self, request, pk=None):
        app_version = request.data.get('app_version')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        dg = get_object_or_404(DeliveryGuy, user=request.user)

        dg.status = constants.DG_STATUS_AVAILABLE
        if app_version is not None:
            dg.app_version = app_version
        dg.save()

        today = datetime.now()
        is_today_checkedIn = False

        attendance_list = DGAttendance.objects.filter(dg=dg, date__year=today.year, date__month=today.month,
                                                      date__day=today.day)

        if len(attendance_list) > 0:
            is_today_checkedIn = True

        if is_today_checkedIn == False:
            attendance = DGAttendance.objects.create(dg=dg, date=today, login_time=today)
            attendance.status = constants.DG_STATUS_WORKING
            attendance.save()
            is_today_checkedIn = True
            if latitude is not None and longitude is not None:
                checkin_location = Location.objects.create(latitude=latitude, longitude=longitude)
                attendance.checkin_location = checkin_location
                attendance.save()

        if is_today_checkedIn is True:
            success_message = 'Thanks for checking in.'
            return response_success_with_message(success_message)
        else:
            error_message = 'something went wrong'
            return response_error_with_message(error_message)

    @detail_route(methods=['put'])
    def check_out(self, request, pk=None):
        dg = get_object_or_404(DeliveryGuy, user=request.user)
        today_now = datetime.now()
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        try:
            try:
                attendance = DGAttendance.objects.filter(dg=dg, date__year=today_now.year, date__month=today_now.month,
                                                         date__day=today_now.day).latest('date')
            except Exception as e:
                error_message = 'You havent checked-in properly or forgot to checkout the day before.'
                return response_error_with_message(error_message)

            attendance.logout_time = today_now
            attendance.save()

            # UPDATE DG AS UNAVAILABLE
            dg.status = constants.DG_STATUS_UN_AVAILABLE
            dg.save()

            if latitude is not None and longitude is not None:
                checkout_location = Location.objects.create(latitude=latitude, longitude=longitude)
                attendance.checkout_location = checkout_location
                attendance.save()

            success_message = 'Thanks for checking out.'
            return response_success_with_message(success_message)
        except Exception as e:
            error_message = 'Something went wrong'
            return response_error_with_message(error_message)

    @detail_route(methods=['put'])
    def attendance(self, request, pk):
        month = request.data.get('month')
        year = request.data.get('year')

        dg = get_object_or_404(DeliveryGuy, pk=pk)
        all_dg_attendance = DGAttendance.objects.filter(dg=dg, date__year=year, date__month=month)

        all_dgs_array = []
        for dg_attendance in all_dg_attendance:
            dg_attendance_dict = dg_attendance_list_dict(dg_attendance)
            all_dgs_array.append(dg_attendance_dict)

        content = {'attendance': all_dgs_array}
        return response_with_payload(content, None)

    @list_route()
    def all_dg_attendance(self, request):
        date_string = self.request.QUERY_PARAMS.get('date', None)
        if date_string is not None:
            date = parse_datetime(date_string)
        else:
            date = datetime.today()

        all_attendance = DGAttendance.objects.filter(date__year=date.year, date__month=date.month,
                                                     date__day=date.day).order_by(Lower('dg__user__first_name'))
        all_dg_attendance = []
        for attendance in all_attendance:
            dg_attendance_dict = dg_attendance_list_dict(attendance)
            all_dg_attendance.append(dg_attendance_dict)

        content = {'all_dg_attendance': all_dg_attendance}
        return response_with_payload(content, None)

    @detail_route(methods=['put'])
    def update_pushtoken(self, request, pk=None):
        push_token = request.data['push_token']

        dg = get_object_or_404(DeliveryGuy, user=request.user)
        dg.device_token = push_token
        dg.save()
        success_message = 'Push Token updated.'
        return response_success_with_message(success_message)

    @list_route()
    def download_attendance(self, request):
        try:
            start_date_string = self.request.QUERY_PARAMS.get('start_date')
            end_date_string = self.request.QUERY_PARAMS.get('end_date')

            start_date = parse_datetime(start_date_string)
            start_date = ist_day_start(start_date)
            start_date = start_date.date()

            end_date = parse_datetime(end_date_string)
            end_date = ist_day_end(end_date)
            end_date = end_date.date()
        except Exception as e:
            params = ['start_date', 'end_date']
            return response_incomplete_parameters(params)

        # CREATE DATE RULE -----------------------------------------------------------
        rule_daily = rrule(DAILY, dtstart=start_date, until=end_date)
        alldates = list(rule_daily)

        # ALL DGS
        all_dgs = DeliveryGuy.objects.all()
        all_attendance = DGAttendance.objects.all()

        all_dg_attendance = []
        worked_hours = 0

        for single_dg in all_dgs:
            if single_dg.is_active:
                download_attendance_dict = download_attendance_excel_dict(single_dg)
                for date in alldates:
                    datewise_dict = attendance_datewise_dict()
                    dg_attendance = all_attendance.filter(dg=single_dg, date=date)
                    if dg_attendance:
                        for single in dg_attendance:
                            if single.login_time is not None and single.logout_time is not None:
                                worked_hours = (single.logout_time - single.login_time)
                                total_seconds_worked = int(worked_hours.total_seconds())
                                hours, remainder = divmod(total_seconds_worked, 60 * 60)
                                worked_hours = "%d hrs" % hours
                            elif single.login_time is not None and single.logout_time is None:
                                worked_hours = (datetime.now(pytz.utc) - single.login_time)
                                total_seconds_worked = int(worked_hours.total_seconds())
                                hours, remainder = divmod(total_seconds_worked, 60 * 60)
                                worked_hours = "%d hrs" % hours
                            else:
                                pass
                        datewise_dict['date'] = date
                        datewise_dict['worked_hrs'] = worked_hours
                    else:
                        date = date
                        worked_hours = 0

                        datewise_dict['date'] = date
                        datewise_dict['worked_hrs'] = worked_hours
                    download_attendance_dict['attendance'].append(datewise_dict)
                all_dg_attendance.append(download_attendance_dict)
            else:
                # when dg is deactivated
                # compare deactivated_date and start_date
                # generate rule from start date till the deactivated date only
                # loop from start date till this deactivated date
                start_month = start_date.month
                dg_deactived_date = single_dg.deactivated_date
                deactivated_month = dg_deactived_date.month
                download_attendance_dict = download_attendance_excel_dict(single_dg)
                if start_date < dg_deactived_date and start_month == deactivated_month:
                    rule_daily_deactivated = rrule(DAILY, dtstart=start_date, until=dg_deactived_date)
                    till_deactivated_date = list(rule_daily_deactivated)
                    for date in till_deactivated_date:
                        datewise_dict = attendance_datewise_dict()
                        dg_attendance = all_attendance.filter(dg=single_dg, date=date)
                        if dg_attendance:
                            for single in dg_attendance:
                                if single.login_time is not None and single.logout_time is not None:
                                    worked_hours = (single.logout_time - single.login_time)
                                    total_seconds_worked = int(worked_hours.total_seconds())
                                    hours, remainder = divmod(total_seconds_worked, 60 * 60)
                                    worked_hours = "%d hrs" % hours
                                elif single.login_time is not None and single.logout_time is None:
                                    worked_hours = (datetime.now(pytz.utc) - single.login_time)
                                    total_seconds_worked = int(worked_hours.total_seconds())
                                    hours, remainder = divmod(total_seconds_worked, 60 * 60)
                                    worked_hours = "%d hrs" % hours
                                else:
                                    pass
                            datewise_dict['date'] = date
                            datewise_dict['worked_hrs'] = worked_hours
                        else:
                            date = date
                            worked_hours = 0

                            datewise_dict['date'] = date
                            datewise_dict['worked_hrs'] = worked_hours
                        download_attendance_dict['attendance'].append(datewise_dict)
                    all_dg_attendance.append(download_attendance_dict)
                elif start_date < dg_deactived_date and start_month < deactivated_month:
                    rule_daily_deactivated = rrule(DAILY, dtstart=start_date, until=end_date)
                    till_date = list(rule_daily_deactivated)
                    for date in till_date:
                        datewise_dict = attendance_datewise_dict()
                        dg_attendance = all_attendance.filter(dg=single_dg, date=date)
                        if dg_attendance:
                            for single in dg_attendance:
                                if single.login_time is not None and single.logout_time is not None:
                                    worked_hours = (single.logout_time - single.login_time)
                                    total_seconds_worked = int(worked_hours.total_seconds())
                                    hours, remainder = divmod(total_seconds_worked, 60 * 60)
                                    worked_hours = "%d hrs" % hours
                                elif single.login_time is not None and single.logout_time is None:
                                    worked_hours = (datetime.now(pytz.utc) - single.login_time)
                                    total_seconds_worked = int(worked_hours.total_seconds())
                                    hours, remainder = divmod(total_seconds_worked, 60 * 60)
                                    worked_hours = "%d hrs" % hours
                                else:
                                    pass
                            datewise_dict['date'] = date
                            datewise_dict['worked_hrs'] = worked_hours
                        else:
                            date = date
                            worked_hours = 0

                            datewise_dict['date'] = date
                            datewise_dict['worked_hrs'] = worked_hours
                        download_attendance_dict['attendance'].append(datewise_dict)
                    all_dg_attendance.append(download_attendance_dict)

        content = {'all_dg_attendance': all_dg_attendance}
        return response_with_payload(content, None)

@api_view(['GET'])
def dg_app_version(request):
    content = {'app_version': constants.LATEST_DG_APP_VERSION}
    return response_with_payload(content, None)

@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def profile(request):
    role = user_role(request.user)
    if role == constants.DELIVERY_GUY:
        delivery_guy = get_object_or_404(DeliveryGuy, user=request.user)
        detail_dict = dg_details_dict(delivery_guy)
        response_content = {"data": detail_dict}
        return response_with_payload(response_content, None)
    else:
        return response_access_denied()