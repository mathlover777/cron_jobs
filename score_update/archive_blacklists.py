import nylas_helper
import token_store
import time

def archive_blacklisted_mails(email_id):
	token = token_store.get_token(email_id)
	nylas_helper.archive_old_blacklist_mails(email_id,token)
	return

def archive_blacklist_for_all_users():
	user_list = token_store.get_email_prio_users()
	# user_list = ['kumar.sachin52@gmail.com']
	print user_list
	for email_id in user_list:
		try:
			archive_blacklisted_mails(email_id)
		except Exception as e:
			print 'blacklist background process crashed for ' + email_id + ' Exception : {' + str(e) + '}'
	return
while True:
	try:
		archive_blacklist_for_all_users()
	except Exception as e:
		print 'blacklist background process crashed' + ' Exception : {' + str(e) + '}'
	time.sleep(60)
