import nylas_helper
import token_store
import time

social_list = ["linkedin","facebook","plus.google","twitter","meetup","tumblr","instagram","flickr","youtube","snapchat","stumbleupon","orkut","goodreads"]

def tag_new_mails(email_id,white_list):
	token = token_store.get_token(email_id)
	nylas_helper.tag_recent_unread_mails(email_id,token,white_list,social_list)
	return

def tag_new_mails_for_all_users():
	user_list = token_store.get_email_prio_users()
	# user_list = ['sachinkumar1911@yahoo.com']
	white_list = token_store.get_white_list()
	print white_list
	print user_list
	for email_id in user_list:
		try:
			tag_new_mails(email_id,white_list)
		except Exception as e:
			print 'tagger crashed for ' + email_id + ' Exception : {' + str(e) + '}'
	return
while True:
	try:
		tag_new_mails_for_all_users()
	except Exception as e:
		print 'tagger crashed' + ' Exception : {' + str(e) + '}'
	time.sleep(60)
