import nylas_helper
import token_store
import time
import datetime
import pytz

source = "planck"
source_2 = "nylas"
use_psync = True

digest_sync = False
digest_client_email = 'eva@plancklabs.com'

def send_daily_digest(email_id, digestclient):
	token = token_store.get_token(email_id, source)
	if(token == ""):
		token = token_store.get_token(email_id, source_2)
		use_psync = False
	# print use_psync, token
	nylas_helper.send_daily_digest(email_id, token, use_psync, digestclient)

def send_daily_digest_to_all_users(nowtime):
	digest_psync = True
	digest_token = token_store.get_token(digest_client_email, source)
	if(digest_token == ""):
		digest_token = token_store.get_token(digest_client_email, source_2)
		digest_psync = False
	
	digestclient = nylas_helper.get_nylas_client_(digest_token, digest_psync)

	# user_list = token_store.get_email_prio_users()
	user_list = ['kumar.sachin52@gmail.com', 'rajesh.x.kumar@gmail.com']
	# print user_list
	digest_times = token_store.get_daily_digest_time(user_list)
	timezones = token_store.get_timezones(user_list)
	for i in range(len(user_list)):
		try:
			user = user_list[i]
			digest_time = digest_times[i]
			timezone = timezones[i]
			tzobj = pytz.timezone(timezone)
			tztime = nowtime.astimezone(tzobj).time()

			dt = digest_time.hour*60+digest_time.minute
			tzt = tztime.hour*60+tztime.minute
			# print tztime, digest_time
			if dt-tzt <= 30: #if the current time and time of daily digest are 30 minutes apart, then send the daily digest
				print "Preparing to send daily digest to",user
				send_daily_digest(user, digestclient)
				print 'Sent the digest to',user
			else:
				print "Not the time",user

		except Exception as e:
			print 'Daily digest crashed {' + str(e) + '}'


while True:
	try:
		tzobj = pytz.timezone("UTC")
		nowtime = tzobj.localize(datetime.datetime.utcnow())
		print nowtime
		send_daily_digest_to_all_users(nowtime)
		time.sleep(1800)
	except Exception as e:
		print 'daily digest crashed' + ' Exception : {' + str(e) + '}'

	
