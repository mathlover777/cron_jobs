import nylas_helper
import token_store
import time
import traceback

source_2 = "nylas"
source = "planck"
use_psync = True

def blacklist_senders(email_id):
	token = token_store.get_token(email_id, source)
	use_psync = True

	if(token == ""):
		token = token_store.get_token(email_id, source_2)
		use_psync = False

	nylas_helper.blacklist_senders(email_id, token, use_psync)
	return

def run_blacklist_senders_for_all_users():
	user_list = token_store.get_email_prio_users()
	# user_list = ['kumar.sachin52@gmail.com']
	# print user_list
	for email_id in user_list:
		try:
			blacklist_senders(email_id)
		except Exception as e:
			print 'blacklist senders background process crashed for ' + email_id + ' Exception : {' + traceback.format_exc() + '}'
	return
while True:
	try:
		run_blacklist_senders_for_all_users()
	except Exception as e:
		print 'blacklist background process crashed' + ' Exception : {' + str(e) + '}'
	time.sleep(60)
