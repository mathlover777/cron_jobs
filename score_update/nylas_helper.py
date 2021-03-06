from BeautifulSoup import BeautifulSoup
import nylas
import helper
import json
import sys
import token_store
import time
import re

# APP_ID = 'cow3ntxewcbvdvtulazbm2fwv'
# APP_SECRET = '56m1p8lujvmxpf9w58vdrv8ed'
prioritizer_url = 'http://planckapi-prioritizer.us-west-1.elasticbeanstalk.com'
use_psync = False

PLANCK_APP_ID = '83fs5bk9kzm5pz3sq2gacsg2d'
PLANCK_APP_SECRET = 'xjhwaych6ufut6xn77qp5kavp'
psync_url = 'https://sync-dev.planckapi.com'
nylas_url = 'https://api.nylas.com'

APP_ID = '5girg6tjmjuenujbsg0lnatlq'
APP_SECRET = '8fokx1yoht10ypwdgev3rqqlp'

digest_client_email = 'message-digest@plancklabs.com'
planck_mails = set([digest_client_email])

def set_psync(use_sync):
	use_psync = use_sync

####Functions for Score update of users for prioritization####

def get_msg_count_in_range(future_time_stamp,past_time_stamp,email,token,direction, use_psync):
	if use_psync:
		client = nylas.APIClient(PLANCK_APP_ID, PLANCK_APP_SECRET, token, api_server=psync_url)
	else:
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

def get_thread_participant_score_with_tags(future_time_stamp,past_time_stamp,token,tag,self_email, use_psync):
	if use_psync:
		client = nylas.APIClient(PLANCK_APP_ID, PLANCK_APP_SECRET, token, api_server=psync_url)
	else:
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

def get_msg_score(email,token, use_psync):
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
		sent_stat[i] = get_msg_count_in_range(future_time_stamp,past_time_stamp,email,token,'from', use_psync)
		# print 'sent_stat'
		receive_stat[i] = get_msg_count_in_range(future_time_stamp,past_time_stamp,email,token,'to', use_psync)
		# print 'receive_stat'
		unread_stat[i] = get_thread_participant_score_with_tags(future_time_stamp,past_time_stamp,token,'unread',email, use_psync)
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

def compute_primitive_score(email, use_psync):
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

def get_recent_contact_score(email_id,token, use_psync):
	# print "get_recent_contact_score"
	get_msg_score(email_id,token, use_psync)
	score_list = compute_primitive_score(email_id, use_psync)
	return score_list

####Functions for email prioritizer####

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

def add_thread_to_readnow(thread, label_flag, inbox_id, read_now_id, read_later_id):
	if label_flag:
		# use labels
		thread.remove_label(read_later_id)
		thread.add_label(inbox_id)
		# thread.add_label(read_now_id)
	#no need to update folders in case of read now. The mail remains in inbox
	return

def add_thread_to_clutter(thread, label_flag, inbox_id, read_now_id, clutter_id):
	if(label_flag):
		thread.remove_label(read_now_id)
		thread.remove_label(inbox_id)
		thread.add_label(clutter_id)
	else:
		thread.update_folder(clutter_id)

def add_thread_to_social(thread, label_flag, inbox_id, read_now_id, social_id):
	if label_flag:
		# use labels
		thread.remove_label(read_now_id)
		thread.remove_label(inbox_id)
		thread.add_label(social_id)
	else:
		thread.update_folder(social_id)

def add_thread_to_blacklist(thread, label_flag, blacklist_id):
	if(label_flag):
		thread.update_labels([blacklist_id])
	else:
		thread.update_folder(blacklist_id)

def is_from_planck(participants):
	return len(planck_mails.intersection(set(participants))) > 0

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

def get_clean_text(content):
	content = re.sub(r'(<!DOCTYPE[^>]*>)|(&\S*;)|(https?:\/\/\S*)','', content, flags = re.MULTILINE)
	content = ''.join(BeautifulSoup(content).findAll(text=lambda text: text.parent.name != "script" and text.parent.name != "style")).replace("\\n", " ")
	return re.sub(r'[ ]+',' ',content)

