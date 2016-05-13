import token_store
import nylas
import nylas_helper
import requests

source = "planck"
source_2 = "nylas"
psync_url = 'https://sync-dev.planckapi.com'

remove_label = ['new_contact','read_later_by_user','read_now_by_user', 'Read Now']
def remove_useless_labels(email_id):
	try:
		token = token_store.get_token(email_id, source)
		if(token == ""):
			token = token_store.get_token(email_id, source_2)
			use_psync = False
		# print use_psync, token
		nylas_helper.set_psync(use_psync)
		ns = nylas_helper.get_nylas_client(token)

		if use_psync:
			sync_url = psync_url
		else:
			sync_url = "https://api.nylas.com"
		
		if nylas_helper.use_labels(ns):
			for label in remove_label:
				lid = nylas_helper.get_id(ns, label)
				if lid is None:
					continue
				url = sync_url+"/labels/" + lid
				response = requests.delete(url, auth=(token, ""))
				print label,":",response
		else:
			for label in remove_label:
				lid = nylas_helper.get_folder_id(ns, label)
				if lid is None:
					continue
				url = sync_url+"/folders/" + lid
				response = requests.delete(url, auth=(token, ""))
				print label,":",response
	except Exception as e:
		print "Account doesn't exist"
	return


if __name__ == '__main__':
	user_list = token_store.get_email_prio_users()
	# user_list = ['kumar.sachin52@gmail.com']
	for email in user_list:
		print email
		remove_useless_labels(email)

