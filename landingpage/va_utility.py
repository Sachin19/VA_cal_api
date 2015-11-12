from nylas import APIClient
from recurrent import RecurringEvent
from access_db import *
import datetime
import redis
import time
import re
import random
import string

key = 'planck_test'
infinity=2556037800

def randomstring(N):
	return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(N))

class VA:
	def __init__(self, credentialfile):
		fil = open(credentialfile,'r')
		credentials = {}
		for line in fil:
			terms = line.strip('\n').split('=')
			credentials[terms[0]] = terms[1]

		print "UPDATE: Credentials Loaded"
		self.credentials = credentials
		try:
			access_token = get_from_database(credentials['namespace'], credentials['email'], 'token')
			if(access_token is None):
				raise Exception
			self.client = APIClient(credentials['APP_ID'], credentials['APP_SECRET'], access_token)
			print "UPDATE: successfully logged into the VA account"
		except Exception as e:
			print "ERROR: The VA account is not registered. Exiting...",e
			sys.exit(-1)

		print "UPDATE: VA successfully loaded."

	def get_client(self):
		return self.client		

	def make_meeting_event(self, sender, participants, startdatetime, enddatetime, place, subject=""):
		cal_id = None
		sclient = APIClient(self.credentials['APP_ID'], self.credentials['APP_SECRET'], sender['token'])
		for cal in sclient.calendars:
			if(not cal['read_only']):
				cal_id = cal['id']

		if(cal_id is None):
			print "ERROR: No modifiable calender present in the user account. Cannot create event."

		else:
			participants_d = []
			for p in participants:
				participants_d.append({'email':p})
			events = sclient.events
			# startdatetime = datetime.datetime(year=date.year, month=date.month, day=date.day, hour=start_time.hour, minute=start_time.minute)
			# enddatetime = datetime.datetime(year=date.year, month=date.month, day=date.day, hour=end_time.hour, minute=end_time.minute)

			meeting = events.create(calendar_id=cal_id, participants=participants_d, when={'start_time':long(startdatetime), 'end_time':long(enddatetime)},location=place, title="Meeting" ,description="Meeting about '"+subject+"'")
			meeting.save(notify_participants=True)

			print "SUCCESS: a meeting has been setup"

	def get_timeslots(self, email, startdate, enddate):
		# print startdate, enddate
		atok = get_from_database(self.credentials['namespace'], email, 'token')
		if(atok is None):
			return None
		tranges = {}
		pclient = APIClient(self.credentials['APP_ID'], self.credentials['APP_SECRET'], atok)
		calid = ""
		for cal in pclient.calendars:
			if(not cal['read_only'] or cal['name']=='Emailed events'):
				calid = cal['id']
				if(calid != ""):
					startafter = long(startdate.strftime("%s"))
					endbefore = long(enddate.strftime("%s"))
					events = pclient.events.where(calendar_id=calid, expand_recurring=True, starts_after=startafter, ends_before=endbefore)
					for event in events:
						if(event.has_key('when')):
							if(event['when'].has_key('start_time') and event['when'].has_key('end_time')):
								if(event.has_key('status')):
									if( event['status'] != 'confirmed'):
										continue
								st = long(event['when']['start_time'])
								et = long(event['when']['end_time'])
								tranges[(st, et)]=1
								
		time_ranges = tranges.keys()
		time_ranges.sort()
		return time_ranges

	def get_occupied_timeslots(self, email, startdate, duration):
		'''
			This function returns unavailable timeslots in the calendar of a user a given time duration

			parameters
			----------------------
			atok: access_token of the user in nylas
			startdate: of type datetime.date
			duration: int (number of days)
		'''
		enddate = startdate + datetime.timedelta(days=duration)
		return self.get_timeslots(email, startdate, enddate)

	def invert_time_ranges(self, time_ranges):
		print time_ranges
		lower = 0
		irange = []
		for i in range(len(time_ranges)):
			upper = time_ranges[i][0]
			if(upper > lower):
				irange.append((lower, upper))
			lower = time_ranges[i][1]

		upper = infinity
		if(upper > lower):
			irange.append((lower, upper))
		
		return irange

	def intersect_time_ranges(self, time_ranges_1, time_ranges_2):
		if(len(time_ranges_1) == 0 or len(time_ranges_2) == 0):
			return []

		current_1 = time_ranges_1[0]
		current_2 = time_ranges_2[0]
		intersection = []
		i1 = 0
		i2 = 0
		while(i1<len(time_ranges_1) and i2<len(time_ranges_2)):
			maxx = max(current_1[0], current_2[0])
			minn = min(current_1[1], current_2[1])

			if(maxx < minn):
				intersection.append((maxx, minn))
				current_1 = (minn, current_1[1])
				current_2 = (minn, current_2[1])

			elif(maxx == current_2[0] and minn == current_1[1]):
				i1+=1
				if(i1 < len(time_ranges_1)):
					current_1 = time_ranges_1[i1]

			elif(maxx == current_1[0] and minn == current_2[1]):
				i2+=1
				if(i2 < len(time_ranges_2)):
					current_2 = time_ranges_2[i2]

		return intersection


	def parse_time_preferences(self, time_ranges_string):
		timeranges = time_ranges_string.split(";")
		parsedranges = []
		dtparser = RecurringEvent()
		for timerange in timeranges:
			[lower, upper] = timerange.split("-")
			lowertime = dtparser.parse(lower)
			uppertime = dtparser.parse(upper)
			parsedranges.append((lowertime.time(), uppertime.time()))

		return sorted(parsedranges, key=lambda x:x[0])

	def expand_recurrence(self, time_ranges, dates):
		expanded_tr = []
		for date in dates:
			for tr in time_ranges:
				expanded_tr.append((long(datetime.datetime.combine(date, tr[0]).strftime("%s")), long(datetime.datetime.combine(date, tr[1]).strftime("%s"))))
		return sorted(expanded_tr)

		