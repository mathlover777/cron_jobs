import nylas_helper
import token_store
import time

def tag_new_mails(email_id):
	token = token_store.get_token(email_id)
	nylas_helper.tag_recent_unread_mails(email_id,token)
	return

def tag_new_mails_for_all_users():
	user_list = token_store.get_email_prio_users()
	print user_list
	# user_list = ['souravmathlover@gmail.com']
	for email_id in user_list:
		tag_new_mails(email_id)
	return
while True:
	try:
		tag_new_mails_for_all_users()
	except:
		print 'crashed'
	time.sleep(300)
