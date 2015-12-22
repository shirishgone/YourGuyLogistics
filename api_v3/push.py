from api_v3 import constants
from gcm import GCM


def send_push(token, data):
    try:
        gcm = GCM(constants.GCM_PUSH_API_KEY)
        response = gcm.json_request(registration_ids=[token], data=data)
    except Exception as e:
        print(e)
        pass
