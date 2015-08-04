from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.decorators import api_view
from rest_framework.response import Response

from yourguy.models import User, Token, Vendor, VendorAgent, Consumer, DeliveryGuy, Employee
from api.views import is_userexists, create_token 
import constants


# from django.contrib.auth.models import User
# from rest_framework viewsets
# from rest_framework.permissions import AllowAny 
# from .permissions import IsStaffOrTargetUser
# class UserView(viewsets.ModelViewSet):
#     serializer_class = UserSerializer
#     model = User
 
#     def get_permissions(self):
#         # allow non-authenticated user to create via POST
#         return (AllowAny() if self.request.method == 'POST'
#                 else IsStaffOrTargetUser()),


## CUSTOM METHODS ------
## CONSUMER DIRECT REGISTRATION

@api_view(['GET'])
def all_vendor_emails(request):
    all_vendors = Vendor.objects.all()
    all_vendors_emails = []
    for vendor in all_vendors:
        all_vendors_emails.append(vendor.email)
    
    content = {'all_vendor_emails':all_vendors_emails}
    return Response(content, status = status.HTTP_200_OK)
        

@api_view(['POST'])
def register(request):

    try:
        role = request.data['role']
        phone_number = request.data['phone_number']
        password = request.data['password']
        
        name = request.data.get('name')
        email = request.data.get('email')
        vendor_id = request.data.get('vendor_id')
        
    except Exception, e:
        content = {
                    'error':'Incomplete params',
                    'description':'MANDATORY: role, phone_number, password. OPTIONAL: name, email, vendor_id'
                    }   
        return Response(content, status = status.HTTP_400_BAD_REQUEST)

    if is_userexists(phone_number):         
        content = {
                    'error':'User already exists',
                    'description':'User with same phone number already exists'
                    }   
        return Response(content, status = status.HTTP_400_BAD_REQUEST)
    else:
        pass    
       
    
    # VENDOR EXISTENCE CHECK ----   
    if role == constants.VENDOR:
        try:
            vendor = Vendor.objects.get(id = vendor_id)       
        except:
            content = {'error':'Vendor with given id doesnt exists'}   
            return Response(content, status = status.HTTP_400_BAD_REQUEST)
    else:
        pass    
    
    user = User.objects.create_user(username=phone_number, password=password)

    if name is not None:
        user.first_name = name

    if email is not None:
        user.email = email
    
    user.save()    

    if role == constants.VENDOR:
        token = create_token(user, constants.VENDOR)
    elif role == constants.DELIVERY_GUY:
        token = create_token(user, constants.DELIVERY_GUY)
    elif role == constants.CONSUMER:
        token = create_token(user, constants.CONSUMER)
    elif role == constants.OPERATIONS:
        token = create_token(user, constants.OPERATIONS)
    elif role == constants.SALES:
        token = create_token(user, constants.SALES)
    else:
        token = None

    if name is not None:
        user.first_name = name

    if email is not None:
        user.email = email
    
    content = {'auth_token': token.key}

    if role == constants.VENDOR:
        vendor = get_object_or_404(Vendor, id = vendor_id)
        vendor_agent = VendorAgent.objects.create(user = user, vendor = vendor)
    elif role == constants.CONSUMER:
        consumer = Consumer.objects.create(user = user)    
    elif role == constants.DELIVERY_GUY:
        delivery_guy = DeliveryGuy.objects.create(user = user)    
    elif role == constants.OPERATIONS:
        employee = Employee.objects.create(user = user)
        employee.department = constants.OPERATIONS
    elif role == constants.SALES:
        employee = Employee.objects.create(user = user)
        employee.department = constants.SALES
    else:
        pass
            
    return Response(content, status = status.HTTP_201_CREATED)              