import nylas_helper
import token_store
import time

source = "planck"
source_2 = "nylas"
use_psync = True

def get_score_list_for_user(email_id):
	token = token_store.get_token(email_id, source)
	use_psync = True
	if(token == ""):
		token = token_store.get_token(email_id, source_2)
		use_psync = False
	# nylas_helper.set_psync(use_psync)
	score_list = nylas_helper.get_recent_contact_score(email_id,token, use_psync)
	return score_list


def update_score_list_for_user(email_id,contact_score_json):
	token_store.update_contact_score(email_id,contact_score_json)

def update_scores():
	user_list = token_store.get_email_prio_users()
	# user_list = ['raj@plancklabs.com']
	for email_id in user_list:
		try:
			contact_score_json = get_score_list_for_user(email_id)
			# print contact_score_json
			update_score_list_for_user(email_id,contact_score_json)
			print "INFO: Updated score for",email_id
		except Exception as e:
			print 'update crashed for user ' + email_id + ' Exception : {' + str(e) + '}'
	return


# need to run this periodically
# update_scores()

while True:
	try:
		update_scores()
		# quit()
	except Exception as e:
		print 'update crashed !' + ' Exception : {' + str(e) + '}'
	time.sleep(5000)
