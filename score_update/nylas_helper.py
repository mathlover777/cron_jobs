import nylas
import helper
import json
import sys
import token_store
import time
import re

# APP_ID = 'cow3ntxewcbvdvtulazbm2fwv'
# APP_SECRET = '56m1p8lujvmxpf9w58vdrv8ed'

APP_ID = '5girg6tjmjuenujbsg0lnatlq'
APP_SECRET = '8fokx1yoht10ypwdgev3rqqlp'

def get_msg_count_in_range(future_time_stamp,past_time_stamp,email,token,direction):
	client = nylas.APIClient(APP_ID, APP_SECRET, token)
	# print "get_msg_count_in_range"
	# message_list = client.namespaces[0].messages.where(**{direction:email,'last_message_before' : future_time_stamp,\
	# 	'last_message_after' : past_time_stamp})
	message_list = client.messages.where(**{direction:email,'last_message_before' : future_time_stamp,\
		'last_message_after' : past_time_stamp})
	# print future_time_stamp,time.strftime("%D %H:%M", time.localtime(int(future_time_stamp)))
	# print past_time_stamp,time.strftime("%D %H:%M", time.localtime(int(past_time_stamp)))
	sent_people_stat = {}
	for message in message_list:
		# print message
		for sent_address in message['to']:
			sent_address_email = sent_address['email']
			if sent_address_email in sent_people_stat:
				sent_people_stat[sent_address_email] += 1
			else:
				sent_people_stat[sent_address_email] = 1
	with open('temp_data.json','wb') as fp:
		json.dump(sent_people_stat,fp = fp,indent = 4)
	return sent_people_stat




def get_thread_participant_score_with_tags(future_time_stamp,past_time_stamp,token,tag,self_email):
	client = nylas.APIClient(APP_ID, APP_SECRET, token)
	# thread_list = client.namespaces[0].threads.where(**{'tag':tag,'last_message_before' : future_time_stamp,\
	# 	'last_message_after' : past_time_stamp})

	# thread_list = client.threads.where(**{'tag':tag,'last_message_before' : future_time_stamp,\
	# 	'last_message_after' : past_time_stamp})  # depreciated tags api

	thread_list = client.threads.where(**{tag:True,'last_message_before' : future_time_stamp,\
		'last_message_after' : past_time_stamp}) # here we are directly using "high level flags" inspead of tags

	exp_count = 0
	nexp_count = 0
	people_stat = {}
	for thread in thread_list:
		# pprint.pprint(thread)
		participant_set = set([ x['email'] for x in thread['participants'] ])
		try:
			participant_set.remove(self_email)
			nexp_count += 1
		except:
			exp_count += 1
		for participant in participant_set:
			if participant in people_stat:
				people_stat[participant] += 1
			else:
				people_stat[participant] = 1
	# print 'exp_count : ',exp_count
	# print 'nexp_count : ',nexp_count
	return people_stat

def get_msg_score(email,token):
	# current_time_stamp = get_current_time_stamp()
	upto_weeks = 4
	# past_time_stamp = get_old_time_stamp(7)
	# token = get_access_token(email)
	# get_sent_msg_count_in_range(current_time_stamp,past_time_stamp,email,token)
	sent_stat = [None] * upto_weeks
	receive_stat = [None] * upto_weeks
	unread_stat = [None] * upto_weeks
	# unseen_stat = [None] * upto_weeks
	# print "get_msg_score"
	for i in xrange(0,upto_weeks):
		# print 'i = ',i
		if i == 0:
			future_time_stamp = helper.get_current_time_stamp()
		else:
			future_time_stamp = helper.get_old_time_stamp(i*7)
		past_time_stamp = helper.get_old_time_stamp((i+1) * 7)
		sent_stat[i] = get_msg_count_in_range(future_time_stamp,past_time_stamp,email,token,'from')
		# print 'sent_stat'
		receive_stat[i] = get_msg_count_in_range(future_time_stamp,past_time_stamp,email,token,'to')
		# print 'receive_stat'
		unread_stat[i] = get_thread_participant_score_with_tags(future_time_stamp,past_time_stamp,token,'unread',email)
		# print 'unread_stat'
		# unseen_stat[i] = get_thread_participant_score_with_tags(future_time_stamp,past_time_stamp,token,'unseen',email)
		# print 'unseen_stat'
	helper.save_json('sent_last.json',sent_stat)
	helper.save_json('receive_last.json',receive_stat)
	helper.save_json('unread_last.json',unread_stat)
	# helper.save_json('unseen_last.json',unseen_stat)

	return

