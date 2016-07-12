import time
from apns import APNs, Frame, Payload
import requests
#use this to generate key without password
#openssl pkcs12 -nocerts -out key.pem -in aps_dev_key.p12 -nodes

def error_handler(error_response):
	print error_response

cert = 'pemfiles/cert.pem'
key = 'pemfiles/key.pem'
apns_obj = APNs(use_sandbox=True, cert_file=cert, key_file=key, enhanced=True)

# for (x,y) in apns_obj.feedback_server.items():
# 	print x, y

r = requests.post('http://planckapi-dev.elasticbeanstalk.com/server/get_push_token',data={'email_id':'rajesh.x.kumar@gmail.com'}, headers = {})
x = r.json()
y = x['push_dict']['ios_id']

payload = Payload(alert="Hello, this is Sachin. I am testing push notifications. Please let me know if you have received this", sound='default', badge=1)
import random

apns_obj.gateway_server.register_response_listener(error_handler)

for device_id in y:
	identifier = random.getrandbits(32)
	apns_obj.gateway_server.send_notification(device_id, payload, identifier=identifier)

