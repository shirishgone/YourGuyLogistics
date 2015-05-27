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

## CUSTOM METHODS ------
## CONSUMER DIRECT REGISTRATION

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
        
    user = User.objects.create(username=phone_number, password=password)

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
    
    if role == constants.VENDOR:
        vendor = Vendor.objects.get(id =vendor_id)
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
            
    content = {'auth_token': token.key}
    return Response(content, status = status.HTTP_201_CREATED)              

# @api_view(['POST'])
# def forgot_password(request):
#     # TODO: Send an email
#     return Response(status=status.HTTP_201_CREATED)      

# @api_view(['POST'])
# def request_vendor_account(request):
#     """
#     Registration for Vendor
#     """
#     try:
#         store = request.data['store_name']
#         phone_number = request.data['phone_number']
#         email = request.data['email']

#         flat_number = request.data['flat_number']
#         building = request.data['building']
#         street = request.data['street']
#         area_code = request.data['area_code']
#     except:
#         content = {'error':'Incomplete params', 'description':'phone_number, store_name, email, flat_number, building, street, area_code'}
#         return Response(content, status = status.HTTP_400_BAD_REQUEST)

#     new_address = Address.objects.create(flat_number=flat_number, building=building, street=street, area_code= area_code)
#     new_requested_vendor = RequestedVendor.objects.create(store_name = store, address = new_address, email = email, phone_number = phone_number)

#     content = {'description':'Request submitted successfully'}
#     return Response(content, status = status.HTTP_201_CREATED)
#
# @api_view(['POST'])
# def sign_in(request):
#     username = request.POST['username']
#     password = request.POST['password']
#     user = authenticate(username = username, password = password)
#     if user is not None:
#         if user.is_active:
#             login(request,user)
#             token = Token.objects.get(user = user)
#             content = {'user_id':user.id, 'token':token.key}
#             return Response(content, status = status.HTTP_201_CREATED)
#         else:
#           content = {'description':'disabled account'}  
#           return Response(content, status = status.HTTP_400_BAD_REQUEST)
#     else:
#        content = {'description': 'Invalid Login'}
#        return Response(content, status = status.HTTP_400_BAD_REQUEST)


# @api_view(['POST'])
# def dg_signin(request):
#     phone_number = request.data['phone_number']
#     password = request.data['password']
#     if is_dgexists(phone_number) is True:
#         user = User.objects.get(username = phone_number)
#         dg = DeliveryGuy.objects.get(user = user)
        
#         if verify_password(user, password):
#             token = Token.objects.get(user=dg.user)
#             content = {'auth_token': token.key}
#             return Response(content, status = status.HTTP_201_CREATED)   
#         else:
#             content = {'error': 'Invalid Credentials'}
#             return Response(content, status = status.HTTP_201_CREATED)   
#     else:
#         content = {'error':'user with phone number doesnt exists'}  
#         return Response(content, status = status.HTTP_404_NOT_FOUND)