# get_sent_msg_score('souravmathlover@gmail.com')

def get_recent_contact_from_single_data(data):
	S = set()
	for period_data in data:
		S = S.union(period_data.keys())
	return S

def get_recent_contact(data_list):
	S = set()
	for data in data_list:
		S = S.union(get_recent_contact_from_single_data(data))
	return S


def get_count_if_exist_else_zero(data,email):
	if email in data:
		return data[email]
	return 0

def compute_primitive_score(email):
	sent_stat = helper.load_json('sent_last.json')
	receive_stat = helper.load_json('receive_last.json')
	unread_stat = helper.load_json('unread_last.json')
	# unseen_stat = helper.load_json('unseen_last.json')

	# recent_contact = get_recent_contact([sent_stat,receive_stat,unread_stat,unseen_stat])
	recent_contact = get_recent_contact([sent_stat,receive_stat,unread_stat])

	# pprint.pprint(recent_contact)

	score = {}

	for contact in recent_contact:
		sent_score = 4 * get_count_if_exist_else_zero(sent_stat[0],contact) +\
			3 * get_count_if_exist_else_zero(sent_stat[1],contact) +\
			2 * get_count_if_exist_else_zero(sent_stat[2],contact) +\
			1 * get_count_if_exist_else_zero(sent_stat[3],contact)
		receive_score = 4 * get_count_if_exist_else_zero(receive_stat[0],contact)+\
			3 * get_count_if_exist_else_zero(receive_stat[1],contact) +\
			2 * get_count_if_exist_else_zero(receive_stat[2],contact) +\
			1 * get_count_if_exist_else_zero(receive_stat[3],contact)
		unread_score = 0 * get_count_if_exist_else_zero(unread_stat[0],contact)+\
			3 * get_count_if_exist_else_zero(unread_stat[1],contact) +\
			2 * get_count_if_exist_else_zero(unread_stat[2],contact) +\
			1 * get_count_if_exist_else_zero(unread_stat[3],contact)
		# unseen_score = 0 * get_count_if_exist_else_zero(unseen_stat[0],contact)+\
		# 	3 * get_count_if_exist_else_zero(unseen_stat[1],contact) +\
		# 	2 * get_count_if_exist_else_zero(unseen_stat[2],contact) +\
		# 	1 * get_count_if_exist_else_zero(unseen_stat[3],contact)
		# score[contact] = sent_score + receive_score - unread_score - unseen_score
		score[contact] = sent_score + receive_score - unread_score

	helper.save_json('score.json',score)

	return score

def get_recent_contact_score(email_id,token):
	# print "get_recent_contact_score"
	get_msg_score(email_id,token)
	score_list = compute_primitive_score(email_id)
	return score_list

def get_other_participants_in_thread(thread,email_id):
	# print thread
	participants = [x['email'] for x in thread['participants']]
	if len(participants) == 1:
		return participants
	plist  = filter(lambda x:x != email_id,participants)
	return plist


def get_id(ns,display_name):
	labels = ns.labels.all()
	label_id_list = [(x['display_name'],x['id']) for x in labels]
	for label_display_name,label_id in label_id_list:
		if label_display_name == display_name:
			return label_id

def add_label(ns, display_name):
	label = ns.labels.create(display_name=display_name)
	label.save()
	msg = display_name + ' added'
	# print msg
	return label.get('id')

