from gcm import GCM
import constants

def send_push(token, data):
	try:
        gcm = GCM(constants.GCM_PUSH_API_KEY)
        response = gcm.json_request(registration_ids = [token], data = data)
        
    except Exception, e:
        print e
        raise e