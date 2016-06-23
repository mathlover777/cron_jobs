import requests
import json
import helper

planck_hard_pass = 'planck_test'
base_url = 'http://planckapi-dev.elasticbeanstalk.com'
prioritizer_url = 'http://planckapi-prioritizer.us-west-1.elasticbeanstalk.com'
# base_url = 'http://token-store-dev.elasticbeanstalk.com'
# base_url = 'http://127.0.0.1:8000'
epoch = 631152000

def get_token(email_id, source="nylas"):
	payload = {'email_id':email_id,'access_token':'planck_test', 'source': source}
	url = base_url + '/server/get_token'
	r = requests.post(url,data = payload)
	# print r
	response = r.json()
	
	if response['success'] != 'true':
		# print 'error'
		return ''
	return response['token']

def get_email_prio_users():
	r = requests.post(base_url + '/server/get_priority_user_list')
	response = r.json()
	if (response['success'] != 'true'):
		print 'error !!'
		return []
	return response['prio_user_list']

def remove_user_from_prio(email_id):
	payload = {'email_id':email_id}
	url = base_url + '/server/remove_user_to_priotity_list'
	r = requests.post(url,data = payload)

def update_contact_score(email_id,contact_score_json):
	# str_score = {}
	# for email in contact_score_json:
	# 	str_score[email.encode('ascii','ignore')] = contact_score_json[email]
	# print str_score
	payload = {'email_id':email_id,'contact_score_json':json.dumps(contact_score_json)}
	url = base_url + '/server/update_contact_score'
	r = requests.post(url,data = payload)
	response = r.json()
	# print response
	return

def get_contact_score_list(email_id,contact_list):
	contact_list = map(lambda x:x.encode('ascii','ignore').lower(),contact_list)
	contact_list_string = ','.join(  map(   lambda x:str(x.encode('ascii','encode')) ,  contact_list )         )
	payload = {'email_id':email_id,'email_id_list':contact_list_string}
	url = base_url + '/server/get_contact_score_list'
	r = requests.post(url,data = payload)
	response = r.json()
	score_dict = {}
	for contact_email_id in contact_list:
		score_dict[contact_email_id] = 0.0
	if response['success'] != 'true':
		return score_dict
	for contact_email_id in contact_list:
		score_dict[contact_email_id] = response[contact_email_id]
	return score_dict

def get_last_updated_time_stamp(email_id):
	payload = {'email_id':email_id}
	url = base_url + '/server/get_last_updated_time_stamp'
	r = requests.post(url,data = payload)
	response = r.json()
	# print response
	if response['success'] != 'true':
		print response
		return helper.get_old_time_stamp_by_minute(60)
	return int(response['time_stamp'])

def set_last_updated_time_stamp(email_id,time_stamp):
	payload = {'email_id':email_id,'last_updated_time':time_stamp}
	url = base_url + '/server/set_last_updated_time_stamp'
	r = requests.post(url,data = payload)
	response = r.json()
	if response['success'] != 'true':
		print 'unable to update !'
		print response
	else:
		# print 'update successful'
		pass
	return int(response['now_time'])


def get_white_list():
	payload = {}
	url = base_url + '/server/get_white_list'
	r = requests.post(url,data = payload)
	response = r.json()
	if response['success'] != 'true':
		print 'unable to get whitelist for this session !'
		# print response
		return []
	return map(lambda x:str(x),response["word_list"])


def store_cursor(email_id,cursor):
	payload = {}
	payload["email_id"] = email_id
	payload["cursor"] = cursor
	url = base_url + '/server/store_cursor'
	r = requests.post(url,data = payload)
	response = r.json()
	# print 'store response'
	# print response
	# print '************'
	if response['success'] != 'true':
		print 'unable store cursor for !' + email_id
		# print response
	return

def get_cursor(email_id,token):
	payload = {}
	payload["email_id"] = email_id
	payload["token"] = token
	url = base_url + '/server/get_cursor'
	r = requests.post(url,data = payload)
	
	# print r


	response = r.json()

	# print response

	# quit()
	if response['success'] != 'true':
		print 'unable get cursor for !' + email_id
		# print response
	return response["cursor"]

