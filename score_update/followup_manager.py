import token_store
import requests
import nylas_helper
import json
import helper
import time

def manage_expired_threads(email_id,expired_thread_list):
	token = token_store.get_token(email_id)
	for thread_id in expired_thread_list:
		token_store.remove_thread_from_followup(email_id,thread_id,token)
	return

def run_followup_manager_for_user(email_id):
	current_time_stamp = helper.get_current_time_stamp()
	expired_thread_list = token_store.get_expired_threads_from_followup(email_id,current_time_stamp)
	# print expired_thread_list
	if len(expired_thread_list) > 0:
		print 'expired threads found'
		manage_expired_threads(email_id,expired_thread_list)
	else:
		print 'no expired thread found for ' + email_id
	return


def run_followup_manager_for_all_users():
	user_list = token_store.get_email_prio_users()
	# print user_list
	# user_list = ['souravmathlover@gmail.com']
	for email_id in user_list:
		print '***************************'
		print email_id
		try:
			run_followup_manager_for_user(email_id)
		except Exception as e:
			print "reminder sender crashed for " + email_id + "exp {" + str(e) + "}"
	return


# run_followup_manager_for_all_users()

while True:
	try:
		run_followup_manager_for_all_users()
	except Exception as e:
		print 'Followup Manager crashed !' + ' Exception : {' + str(e) + '}'
	# quit()
	time.sleep(3600)
