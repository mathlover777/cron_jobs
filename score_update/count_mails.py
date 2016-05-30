import nylas_helper
import token_store

source = "planck"
source_2 = "nylas"
use_psync = True

digest_sync = False
digest_client_email = 'eva@plancklabs.com'

def count_contact_wise_mails(email_id):
	token = token_store.get_token(email_id, source)
	if(token == ""):
		token = token_store.get_token(email_id, source_2)
		use_psync = False
	nylas_helper.count_contact_wise_mails(email_id, token, use_psync)

def count_contact_wise_mails_for_all_users():
	# user_list = token_store.get_email_prio_users()
	user_list = ['kumar.sachin52@gmail.com']
	print user_list
	for email_id in user_list:
		try:
			count_contact_wise_mails(email_id)
		except Exception as e:
			print 'Daily digest crashed {' + str(e) + '}'


while True:
	try:
		count_contact_wise_mails_for_all_users()	
		sleep(300)
	except Exception as e:
		print 'count_mails crashed' + ' Exception : {' + str(e) + '}'
		sleep(60)

	
