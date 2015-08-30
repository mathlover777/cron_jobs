import nylas_helper
import token_store
import time

def get_score_list_for_user(email_id):
	token = token_store.get_token(email_id)
	# print email_id
	# print token
	score_list = nylas_helper.get_recent_contact_score(email_id,token)
	# print score_list
	return score_list


def update_score_list_for_user(email_id,contact_score_json):
	token_store.update_contact_score(email_id,contact_score_json)

def update_scores():
	user_list = token_store.get_email_prio_users()
	# print user_list
	for email_id in user_list:
		try:
			contact_score_json = get_score_list_for_user(email_id)
			update_score_list_for_user(email_id,contact_score_json)
		except:
			print 'update crashed for user ' + email_id
	return


# need to run this periodically
# update_scores()

while True:
	try:
		update_scores()
	except:
		print 'update crashed !'
	time.sleep(5000)
