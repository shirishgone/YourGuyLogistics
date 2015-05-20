from yourguy.models import User, Token

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets

from api.serializers import UserSerializer
from rest_framework.decorators import list_route, detail_route
from rest_framework.decorators import api_view

class UserViewSet(viewsets.ModelViewSet):
    """
    User viewset that provides the standard actions 
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

# CUSTOM METHODS FOR REGISTRATION AND SIGN-IN ------

## CONSUMER DIRECT REGISTRATION

@api_view(['POST'])
def register_consumer(request):
    try:
        phone_number = request.data['phone_number']
        password = request.data['password']
        name = request.data.get('name')
        email = request.data.get('email')
        
    except Exception, e:
        content = {
                    'error':'Incomplete params',
                    'description':'phone_number, password, email'
                    }   
        return Response(content, status = status.HTTP_400_BAD_REQUEST)

    if is_userexists(phone_number) is True:
        user = User.objects.get(username = phone_number)
        if is_consumerexists(user) is True:
            token = Token.objects.get(user = user)
        else:
            consumer = Consumer.objects.create(user = user)
            token = create_token(user, constants.CONSUMER)    
            user.password = password
            user.save()
    else:
        user = User.objects.create(username=phone_number, password=password)
        token = create_token(user, constants.CONSUMER)
        consumer = Consumer.objects.create(user = user)

    content = {'auth_token': token.key}
    return Response(content, status = status.HTTP_201_CREATED)              

@api_view(['POST'])
def forgot_password(request):
    # TODO: Send an email
    return Response(status=status.HTTP_201_CREATED)      

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