def add_folder(ns, display_name):
	folder = ns.folders.create(display_name=display_name)
	folder.save()
	msg = display_name + ' added'
	# print msg
	return folder.get('id')

def get_folder_id(ns,display_name):
	labels = ns.folders.all()
	label_id_list = [(x['display_name'],x['id']) for x in labels]
	for label_display_name,label_id in label_id_list:
		if label_display_name == display_name:
			return label_id

def get_email_domain(email_id):
	email_str = email_id.encode('ascii','ignore')
	domain = re.search("@[\w.]+", email_str)
	return str(domain.group())

def use_labels(ns):
	if(ns.account['organization_unit'] == 'label'):
		return True
	return False

def tag_thread_given_condition(thread, label_flag, id_remove, id_add, score, boolean_flags):
	if label_flag:
		# use labels
		thread.remove_label(id_remove)
		thread.add_label(id_add)
	else:
		# use folder
		if score > 0 or boolean_flags:
			return
		thread.update_folder(id_add)
	return

def add_thread_to_clutter(thread, label_flag, clutter_id):
	if(label_flag):
		thread.update_labels([clutter_id])
	else:
		thread.update_folder(clutter_id)

def add_thread_to_social(thread, label_flag, social_id):
	if label_flag:
		# use labels
		thread.add_label(social_id)
	else:
		thread.update_folder(social_id)

def add_thread_to_blacklist(thread, label_flag, blacklist_id):
	if(label_flag):
		thread.update_labels([blacklist_id])
	else:
		thread.update_folder(blacklist_id)

def is_white_listed_mail(subject_line,white_list):
	subject_line = subject_line.lower()
	normalized_white_list_set = set(white_list) # the api already gives normalized strings
	
	for word in normalized_white_list_set:
		p = re.compile(word)
		if re.search(p,subject_line) is not None:
			return True

	return False

def is_social_mail(email_id, subject, participants, social_list):
	for word in social_list:
		p = re.compile(word)
		for participant in participants:
			if(participant['email'] != email_id):
				if re.search(p, participant['email']) is not None or re.search(p, participant['name']) is not None:
					return True
	return False

def contains_contact(email_id, participants):
	for participant in participants:
		if token_store.get_contact(email_id, participant) is not None:
			return True
	return False

def is_spam_thread(thread, label_flag):
	if label_flag:
		labelnames = [label['name'] for label in thread['_labels']]
		if('spam' in labelnames or 'junk' in labelnames):
			return True
	else:
		foldernames = [folder['name'] for folder in thread['_folders']]
		if('spam' in foldernames or 'junk' in foldernames):
			return True

	return False

