import token_store
import requests
import nylas_helper
import json
import helper
import time

def is_thread_replied(email_id,thread,first_msg,nylas_client):
	# print thread
	message_id_list = thread["message_ids"]

	other_threads = message_id_list.remove(first_msg)

	for message_id in message_id_list:
		message_object = nylas_client.messages.find(message_id)
		from_email_id = message_object["from"][0]["email"].lower()
		if from_email_id != email_id.lower():
			# got reply in the same thread from a different id
			return True
	return False

def send_reminder(email_id,thread,subject,auto_ask,msg_id):
	
	sender_id = "reminders@plancklabs.com"
	sender_name = 'Planck Reminders'
	participants = filter(lambda x:x['email'].lower() != email_id.lower(),thread['participants'])
	unique_first_name_list = list(set([x['name'] for x in participants]))

	first_name_list = ', '.join(unique_first_name_list)
	
	# send mail to sender
	receiver_list = json.dumps([{'email':email_id}])
	sender_subject = subject
	sender_body = "Hi, you asked me to remind you, if no replies are received to the thread with subject \""+sender_subject+"\". Please take necessary action\n\nThank you,"
	token_store.send_mail_to_users(sender_id,sender_name,receiver_list,sender_subject,sender_body,'')

	# send mail to receivers if required
	if(auto_ask == 1):
		sender_name = email_id
		sender_id = email_id
		receiver_list = json.dumps(participants)
		sender_subject = ''
		sender_body = 'Hi, This is a gentle reminder that '+sender_name+' is waiting for your reply to the thread with subject "'+sender_subject+'". Please reply at your convenience.\n\nThank you,'
		#TODO: reply to the same thread
		token_store.send_mail_to_users(sender_id,sender_name,receiver_list,
			sender_subject,sender_body,msg_id)
		print "sent mail to all"
	return

def manage_expired_threads(email_id, expired_thread_list):
	token = token_store.get_token(email_id)
	nylas_client = nylas_helper.get_nylas_client(token)
	for thread in expired_thread_list:
		auto_ask = int(thread["auto_ask"])
		first_msg = thread["first_msg"]
		thread_id = thread["id"]
		subject = thread["subject"]

		thread_object = nylas_client.threads.find(thread_id)
		# print thread_object


		if(is_thread_replied(email_id,thread_object,first_msg,nylas_client)):
			print "thread is replied"
			token_store.remove_thread_from_reminder_list(email_id,thread_id)
		else:
			print "thread is not replied"
			send_reminder(email_id,thread_object,subject,auto_ask,first_msg)
	return


def run_reminder_sender_for_user(email_id):
	current_time_stamp = helper.get_current_time_stamp()
	expired_thread_list = token_store.get_expired_threads_in_reminder_list(email_id,current_time_stamp)
	
	print expired_thread_list

	if len(expired_thread_list) > 0:
		print 'expired threads found'
		manage_expired_threads(email_id,expired_thread_list)
	else:
		print 'no expired thread found for ' + email_id

	return


def run_reminder_sender_for_all_users():
	user_list = token_store.get_email_prio_users()
	# print user_list
	user_list = ['kumar.sachin52@gmail.com']
	for email_id in user_list:
		print '***************************'
		print email_id
		try:
			run_reminder_sender_for_user(email_id)
		except Exception as e:
			print "reminder sender crashed for " + email_id + "exp {" + str(e) + "}"
	return


# run_reminder_sender_for_all_users()

while True:
	try:
		run_reminder_sender_for_all_users()
	except Exception as e:
		print 'reminder sender crashed !' + ' Exception : {' + str(e) + '}'
	# quit()
	time.sleep(3600)