def has_html_content(ns, thread, threshold=0.2):
	messages = []
	clean_messages = []
	for message_id in thread['message_ids']:
		m = ns.messages.find(message_id)
		messages.append(len(m['body']))
		clean_messages.append(len(get_clean_text(m['body'])))

	if sum(messages) > 0:
		f_html = 1.0*sum(clean_messages)/sum(messages)

		if f_html < threshold:
			return True
	else:
		return True
	# cleantext = get_clean_text()
	return False

def is_new_contact(ns, old_time, contact_email_id, thread):
	oldthreads = ns.threads.where(**{'from':contact_email_id,'last_message_before':old_time})
	if oldthreads.first() is None:
		if has_html_content(ns, thread):
			return False
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

def overlap(a, b):
	return len(list(set(a) & set(b)))

def tag_unread_mails_in_time_range(email_id,token,now_time,old_time,white_list, social_list=[], use_psync=False):
	if use_psync:
		client = nylas.APIClient(PLANCK_APP_ID, PLANCK_APP_SECRET, token, api_server=psync_url)
	else:
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
		inbox_id = get_id(ns, 'Inbox')
		read_now_id = get_id(ns,'Read Now')
		read_later_id = get_id(ns,'Read Later')
		if read_later_id is None:
			read_later_id = get_id(ns, 'Read Later')
		social_id = get_id(ns, 'Social')
		if social_id is None:
			social_id = add_label(ns, 'Social')
		#as per new rules, mails from blacklisted email ids should be deleted.
		blacklist_id = get_id(ns, 'Trash')
		label_flag = True
	else:
		inbox_id = get_folder_id(ns, 'Inbox')
		read_now_id = get_folder_id(ns,'Read Now')
		read_later_id = get_folder_id(ns,'Read Later')
		if read_later_id is None:
			read_later_id = add_folder(ns, 'Read Later')
		social_id = get_folder_id(ns, 'Social')
		if social_id is None:
			social_id = add_folder(ns, 'Social')

		blacklist_id = get_folder_id(client, 'Trash')
		if blacklist_id is None:
			blacklist_id = get_folder_id(client, 'Deleted Items')
			if blacklist_id is None:
				blacklist_id = add_folder(client, 'Trash')
				print 'Created Trash folder for',email_id

		label_flag = False
	
	for thread in recent_threads_list:
		# TODO refactor using is_object_important
		plist = get_other_participants_in_thread(thread,email_id)
		
		blacklist = token_store.get_blacklist(email_id)
		blacklist_flag = False
		if overlap(plist, blacklist) > 0:
			blacklist_flag = True

		if(blacklist_flag):
			# print 'INFO:', email_id, thread['id'], "B"
			add_thread_to_blacklist(thread, label_flag, blacklist_id)
			continue

		social_list_flag = is_social_mail(email_id, thread['subject'], thread['participants'], social_list)

		important_flag = is_from_planck(plist)
		if not important_flag:
			important_flag = is_white_listed_mail(thread['subject'],white_list)
		if not important_flag:
			important_flag = contains_contact(email_id, plist)
		if not important_flag:
			for p_id in plist:
				important_flag = is_new_contact(ns, old_time-600, p_id, thread)
				if important_flag:
					break

		score = 0.0
		for participant in plist:
			score += score_dict[participant.encode('ascii','ignore').lower()]

		if score > 0 or important_flag:
			#TODO: check if the email is not marked as something else
			add_thread_to_readnow(thread, label_flag, inbox_id, read_now_id, read_later_id)
			# print 'INFO:',email_id, thread['id'],"N"
		else:
			if(social_list_flag):
				# print 'INFO:',email_id,thread['id'],"S", 
				add_thread_to_social(thread, label_flag, inbox_id, read_now_id, social_id)
				continue
			add_thread_to_clutter(thread, label_flag, inbox_id, read_now_id, read_later_id)
			# tag_thread_given_condition(thread,label_flag,read_now_id,read_later_id,score,boolean_flags)
			# print 'INFO:',email_id, thread['id'],"L"
	return

def get_nylas_client(token):
	if use_psync:
		client = nylas.APIClient(PLANCK_APP_ID, PLANCK_APP_SECRET, token, api_server=psync_url)
	else:
		client = nylas.APIClient(APP_ID, APP_SECRET, token)
	return client

