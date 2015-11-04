import token_store
import requests
import nylas_helper

def from_email_ids(email_id,single_delta_object):
	object_type = single_delta_object["object"]
	if(object_type == "thread"):
		return filter(lambda x:x['email'].lower() != email_id.lower(),single_delta_object['attributes']['participants'])
	elif(object_type == "message"):
		return single_delta_object["attributes"]["from"]
	else:
		return []

def get_object_info(email_id,single_delta_object):
	single_delta_info = {}
	single_delta_info["participants"] = from_email_ids(email_id,single_delta_object)
	single_delta_info["snippet"] = single_delta_object["attributes"]["snippet"]
	single_delta_info["subject"] = single_delta_object["attributes"]["subject"]
	single_delta_info["object"] = single_delta_object["object"]
	return single_delta_info

def get_info_from_delta_object(email_id,delta_list):
	delta_info_list = [None] * len(delta_list)
	i = 0 
	for delta_object in delta_list:
		delta_info_list[i] = get_object_info(delta_object)
		i += 1
	return delta_info_list

def get_delta(email_id,token):
	cursor_param = {}
	cursor = token_store.get_cursor(email_id,token)
	cursor_param["cursor"] = cursor
	delta_changes = []
	cursor_end = None
	while True:
		r = requests.get('https://api.nylas.com/delta', params = cursor_param, auth = (token, ''))
		r_json = r.json()
		cursor_start = r_json["cursor_start"]
		cursor_end = r_json["cursor_end"]
		delta_changes = delta_changes + r_json["deltas"]
		if cursor_start == cursor_end:
		    break
	if cursor_end != cursor:
		token_store.store_cursor(email_id,token,cursor)
	return delta
    
def send_push_using_delta_info(email_id,delta_info):
	push_content = get_push_content(delta_info)
	token_store.send_push_notification(email_id,push_content)
	return

def get_push_content(delta_info):
	push_data = {}

	return push_data

def get_deltas_to_push(email_id,token,delta_info_list,white_list):
	request_set = set([])
	for delta_info in delta_info_list:
		plist = delta_info["participants"]
		for participant in plist:
			request_set.add(participant)
	score_dict = token_store.get_contact_score_list(email_id,list(request_set))
	good_deltas = filter(lambda x:nylas_helper.is_object_important(x,white_list,score_dict,list(request_set)))
	return good_deltas

def run_push_for_user(email_id,white_list):
	token = token_store.get_token(email_id)
	delta = get_delta(email_id,token)
	if len(delta) == 0 :
		return
	# we have got some changes
	delta_info_list = get_info_from_delta_object(email_id,delta)
	deltas_to_push = get_deltas_to_push(email_id,token,delta_info_list,white_list)
	if(len(deltas_to_push) > 0):
		send_push_using_delta_info(email_id,deltas_to_push)
	return


def run_push_for_all_users():
	# user_list = token_store.get_email_prio_users()
	user_list = ['souravmathlover@gmail.com']
	white_list = token_store.get_white_list()
	for email_id in user_list:
		run_push_for_user(email_id,white_list)
	return


run_push_for_all_users()

# while True:
# 	try:
# 		run_push_for_all_users()
# 		# quit()
# 	except Exception as e:
# 		print 'push crashed !' + ' Exception : {' + str(e) + '}'
# 	time.sleep(1000)