def send_push_notification(email_id,title,body,data = {}):
	payload = {}
	payload["email_id"] = email_id
	payload["data"] = json.dumps(data)
	payload["title"] = title
	payload["body"] = body
	
	url = base_url + '/server/send_push_to_user'
	r = requests.post(url,data = payload)
	response = r.json()
	print response
	if response['success'] != 'true':
		print 'unable to send push notification to ' + email_id
		# print response
	return

def add_thread_to_reminder_list(email_id,max_time,thread_id,msg_id,auto_ask,subject):
	payload = {'email_id':email_id,'max_time':max_time,'thread_id':thread_id,
		'msg_id':msg_id,'auto_ask':auto_ask,'subject':subject}
	url = base_url + '/server/add_thread_to_reminder_list'
	r = requests.post(url,data = payload)
	# print r
	response = r.json()
	# print response
	if response['success'] != 'true':
		return False
	return True



def get_expired_threads_in_reminder_list(email_id,max_time):
	payload = {'email_id':email_id,'max_time':max_time}
	
	# print payload	

	url = base_url + '/server/get_expired_threads_in_reminder_list'
	r = requests.post(url,data = payload)
	# print r
	# print '******************'
	# print r.text
	# print '******************'
	response = r.json()
	# print response
	if response['success'] != 'true':
		print r.text
		return []
	return response["thread_list"]

def remove_thread_from_reminder_list(email_id,thread_id):
	payload = {'email_id':email_id,'thread_id':thread_id}
	url = base_url + '/server/remove_thread_from_reminder_list'
	r = requests.post(url,data = payload)
	# print r
	response = r.json()
	# print response
	if response['success'] != 'true':
		print r.text
		return False
	return True

def send_mail_to_users(sender_id,sender_name,receiver_list,subject,body,msg_id = None):
	if sender_id is None:
		sender_id = 'reminders@plancklabs.com'
	if  sender_name is None:
		sender_name = 'Reminders Planck Labs'
	payload = {'sender_id':sender_id,'sender_name':sender_name,
		'receiver_list':receiver_list,'body':body,'msg_id':msg_id,'subject':subject}
	url = base_url + '/server/send_mail_to_users'
	r = requests.post(url,data = payload)
	# print r
	# print r.text
	response = r.json()
	# print response
	if response['success'] != 'true':
		print r.text
		return False
	return True

def add_thread_to_followup(email_id,thread_id,current_status,snooze_till,token):
	payload = {'email_id':email_id,'thread_id':thread_id,'current_status':current_status,
		'snooze_till':snooze_till,'token':token}
	url = base_url + '/server/add_thread_to_followup'
	r = requests.post(url,data = payload)
	print r.text
	response = r.json()
	print response
	if response['success'] != 'true':
		print r.text
		# print response
	return

def get_expired_threads_from_followup(email_id,max_time):
	payload = {'email_id':email_id,'max_time':max_time}
	url = base_url + '/server/get_expired_threads_from_followup'
	r = requests.post(url,data = payload)
	print r.text
	response = r.json()
	print response
	if response['success'] != 'true':
		print r.text
		# print response
		return []
	return response["expired_thread_list"]

def remove_thread_from_followup(email_id,thread_id,token):
	payload = {'email_id':email_id,'token':token,'thread_id':thread_id}
	url = base_url + '/server/remove_thread_from_followup'
	r = requests.post(url,data = payload)
	print r.text
	response = r.json()
	print response
	if response['success'] != 'true':
		print r.text
		# print response
		return False
	return True

#uses prioritizer url
def get_new_blacklist(email_id):
	payload = {'email_id':email_id}
	url = prioritizer_url + '/api/get_new_blacklist/'
	r = requests.post(url,data = payload)
	response = r.json()
	# print response
	if response['success'] != 'true':
		print 'Unable to get blacklist for email_id: '+email_id
		# print response
		return []
	return map(lambda x:str(x),response["blacklist_new"])

#uses prioritizer url
def get_blacklist(email_id):
	payload = {'email_id':email_id}
	url = prioritizer_url + '/api/get_blacklist/'
	r = requests.post(url,data = payload)
	response = r.json()
	# print response
	if response['success'] != 'true':
		print 'Unable to get blacklist for email_id: '+email_id
		# print response
		return []
	# print response["blacklist"]
	return map(lambda x:str(x['email']),response["blacklist"])

