from datetime import datetime

from django.db.models import Q
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from rest_framework import status, authentication
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api_v3 import constants
from api_v3.utils import paginate, user_role
from yourguy.models import DeliveryGuy, DGAttendance


def dg_list_dict(delivery_guy, attendance):
    dg_list_dict = {
        'id': delivery_guy.id,
        'name': delivery_guy.user.first_name,
        'phone_number': delivery_guy.user.username,
        'app_version': delivery_guy.app_version,
        'status': delivery_guy.status,
        'employee_code': delivery_guy.employee_code
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
        'name': delivery_guy.user.first_name,
        'phone_number': delivery_guy.user.username,
        'app_version': delivery_guy.app_version,
        'status': delivery_guy.status,
        'shift_start_datetime': delivery_guy.shift_start_datetime,
        'shift_end_datetime': delivery_guy.shift_end_datetime,
        'current_load': delivery_guy.current_load,
        'capacity': delivery_guy.capacity,
        'area': delivery_guy.area,
        'battery_percentage': delivery_guy.battery_percentage,
        'last_connected_time': delivery_guy.last_connected_time,
        'assignment_type': delivery_guy.assignment_type,
        'transportation_mode': delivery_guy.assignment_type
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
        if role == constants.OPERATIONS:
            delivery_guy = get_object_or_404(DeliveryGuy, pk=pk)
            delivery_guy.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, pk=None):
        role = user_role(request.user)
        if role == constants.VENDOR:
            content = {
                'error': 'You don\'t have permissions to view delivery guy info'
            }
            return Response(content, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            delivery_guy = get_object_or_404(DeliveryGuy, id = pk)
            detail_dict = dg_details_dict(delivery_guy)
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

            # Attendance for the DG of the day -----------------------------------------------------
            result = []
            for delivery_guy in result_dgs:
                try:
                    attendance = DGAttendance.objects.filter(dg=delivery_guy, date__year=date.year,
                                                             date__month=date.month, date__day=date.day).latest('date')
                except Exception as e:
                    attendance = None

                result.append(dg_list_dict(delivery_guy, attendance))

            content = {
                "data": result,
                "total_pages": total_pages,
                "total_dg_count": total_dg_count
            }
            return Response(content, status=status.HTTP_200_OK)

    @detail_route(methods=['put'])
    def check_in(self, request, pk=None):
        app_version = request.data.get('app_version')
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
    
    @detail_route(methods=['get'])
    def profile(self, request, pk = None):
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

@api_view(['GET'])
def dg_app_version(request):
    response_content = { 
        "app_version": constants.LATEST_DG_APP_VERSION
        }
    return Response(response_content, status = status.HTTP_200_OK)            