def get_nylas_client_(token, psync_use):
	if psync_use:
		client = nylas.APIClient(PLANCK_APP_ID, PLANCK_APP_SECRET, token, api_server=psync_url)
	else:
		client = nylas.APIClient(APP_ID, APP_SECRET, token)
	return client

def tag_recent_unread_mails(email_id,token,white_list, social_list=[], use_psync=False):
	# this will retrieve the all unread threads
	# now depending on the people involved in the thread other than the current
	# it will check mails only on the last 60 mins

	old_time = token_store.get_last_updated_time_stamp(email_id)
	now_time = token_store.set_last_updated_time_stamp(email_id,0)
	# now_time = helper.get_current_time_stamp()
	# print time.strftime("%D %H:%M", time.localtime(int(now_time)))

	tag_unread_mails_in_time_range(email_id,token,now_time,old_time,white_list, social_list, use_psync)

####Used in Push Notification####

def is_object_important(delta_object, blacklist, old_time, email_id, white_list, score_dict, other_participant_list):
	
	# print score_dict
	# print other_participant_list

	#######
	blacklist_flag = False
	if overlap(other_participant_list, blacklist) > 0:
		return False #blacklisted mail

	important_flag = is_from_planck(other_participant_list)
	if not important_flag:
		important_flag = is_white_listed_mail(delta_object['subject'],white_list)
	if not important_flag:
		important_flag = contains_contact(email_id, other_participant_list)
	# if not important_flag:
	# 	important_flag = contains_important_contact(email_id, other_participant_list)
	if important_flag:
		return True

	score = 0.0
	for participant in other_participant_list:
		score += score_dict[participant.encode('ascii','ignore').lower()]

	if score > 0:
		return True
	else:
		return False

####Add to Blacklist triggers this####

def archive_old_blacklist_mails(email_id, token, use_psync):
	blacklist = token_store.get_new_blacklist(email_id)
	if use_psync:
		print token
		client = nylas.APIClient(PLANCK_APP_ID, PLANCK_APP_SECRET, token, api_server=psync_url)
	else:
		client = nylas.APIClient(APP_ID, APP_SECRET, token)
	ns = client
	label_flag = use_labels(ns)
	if(label_flag):
		#as per new rules, mails from blacklisted ids should be deleted
		blacklist_id = get_id(ns, 'Trash')
	else:
		blacklist_id = get_folder_id(ns, 'Trash')
		if(blacklist_id is None):
			blacklist_id = get_folder_id(ns, 'Deleted Items')
			if blacklist_id is None:
				blacklist_id = add_folder(ns, 'Trash')

	for black_email in blacklist:
		for message in ns.messages.where(**{'from':black_email}):
			try:
				if(label_flag):
					message.update_labels([blacklist_id])
				else:
					message.update_folder(blacklist_id)
			except Exception as e:
				pass
				# print 'Could not update label for '+black_email+'. Must be in "sent". Skipping'

		token_store.remove_from_new_blacklist(email_id, black_email)

##blacklist sender helper
def has_sent_label(thread, sent_id):
	for label in thread['_labels']:
		if label['id'] == sent_id:
			return True
	return False

##This function looks at the Black Hole folder and blacklists all the senders
def blacklist_senders(email_id, token, use_psync):
	blacklist = token_store.get_blacklist(email_id)
	if use_psync:
		print token
		client = nylas.APIClient(PLANCK_APP_ID, PLANCK_APP_SECRET, token, api_server=psync_url)
	else:
		client = nylas.APIClient(APP_ID, APP_SECRET, token)
	ns = client
	label_flag = use_labels(ns)
	if(label_flag):
		#as per new rules, mails from blacklisted ids should be deleted
		trash_id = get_id(ns, 'Trash')
		sent_id = get_id(ns, 'Sent Mail')
		print 'sent_id, trash_id', sent_id, trash_id
	else:
		trash_id = get_folder_id(ns, 'Trash')
		if(trash_id is None):
			trash_id = get_folder_id(ns, 'Deleted Items')
			if trash_id is None:
				trash_id = add_folder(ns, 'Trash')

	black_threads = ns.threads.where(**{'in':'Black Hole'})
	black_senders = set()
	for black_thread in black_threads:
		print 'black_thread', black_thread['id']
		if len(black_thread['message_ids']) > 0:
			black_msg = ns.messages.find(black_thread['message_ids'][0])
			for sender in black_msg['from']:
				black_senders.add(sender['email'])

		if label_flag:
			updates = [trash_id]
			if has_sent_label(black_thread, sent_id):
				updates.append(sent_id)
			black_thread.update_labels(updates)
		else:
			black_thread.update_folder(trash_id)

	for sender in black_senders:
		if sender not in blacklist:
			token_store.add_to_blacklist(email_id, sender)