#uses prioritizer url
def remove_from_new_blacklist(email_id, black_email):
	payload = {'email_id':email_id, 'blacklist_id':black_email}
	url = prioritizer_url + '/api/remove_from_new_blacklist/'
	r = requests.post(url,data = payload)
	response = r.json()
	if response['success'] != 'true':
		print 'Error on request. Unable to remove from',black_email,'from blacklist of email_id: '+email_id

def get_contact(email_id, contact_email_id):
	payload = {'email_id':email_id, 'contact_email_id':contact_email_id}
	url = prioritizer_url + '/api/get_contact/'
	r = requests.post(url,data = payload)
	response = r.json()
	if response['success'] != 'true':
		return None
	else:
		return response['contact_json']

def get_daily_digest_time(user_list):
	user_list_string = ';'.join( map(lambda x:str(x.encode('ascii','encode')), user_list))
	payload = {'email_id':user_list_string}
	url = base_url + '/server/get_daily_digest_time'
	r = requests.post(url,data = payload)
	response = r.json()

	if response['success'] != 'true':
		print 'unable to get daily digest time for this session !'
		# print response
		return []
	dtimes = map(lambda x:str(x),response["time"].split(";"))
	import datetime
	digest_time = [datetime.datetime.strptime(x,"%H:%M").time() if x != "" else datetime.time(21,0) for x in dtimes]
	return digest_time

def get_timezones(user_list):
	user_list_string = ';'.join(map(lambda x:str(x.encode('ascii','encode')), user_list))
	payload = {'email_id':user_list_string}
	url = base_url + '/server/get_timezone'
	r = requests.post(url,data = payload)
	response = r.json()
	if response['success'] != 'true':
		print 'unable to get timezones for this session !'
		# print response
		return ['UTC' for user in user_list]
	tz = map(lambda x:str(x),response["timezone"].split(";"))
	timezones = [timezone if timezone != "" else "UTC" for timezone in tz]
	return timezones

def get_last_digest_time_stamp(email_id):
	payload = {'email_id':email_id}
	url = base_url + '/server/get_last_digest_time_stamp'
	r = requests.post(url,data = payload)
	response = r.json()
	# print response
	if response['success'] != 'true':
		print response
		return helper.get_old_time_stamp(1)
	return int(response['time_stamp'])

def set_last_digest_time_stamp(email_id,time_stamp):
	payload = {'email_id':email_id,'last_digest_time':time_stamp}
	url = base_url + '/server/set_last_digest_time_stamp'
	r = requests.post(url,data = payload)
	response = r.json()
	if response['success'] != 'true':
		print 'unable to update !'
		print response
	else:
		# print 'update successful'
		pass
	return int(response['now_time'])

def get_last_mail_count_timestamp(email_id):
	payload = {'email_id':email_id}
	url = base_url + '/server/get_last_mail_count_timestamp'
	r = requests.post(url,data = payload)
	response = r.json()
	# print response
	if response['success'] != 'true':
		# print response
		return epoch #Jan 1, 1990, Assuming current email clients didn't exist earlier
		# return helper.get_old_time_stamp_by_minute(60)
	return int(response['time_stamp'])

def set_last_mail_count_timestamp(email_id,time_stamp):
	payload = {'email_id':email_id,'last_mail_count_time':time_stamp}
	url = base_url + '/server/set_last_mail_count_timestamp'
	r = requests.post(url,data = payload)
	response = r.json()
	if response['success'] != 'true':
		print 'unable to update !'
		print response
	else:
		# print 'update successful'
		pass
	return int(response['now_time'])

def update_contact_mail_counts(email_id, contacts, counts):
	contact_string = ";".join(contacts)
	count_string = ";".join(counts)
	payload = {'email_id':email_id, 'contact_email_id':contact_string, 'counts':count_string}

	url = base_url + "/server/update_contact_mail_counts"
	r = requests.post(url, data=payload)
	response = r.json()

	if(response['success'] != 'true'):
		print 'unable to update contact count ',email_id
		print response

def update_daily_digest_threads(email_id, thread_ids):
	if len(thread_ids) <= 0:
		return
	threadstring = ";".join(thread_ids)
	payload = {'email_id':email_id, 'digest_threads':threadstring}
	url = base_url+'/server/update_daily_digest_threads'
	
	r = requests.post(url, data=payload)
	response = r.json()

	if response['success'] != 'true':
		raise ValueError("Could not update digest threads on the server")