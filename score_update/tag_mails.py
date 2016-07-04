import nylas_helper
import token_store
import time
import nylas

source = "planck"
source_2 = "nylas"
social_list = ["linkedin","facebook","plus.google","twitter","meetup","tumblr","instagram","flickr","youtube","snapchat","stumbleupon","orkut","goodreads"]

def tag_new_mails(email_id,white_list):
	token = token_store.get_token(email_id, source)
	use_psync = True
	if(token == ""):
		token = token_store.get_token(email_id, source_2)
		use_psync = False
	# print use_psync, token
	nylas_helper.set_psync(use_psync)
	nylas_helper.tag_recent_unread_mails(email_id,token,white_list,social_list, use_psync)
	return

def tag_new_mails_for_all_users():

	# user_list = token_store.get_email_prio_users()
	user_list = ['rajesh.x.kumar@gmail.com']
	white_list = token_store.get_white_list()
	# print white_list
	# print user_list
	for email_id in user_list:
		try:
			tag_new_mails(email_id,white_list)
		except Exception as e:
			try:
				if type(e) == nylas.client.errors.NotFoundError:
					if e.as_dict()['message'] == 'Account deleted':
						token_store.remove_user_from_prio(email_id)
						print "Removed "+email_id+". Showed 'Account deleted' error."
				else:
					print 'tagger crashed for ' + email_id + ' Exception : {' + str(e) + '}'
			except Exception as e2:
				print 'tagger deleter crashed for ' + email_id + ' Exception : {' + str(e2) + '}'
	return
while True:
	try:
		tag_new_mails_for_all_users()
	except Exception as e:
		print 'tagger crashed' + ' Exception : {' + str(e) + '}'
		time.sleep(60)