####Daily Digest Functions####

def get_sender_string(email_id, participants):
	partlist = []
	for participant in participants:
		if(participant['email'] == email_id):
			continue
		if participant['name'] == "":
			partlist.append(participant['email'])
		else:
			partlist.append(participant['name'])

	if len(partlist) == 0:
		partlist.append("me")
	if len(partlist) > 4:
		partlist = partlist[:4]
		partlist.append("...")
	return ", ".join(partlist)

def create_html_digest(email_id, displayname, clutterthreads, socialthreads):
	htmltemplatetext = open("html_templates/dailydigest.html").read()
	soup = BeautifulSoup(htmltemplatetext)
	soup, c1, tids1 = create_html_digest_for_label(email_id, clutterthreads, 'readlater', soup)
	soup, c2, tids2 = create_html_digest_for_label(email_id, socialthreads, 'social', soup)

	maar = soup.findAll('a',{'class':'maar'})
	for i in range(len(maar)):
		maar[i]['href'] = prioritizer_url + "/daily_digest/mark_all_as_read?email="+email_id

	archall = soup.findAll('a',{'class':'archall'})
	for i in range(len(archall)):
		archall[i]['href'] = prioritizer_url + "/daily_digest/archive_all?email="+email_id

	delall = soup.findAll('a',{'class':'delall'})
	for i in range(len(delall)):
		delall[i]['href'] = prioritizer_url + "/daily_digest/delete_all?email="+email_id	

	# token_store.update_daily_digest_threads(email_id, tids1+tids2)

	displaynametag = soup.find('span', {'id':'username'})
	if displaynametag is not None:
		displaynametag.contents[0].replaceWith(" "+displayname)

	return str(soup), c1+c2

def create_html_digest_for_label(email_id, threads, label, soup):
	
	threadtable = soup.find('table',{'id':label+'table'})
	threadentrytemplate = open("html_templates/thread.html").read()
	count = 0
	thread_ids = []
	for thread in threads:
		# print 'thread '+label, count
		threadsoup = BeautifulSoup(threadentrytemplate)
		threadtag = threadsoup.first()

		subject = thread['subject']
		outline = thread['snippet']
		thread_ids.append(thread['id'])

		sender = get_sender_string(email_id, thread['participants'])

		sendertag = threadtag.find('span',{'id':'thsender'})
		if sendertag is not None:
			sendertag.contents[0].replaceWith(sender)

		subjecttag = threadtag.find('span',{'id':'thsubject'})
		if subjecttag is not None:
			subjecttag.contents[0].replaceWith(subject)		

		outlinetag = threadtag.find('div',{'id':'thoutline'})
		if outlinetag is not None:
			outlinetag.contents[0].replaceWith(outline)

		inboxonce = threadtag.find('a',{'class':'inboxonce'})
		if inboxonce is not None:
			inboxonce['href']=prioritizer_url+'/daily_digest/inbox_once?email='+email_id+"&id="+thread['id']

		inboxalways = threadtag.find('a',{'class':'inboxalways'})
		if inboxalways is not None:
			inboxalways['href']=prioritizer_url+'/daily_digest/inbox_always?email='+email_id+"&id="+thread['id']

		unsubscribe = threadtag.find('a',{'class':'unsubscribe'})
		if unsubscribe is not None:
			unsubscribe['href']=prioritizer_url+'/daily_digest/unsubscribe?email='+email_id+"&id="+thread['id']

		threadtable.append(threadtag)
		count += 1

	if count > 0:
		labelcounttag = soup.find('span', {'id':label+'number'})
		if labelcounttag is not None:
			labelcounttag.contents[0].replaceWith(" ("+str(count)+")")

	return soup, count, thread_ids		

