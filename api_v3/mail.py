from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.views import send_email
from api_v3 import constants


@api_view(['POST'])
def website_email(request):
    try:
        name = request.data['name']
        phone_number = request.data['phone_number']
        message = request.data['message']
    except Exception as e:
        content = {
            'error': 'Imcomplete parameters',
            'description': 'name, phone_number, message are mandatory parameters'
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    body = 'Hi,'
    body = body + '\n\nMr.%s has sent a message from website.' % (name)
    body = body + '\nPhone number: %s' % (phone_number)
    body = body + '\nMessage: %s' % (message)
    body = body + '\n\n-YourGuy Bot'
    send_email(constants.EMAIL_WEBSITE, 'Message from website', body)
    return Response(status=status.HTTP_200_OK)
