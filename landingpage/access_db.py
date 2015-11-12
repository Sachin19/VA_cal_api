import requests
def get_from_database(namespace, ID, key):
	if(key == 'token'):
		data = {'email_id':ID,'access_token':'planck_test'}
		r = requests.post("http://token-store-dev.elasticbeanstalk.com/server/get_token", data=data)
		rjson = r.json()
		# print rjson
		if(rjson['success'] == 'true'):
			return rjson['token']
	elif(key == "pref"):
		data = {'email_id':ID, 'namespace':namespace}
		r = requests.post("http://token-store-dev.elasticbeanstalk.com/server/get_preferences", data=data)
		rjson = r.json()
		return rjson['time_range'], rjson['locations'], rjson['no_meet_days']
	elif(key=='thread'):
		data = {'thread_id':ID}
		r = requests.post("http://token-store-dev.elasticbeanstalk.com/server/get_thread", data=data)
		rjson = r.json()
		if(rjson['success'] == 'true'):
			return rjson['event_details']
	return None

def save_to_database(namespace, ID, key, event_details):
	if(key == 'thread'):
		data = {'thread_id':ID, 'event_details':event_details}
		r = requests.post("http://token-store-dev.elasticbeanstalk.com/server/save_thread", data=data)
		rjson = r.json()
		if(rjson['success'] == 'true'):
			return True
		else:
			return False