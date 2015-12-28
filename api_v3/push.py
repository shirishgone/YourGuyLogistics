from api_v3 import constants
from gcm import GCM
from api_v3.utils import log_exception

def send_push(token, data):
    try:
        gcm = GCM(constants.GCM_PUSH_API_KEY)
        response = gcm.json_request(registration_ids=[token], data=data)
    except Exception as e:
        log_exception(e, 'Push notification not sent')
