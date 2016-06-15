import nylas_helper
import token_store
import time

source_2 = "nylas"
source = "planck"
use_psync = True

def archive_blacklisted_mails(email_id):
	token = token_store.get_token(email_id, source)
	use_psync = True

	if(token == ""):
		token = token_store.get_token(email_id, source_2)
		use_psync = False

	nylas_helper.archive_old_blacklist_mails(email_id, token, use_psync)
	return

def archive_blacklist_for_all_users():
	# user_list = token_store.get_email_prio_users()
	user_list = ['pavel@plancklabs.com']
	print user_list
	for email_id in user_list:
		# try:
			archive_blacklisted_mails(email_id)
		# except Exception as e:
		# 	print 'blacklist background process crashed for ' + email_id + ' Exception : {' + str(e) + '}'
	return
while True:
	# try:
		archive_blacklist_for_all_users()
	# except Exception as e:
		# print 'blacklist background process crashed' + ' Exception : {' + str(e) + '}'
	# time.sleep(60)
