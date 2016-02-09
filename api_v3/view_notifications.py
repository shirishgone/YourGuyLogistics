from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, authentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import list_route, detail_route

from yourguy.models import Notification, Employee
from api.views import user_role
from api_v2.views import paginate

import requests
import constants
from api_v3.utils import response_access_denied, response_with_payload, response_error_with_message, response_success_with_message, response_invalid_pagenumber, response_incomplete_parameters

def notification_dict(notification):
    res_order = {
        'notification_id':notification.id,
        'notification_type' : {
        'type_id':notification.notification_type.id,
        'title':notification.notification_type.title
        },
        'delivery_id' : notification.delivery_id,
        'message' : notification.message,
        'time_stamp':notification.time_stamp,
        'read':notification.read
        }
    return res_order

class NotificationViewSet(viewsets.ViewSet):
    """
    Notifications viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()
    
    def destroy(self, request, pk= None):
        return response_access_denied()

    def retrieve(self, request, pk = None):
        role = user_role(request.user)
        if role == constants.OPERATIONS:
            employee = get_object_or_404(Employee, user = request.user)
            notification = get_object_or_404(Notification, pk = pk)
            all_notifications = employee.notifications.all()
            is_permitted = False
            for notif in all_notifications:
                if notification.id == notif.id:
                    is_permitted = True
                    break
            
            if is_permitted == True:
                notif_dict = notification_dict(notification)
                return Response(notif_dict, status = status.HTTP_200_OK)      
            else:
                return response_access_denied()                
        else:
            return response_access_denied()            

    def list(self, request):
        page = self.request.QUERY_PARAMS.get('page', '1')
        page = int(page)
        role = user_role(request.user)
        if role == constants.OPERATIONS:        
            employee = get_object_or_404(Employee, user = request.user)
            notifications = employee.notifications.all().select_related('notification_type').order_by('-time_stamp')
            notifications_count = len(notifications)
            total_pages =  int(notifications_count/constants.PAGINATION_PAGE_SIZE) + 1
            if page > total_pages or page<=0:
                return response_invalid_pagenumber()
            else:
                notifications = paginate(notifications, page)
            # ----------------------------------------------------------------------------        
            result = []
            for notification in notifications:
                notif_dict = notification_dict(notification)
                result.append(notif_dict)

            response_content = {
            "data": result, 
            "total_pages": total_pages, 
            "total_notifications" : notifications_count
            }
            return response_with_payload(response_content, None)
        else:       
            success_message = 'You dont have any notifications for now.'
            return response_success_with_message(success_message)

    @detail_route(methods=['post'])
    def read(self, request, pk):
        role = user_role(request.user)
        if role == constants.OPERATIONS:
            employee = get_object_or_404(Employee, user = request.user)
            notification = get_object_or_404(Notification, pk = pk)
            all_notifications = employee.notifications.all()
            is_permitted = False
            for notif in all_notifications:
                if notification.id == notif.id:
                    is_permitted = True
                    break
            if is_permitted == True:
                notification.read = True
                notification.save()
                return Response(status = status.HTTP_200_OK)      
            else:
                return response_access_denied()
        else:
            return response_access_denied()
    
    @list_route(methods=['GET'])
    def pending(self, request):        
        role = user_role(request.user)
        if role == constants.OPERATIONS:
           employee = get_object_or_404(Employee, user = request.user) 
           notifications_count = employee.notifications.filter(read = False).count()
           response_content = {"count": notifications_count}
           return response_with_payload(response_content, None)
        else:  
            success_message = 'You dont have any pending notifications for now.'
            return response_success_with_message(success_message)