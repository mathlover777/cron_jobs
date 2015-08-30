import time
import datetime
import json

def get_current_time_stamp():
	return int(time.time())

def get_old_time_stamp(days_before):
	yesterday = datetime.date.today() - datetime.timedelta(days_before)
	return yesterday.strftime("%s")

def get_old_time_stamp_by_minute(minute):
	return int((datetime.datetime.now() - datetime.timedelta(minutes = minute)).strftime("%s"))

def load_json(filename):
	with open(filename,'rb') as fp:
		return json.load(fp = fp)

def save_json(filename,data):
	with open(filename,'wb') as fp:
		json.dump(data,fp = fp,indent = 4)
	return

