import token_store
import requests
import nylas_helper
import json
import time
import traceback

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
	try:
		single_delta_info["participants"] = from_email_ids(email_id,single_delta_object)
	except:
		single_delta_info["participants"] = []
	try:
		single_delta_info["snippet"] = single_delta_object["attributes"]["snippet"]
	except:
		single_delta_info["snippet"] = ""
	try:
		single_delta_info["subject"] = single_delta_object["attributes"]["subject"]
	except:
		single_delta_info["subject"] = "" 
	try:
		single_delta_info["object"] = single_delta_object["object"]
	except:
		single_delta_info["object"] = "thread"
	try:
		single_delta_info["unread"] = single_delta_object["attributes"]["unread"]
	except:
		single_delta_info["unread"] = False
	
	return single_delta_info

def get_info_from_delta_object(email_id, delta_list):
	delta_info_list = [None for i in range(len(delta_list))]
	i = 0 
	for delta_object in delta_list:
		delta_info_list[i] = get_object_info(email_id, delta_object)
		i += 1
	return delta_info_list

def get_fresh_cursor(token):
	r = requests.post('https://api.nylas.com/delta/latest_cursor', auth=(token, ''))
	return r.json()["cursor"]

def get_delta(email_id,token):
	cursor_param = {}
	server_cursor = token_store.get_cursor(email_id,token)
	cursor = server_cursor
	# print "cursor : " + cursor
	# quit()
	delta_changes = []
	# print cursor_param
	cursor_end = None
	while True:
		cursor_param["cursor"] = cursor
		r = requests.get('https://api.nylas.com/delta', params = cursor_param, auth = (token, ''))
		r_json = r.json()
		# print r_json
		cursor_start = r_json["cursor_start"]
		cursor_end = r_json["cursor_end"]
		delta_changes = delta_changes + r_json["deltas"]
		
		# print 'start',cursor_start
		# print 'end',cursor_end

		if cursor_start == cursor_end:
		    break
		cursor = cursor_end
	# if server_cursor != cursor:
	token_store.store_cursor(email_id,cursor)
	return delta_changes
    
def send_push_using_delta_info(email_id, delta_info):
	title,body,data = get_push_content(delta_info)
	print "ANDR_DEL: ",email_id
	token_store.send_push_notification(email_id,title,body,data)
	return

def get_push_content(delta_info):

	# print 'delta_info', delta_info

	push_data = {}
	all_participant_list = reduce(lambda x,y:x + y,[x['participants'] for x in delta_info])
	
	unique_first_name_list = list(set([x['name'].split()[0] for x in all_participant_list]))

	first_name_list = ', '.join(unique_first_name_list)
	
	title = "Important Message(s) from"
	if len(delta_info) > 0:
		title = str(len(delta_info))+" "+title

	body = first_name_list
	data = {}
	return title,body,data

def get_deltas_to_push(email_id, token, all_delta_info_list, white_list):
	# print all_delta_info_list
	delta_info_list = filter(lambda x:x["unread"],all_delta_info_list)
	request_set = set([])
	for delta_info in delta_info_list:
		plist = delta_info["participants"]
		# print plist
		for participant in plist:
			request_set.add(participant["email"])
	score_dict = token_store.get_contact_score_list(email_id,list(request_set))
	blacklist = token_store.get_blacklist(email_id)
	old_time = token_store.get_last_updated_time_stamp(email_id)
	# print score_dict

	good_deltas = filter( lambda x:nylas_helper.is_object_important(x, blacklist, old_time, email_id, white_list,score_dict,[y['email'] for y in x['participants']]) , delta_info_list)
	# print good_deltas

	return good_deltas

def run_push_for_user(email_id, white_list):
	token = token_store.get_token(email_id)
	print "token:", token
	delta = get_delta(email_id,token)
	# print delta
	if len(delta) == 0 :
		print "NODEL",email_id
		return
	# we have got some changes
	delta_info_list = get_info_from_delta_object(email_id, delta)
	deltas_to_push = get_deltas_to_push(email_id, token, delta_info_list, white_list)
	if(len(deltas_to_push) > 0):
		# print "push to send !"
		send_push_using_delta_info(email_id,deltas_to_push)
	else:
		print "NODEL: ",email_id
	return


def run_push_for_all_users():
	user_list = token_store.get_email_prio_users()
	# user_list = ['kumar.sachin52@gmail.com', 'souravmathlover@gmail.com', 'rajesh.x.kumar@gmail.com']
	# print user_list
	# user_list = ['souravmathlover@gmail.com']
	white_list = token_store.get_white_list()
	for email_id in user_list:
		try:
			run_push_for_user(email_id,white_list)
		except Exception as e:
			print "push sender crashed for " + email_id + "exp {" + traceback.format_exc() + "}"
	return


# run_push_for_all_users()

while True:
	# try:
	run_push_for_all_users()
	print "##done##"
	# except Exception as e:
		# print 'push crashed !' + ' Exception : {' + str(e) + '}'
	# quit()
	time.sleep(100)