def get_mails_by_time_range(old_time, now_time, ns, label):
	recent_threads = ns.threads.where(**{'last_message_after':old_time,'last_message_before' :now_time, 'in':label})
	return recent_threads

def send_daily_digest(email_id, token, use_psync, digest_client):
	##highest priority
	old_time = token_store.get_last_digest_time_stamp(email_id)
	now_time = token_store.set_last_digest_time_stamp(email_id,0)
	# old_time = 1463993731
	# now_time = 1464065731
	print old_time, now_time
	
	ns = get_nylas_client_(token, use_psync)
	cluttermails = get_mails_by_time_range(old_time, now_time, ns, "Read Later")
	socialmails = get_mails_by_time_range(old_time, now_time, ns, "Social")

	accountinfo = ns.account
	displayname = accountinfo['name']
	if displayname == "":
		displayname = email_id

	digestbody, count = create_html_digest(email_id, displayname, cluttermails, socialmails)

	if count > 0:
		digest_draft = digest_client.drafts.create()
		digest_draft.to =  [{'email':email_id}]
		digest_draft.subject = str(count)+' message(s) for you to review'
		digest_draft.body = digestbody
		digest_draft.send()

def send_daily_digest_test(email_id, token, use_psync, digest_client):
	##highest priority
	# old_time = token_store.get_last_digest_time_stamp(email_id)
	# now_time = token_store.set_last_digest_time_stamp(email_id,0)
	old_time = 1463990731
	now_time = 1464065731
	print old_time, now_time
	
	ns = get_nylas_client_(token, use_psync)
	cluttermails = get_mails_by_time_range(old_time, now_time, ns, "Read Later")
	socialmails = get_mails_by_time_range(old_time, now_time, ns, "Social")

	accountinfo = ns.account
	displayname = accountinfo['name']
	if displayname == "":
		displayname = email_id
	# print 'D',displayname

	digestbody, count = create_html_digest(email_id, displayname, cluttermails, socialmails)
	# print 'D',digestbody[:10]
	digest_draft = digest_client.drafts.create()

	digest_draft.to =  [{'email':email_id}]
	digest_draft.subject = str(count)+' messages for you to review'
	digest_draft.body = digestbody
	# raw_input("send?")
	digest_draft.send()
	# print "sent"

###Counting mails from contacts###

def is_blacklisted(message, use_label):
	if use_label:
		for label in message['_labels']:
			if label['display_name'] == 'Black Hole':
				return True
	else:
		if message['_folder']['display_name'] == 'Black Hole':
			return True
	return False

def count_contact_wise_mails(email_id, token, use_psync):

	ns = get_nylas_client_(token, use_psync)

	old_time = token_store.get_last_mail_count_timestamp(email_id)
	now_time = int(time.time())
	print old_time, now_time
	from collections import defaultdict
	count = defaultdict(int)
	# if old_time == epoch:
	# 	# raw_input('first time '+email_id)
	# 	print "First time of",email_id
	# 	import requests
	# 	contacts = ns.contacts
	# 	cc = 0
	# 	for contact in ns.contacts:
	# 		url = nylas_url
	# 		if use_psync:
	# 			url = psync_url
	# 		if contact['email'] is not None:
	# 			r = requests.get(url+"/messages?from="+contact['email']+"&in=Read+Later&view=count", auth=(token, ""))
	# 			result = r.json()
	# 			if result.has_key('count'):
	# 				count[contact['email']] = result['count']
	# 				cc+=1
	# 		if cc%100==0:
	# 			print cc


	# else:
		# raw_input('next time '+email_id)
	use_label = use_labels(ns)
	recent_messages = ns.messages.where(**{'last_message_after':old_time,'last_message_before' :now_time, 'in':'Read Later'})
	for message in recent_messages:
		if not is_blacklisted(message, use_label):
			for contact in message['from']:
				if contact['email'] != "":
					count[contact['email']] += 1

	print 'counts done'
	# print count
	if len(count) > 0:
		print 'counts calculated'
	contacts = []
	counts = []
	for email in count.keys():
		if count[email] > 0:
			contacts.append(email)
			counts.append(str(count[email]))
	if len(contacts) > 0:
		token_store.update_contact_mail_counts(email_id, contacts, counts)
	now_time = token_store.set_last_mail_count_timestamp(email_id,now_time)
	print 'updated'


