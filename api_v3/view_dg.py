from datetime import datetime

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
    Area, Picture


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
        'name': "%s %s" %(delivery_guy.user.first_name, delivery_guy.user.last_name),
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
        'profile_picture':'',
        'area': [],
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

class DGViewSet(viewsets.ModelViewSet):
    """
    DeliveryGuy viewset that provides the standard actions
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = DeliveryGuy.objects.all()

    def destroy(self, request, pk=None):
        role = user_role(request.user)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)            

    def retrieve(self, request, pk=None):
        role = user_role(request.user)
        if role == constants.VENDOR:
            content = {
                'error': 'You don\'t have permissions to view delivery guy info'
            }
            return Response(content, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            delivery_guy = get_object_or_404(DeliveryGuy, id=pk)
            detail_dict = dg_details_dict(delivery_guy)

            if delivery_guy.area is not None:
                associated_areas = Area.objects.filter(pin_code=delivery_guy.area.pin_code)
                for single_area in associated_areas:
                    detail_dict['area'].append(single_area.pin_code)

            if delivery_guy.profile_picture is not None:
                detail_dict['profile_picture'] = delivery_guy.profile_picture.name

            associated_tl = DeliveryTeamLead.objects.filter(
                associate_delivery_guys__user__username=delivery_guy.user.username)
            if associated_tl is not None:
                for single_tl in associated_tl:
                    detail_dict['team_leads'].append('%s %s' %(single_tl.delivery_guy.user.first_name,
                                                               single_tl.delivery_guy.user.last_name))

            associated_ops_mngr = Employee.objects.filter(
                associate_delivery_guys__user__username=delivery_guy.user.username)
            if associated_ops_mngr is not None:
                for single_ops_mngr in associated_ops_mngr:
                    detail_dict['ops_managers'].append('%s %s' %(single_ops_mngr.user.first_name,
                                                                 single_ops_mngr.user.last_name))

            content = {
                "data": detail_dict
            }
            return Response(content, status=status.HTTP_200_OK)

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
                content = {
                    'error': "Wrong attendance_status. Options: ALL or ONLY_CHECKEDIN or NOT_CHECKEDIN"
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        # ---------------------------------------------------------------------------

        if role == 'vendor':
            content = {
                'error': "You don\'t have permissions to view delivery guy info"
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
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
                response_content = {
                    "error": "Invalid page number"
                }
                return Response(response_content, status=status.HTTP_400_BAD_REQUEST)
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
            executed_orders_today= delivery_statuses_today.filter(order_status=constants.ORDER_STATUS_DELIVERED)
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

                if attendance is not None:
                    if attendance.login_time is not None:
                        worked_hours = (now - attendance.login_time)
                        total_seconds_worked = int(worked_hours.total_seconds())
                        hours, remainder = divmod(total_seconds_worked,60*60)
                        minutes, seconds = divmod(remainder,60)

                        worked_hours = "%d:%d:%d" %(hours, minutes, seconds)
                else:
                    worked_hours = 0

                result.append(dg_list_dict(delivery_guy, attendance, no_of_assigned_orders, no_of_executed_orders, worked_hours))

            content = {
                "data": result,
                "total_pages": total_pages,
                "total_dg_count": total_dg_count
            }
            return Response(content, status=status.HTTP_200_OK)

    def create(self, request):
        role = user_role(request.user)
        if role == constants.OPERATIONS:

            try:
                role = request.data['role']
                phone_number = request.data['phone_number']
                password = request.data['password']
                name = request.data['name']
                area_ids = request.data.get('area_ids')
                shift_start_datetime = request.data.get('shift_start_datetime')
                shift_end_datetime = request.data.get('shift_end_datetime')
                transportation_mode = request.data.get('transportation_mode')
                ops_manager_ids = request.data.get('ops_manager_ids')
                team_lead_ids = request.data.get('team_lead_ids')
                profile_picture = request.data.get('profile_pic_name')

            except Exception as e:
                content = {
                    'error': 'Incomplete params',
                    'description': 'MANDATORY: role, phone_number, password, name. '
                                   'OPTIONAL: area_ids, shift_start_datetime, shift_end_datetime, '
                                   'transportation_mode, ops_manager_ids, team_lead_ids, profile_picture'
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            content = {
                'error': 'API Access limited.',
                'description': 'You cant access this API'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # CHECK IF USER EXISTS  -----------------------------------
        if is_userexists(phone_number):
            content = {
                'error': 'User already exists',
                'description': 'User with same phone number already exists'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        # ---------------------------------------------------------------
        user = User.objects.create_user(username=phone_number, password=password, first_name=name)
        user.save()

        if role == constants.DELIVERY_GUY:
            token = create_token(user, constants.DELIVERY_GUY)
            delivery_guy = DeliveryGuy.objects.create(user=user)
            assign_usergroup(user)

            delivery_guy.is_active = True
            delivery_guy.save()

            if len(area_ids) != 0:
                for single_area_id in area_ids:
                    area_id = single_area_id
                    area = get_object_or_404(Area, id=area_id)
                    delivery_guy.area = area

            if shift_start_datetime is not None:
                delivery_guy.shift_start_datetime = shift_start_datetime

            if shift_end_datetime is not None:
                delivery_guy.shift_end_datetime = shift_end_datetime

            if transportation_mode is not None:
                delivery_guy.transportation_mode = transportation_mode

            if len(ops_manager_ids) != 0:
                for single_ops_manager_id in ops_manager_ids:
                    ops_manager_id = single_ops_manager_id
                    ops_manager = get_object_or_404(Employee, id=ops_manager_id)
                    ops_manager.associate_delivery_guys.add(delivery_guy)

            if len(team_lead_ids) != 0 and delivery_guy.is_teamlead is False:
                for single_team_lead_id in team_lead_ids:
                    team_lead_id = single_team_lead_id
                    team_lead = get_object_or_404(DeliveryTeamLead, id=team_lead_id)
                    team_lead.associate_delivery_guys.add(delivery_guy)

            if profile_picture is not None:
                profile_pic = Picture.objects.create(name=profile_picture)
                delivery_guy.profile_picture = profile_pic

            delivery_guy.save()
        else:
            token = None

        if token is not None:
            content = {'auth_token': token.key}
        else:
            content = {'auth_token': None,
                       'user created for group: ': role}

        return Response(content, status=status.HTTP_201_CREATED)

    @detail_route(methods=['put'])
    def edit_dg_details(self, request, pk=None):
        try:
            role = user_role(request.user)
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            area_ids = request.data.get('area_ids')
            shift_start_datetime = request.data.get('shift_start_datetime')
            shift_end_datetime = request.data.get('shift_end_datetime')
            transportation_mode = request.data.get('transportation_mode')
            ops_manager_ids = request.data.get('ops_manager_ids')
            team_lead_ids = request.data.get('team_lead_ids')
            profile_picture = request.data.get('profile_pic_name')
        except Exception as e:
                content = {
                    'error': 'Only following params can be edited',
                    'description': 'OPTIONAL: first_name, last_name, area_ids, shift_start_datetime, '
                                   'shift_end_datetime, transportation_mode, ops_manager_ids, team_lead_ids, '
                                   'profile_picture'
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if role == constants.VENDOR:
            content = {
                'error': 'You don\'t have permissions to view delivery guy info'
            }
            return Response(content, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            delivery_guy = get_object_or_404(DeliveryGuy, id=pk)

            if delivery_guy.is_active:
                if first_name is not None:
                    delivery_guy.user.first_name = first_name
                    delivery_guy.user.save()

                if last_name is not None:
                    delivery_guy.user.last_name = last_name
                    delivery_guy.user.save()

                if area_ids is not None:
                    for single_area_id in area_ids:
                        area_id = single_area_id
                        area = get_object_or_404(Area, id=area_id)
                        delivery_guy.area = area
                        delivery_guy.area.save()

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

                content = {
                    "description": 'Delivery guy updated'
                }
                return Response(content, status=status.HTTP_200_OK)

            else:
                content = {
                    'error': "You can only edit active dg"
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['put'])
    def deactivate(self, request, pk=None):
        role = user_role(request.user)
        try:
            deactivate_reason = request.data['deactivate_reason']
        except Exception as e:
                content = {
                    'error': 'Incomplete params',
                    'description': 'MANDATORY: deactivate_reason'
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if role == constants.OPERATIONS:
            delivery_guy = get_object_or_404(DeliveryGuy, id=pk)
            if delivery_guy.is_active is True:
                delivery_guy.is_active = False
                delivery_guy.save()
                content = {
                    'delivery_guy': '%s %s is deactivated' %(delivery_guy.user.first_name, delivery_guy.user.last_name),
                    'deactivate_reason': deactivate_reason
                }
                return Response(content, status=status.HTTP_200_OK)
            else:
                content = {
                    'error': 'DG already deactivated',
                    'description': 'This dg had already been deactivated'
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            content = {
                'error': 'API Access limited.',
                'description': 'You cant access this API'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

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
            content = {
                'description': 'Thanks for checking in.'
            }
            return Response(content, status=status.HTTP_200_OK)
        else:
            content = {
                'error': 'Something went wrong'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

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
                content = {
                    'error': 'You havent checked-in properly or forgot to checkout the day before.'
                }
                return Response(content, status=status.HTTP_200_OK)

            attendance.logout_time = today_now
            attendance.save()

            # UPDATE DG AS UNAVAILABLE
            dg.status = constants.DG_STATUS_UN_AVAILABLE
            dg.save()

            if latitude is not None and longitude is not None:
                checkout_location = Location.objects.create(latitude=latitude, longitude=longitude)
                attendance.checkout_location = checkout_location
                attendance.save()

            content = {
                'description': 'Thanks for checking out.'
            }
            return Response(content, status=status.HTTP_200_OK)
        except Exception as e:
            content = {
                'error': 'Something went wrong'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

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

        content = {
            'attendance': all_dgs_array
        }
        return Response(content, status=status.HTTP_200_OK)

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

        content = {
            'all_dg_attendance': all_dg_attendance
        }
        return Response(content, status=status.HTTP_200_OK)

    @detail_route(methods=['put'])
    def update_pushtoken(self, request, pk=None):
        push_token = request.data['push_token']

        dg = get_object_or_404(DeliveryGuy, user=request.user)
        dg.device_token = push_token
        dg.save()

        content = {
            'description': 'Push Token updated'
        }
        return Response(content, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def dg_app_version(request):
    response_content = { 
        "app_version": constants.LATEST_DG_APP_VERSION
        }
    return Response(response_content, status = status.HTTP_200_OK)            

@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def profile(request):
    role = user_role(request.user)
    if role == constants.DELIVERY_GUY:
        delivery_guy = get_object_or_404(DeliveryGuy, user = request.user)
        detail_dict = dg_details_dict(delivery_guy)
        response_content = { "data": detail_dict}
        return Response(response_content, status = status.HTTP_200_OK)
    else:
        content = {
        'error':'You dont have permissions to view delivery guy info'
        }
        return Response(content, status = status.HTTP_405_METHOD_NOT_ALLOWED)