from yourguy.models import User, Token

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, authentication
from rest_framework import viewsets

from api.serializers import UserSerializer
from rest_framework.decorators import list_route, detail_route

class UserViewSet(viewsets.ModelViewSet):
    """
    User viewset that provides the standard actions 
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = User.objects.all()
    serializer_class = UserSerializer

    @detail_route(methods=['post'])
    def sign_in(self, request, pk=None):
    	username = request.POST['username']
    	password = request.POST['password']
    	user = authenticate(username = username, password = password)
    	if user is not None:
    		if user.is_active:
    			login(request,user)
    			token = Token.objects.get(user = user)
    			content = {'user_id':user.id, 'token':token.key}
    			return Response(content, status = status.HTTP_201_CREATED)
    		else:
    			content = {'description':'disabled account'}	
    			return Response(content, status = status.HTTP_400_BAD_REQUEST)
    	else:
    		content = {'description': 'Invalid Login'}
    		return Response(content, status = status.HTTP_400_BAD_REQUEST)

    @list_route()
    def forgot_password():
    	# TODO: Send an email
        return Response(status=status.HTTP_201_CREATED)      