def tag_unread_mails_in_time_range(email_id,token,now_time,old_time,white_list, social_list=[]):
	client = nylas.APIClient(APP_ID, APP_SECRET, token)
	ns = client

	recent_threads = ns.threads.where(**{'last_message_after':old_time-600,'last_message_before' :now_time, 'in':'inbox'})
	# recent_threads = ns.threads.where(**{'from':'dipayan1992@gmail.com', 'in':'inbox'})
	recent_threads_list = [x for x in recent_threads]

	request_set = set([])
	for thread in recent_threads_list:
		# print thread['participants']
		plist = get_other_participants_in_thread(thread,email_id)
		for participant in plist:
			request_set.add(participant)
	
	score_dict = token_store.get_contact_score_list(email_id,list(request_set))

	if use_labels(ns):
		read_now_id = get_id(ns,'Read Now')
		read_later_id = get_id(ns,'Read Later')
		social_id = get_id(ns, 'Social')
		if social_id is None:
			social_id = add_label(ns, 'Social')
		blacklist_id = get_id(ns, 'Black Hole')
		if(blacklist_id is None):
			blacklist_id = add_label(ns, 'Black Hole')

		label_flag = True
	else:
		read_now_id = get_folder_id(ns,'Read Now')
		read_later_id = get_folder_id(ns,'Read Later')
		social_id = get_folder_id(ns, 'Social')
		if social_id is None:
			social_id = add_folder(ns, 'Social')
		blacklist_id = get_folder_id(ns, 'Black Hole')
		if(blacklist_id is None):
			blacklist_id = add_folder(ns, 'Black Hole')

		label_flag = False
	
	for thread in recent_threads_list:
		# TODO refactor using is_object_important
		plist = get_other_participants_in_thread(thread,email_id)

		blacklist = token_store.get_blacklist(email_id)
		blacklist_flag = False
		if(len(plist) == 1):
			if(plist[0].lower() in blacklist):
				blacklist_flag = True

		if(blacklist_flag):
			print 'INFO:', email_id, thread['id'], "B"
			add_thread_to_blacklist(thread, label_flag, blacklist_id)
			continue

		social_list_flag = is_social_mail(email_id, thread['subject'], thread['participants'], social_list)
		white_list_flag = is_white_listed_mail(thread['subject'],white_list)
		contact_flag = contains_contact(email_id, plist)

		score = 0.0
		for participant in plist:
			score += score_dict[participant.encode('ascii','ignore').lower()]

		boolean_flags = white_list_flag or contact_flag
		# print "C", contact_flag

		if score > 0 or boolean_flags:
			tag_thread_given_condition(thread,label_flag,read_later_id,read_now_id,score,boolean_flags)
			# print 'INFO:',email_id, thread['id'],"N"
		else:
			if(social_list_flag):
				# print 'INFO:',email_id,thread['id'],"S", 
				add_thread_to_social(thread, label_flag, social_id)
				continue
			add_thread_to_clutter(thread, label_flag, read_later_id)
			# tag_thread_given_condition(thread,label_flag,read_now_id,read_later_id,score,boolean_flags)
			# print 'INFO:',email_id, thread['id'],"L"
	return

def get_nylas_client(token):
	return nylas.APIClient(APP_ID, APP_SECRET, token)

def is_object_important(delta_object,white_list,score_dict,other_participant_list):
	
	# print score_dict
	# print other_participant_list

	white_list_flag = is_white_listed_mail(delta_object['subject'],white_list)
	score = 0.0
	for participant in other_participant_list:
		score += score_dict[participant.encode('ascii','ignore').lower()]	
	boolean_flags = white_list_flag
	if(boolean_flags or score > 0.0):
		# its a good object
		return True
	return False

def tag_recent_unread_mails(email_id,token,white_list, social_list=[]):
	# this will retrieve the all unread threads
	# now depending on the people involved in the thread other than the current
	# it will check mails only on the last 60 mins

	old_time = token_store.get_last_updated_time_stamp(email_id)
	# print time.strftime("%D %H:%M", time.localtime(int(old_time))), 
	now_time = token_store.set_last_updated_time_stamp(email_id,0)
	# print old_time, now_time
	# now_time = helper.get_current_time_stamp()
	# print time.strftime("%D %H:%M", time.localtime(int(now_time)))

	tag_unread_mails_in_time_range(email_id,token,now_time,old_time,white_list, social_list)
	
	return

def archive_old_blacklist_mails(email_id, token):
	blacklist = token_store.get_new_blacklist(email_id)
	client = nylas.APIClient(APP_ID, APP_SECRET, token)
	ns = client
	
	label_flag = use_labels(ns)
	if(label_flag):
		blacklist_id = get_id(ns, 'Black Hole')
		if(blacklist_id is None):
			blacklist_id = add_label(ns, 'Black Hole')
	else:
		blacklist_id = get_folder_id(ns, 'Black Hole')
		if(blacklist_id is None):
			blacklist_id = add_folder(ns, 'Black Hole')

	for black_email in blacklist:
		for message in ns.messages.where(**{'from':black_email}):
			if(label_flag):
				message.update_labels([blacklist_id])
			else:
				message.update_folder(blacklist_id)

		token_store.remove_from_new_blacklist(email_id, black_email)