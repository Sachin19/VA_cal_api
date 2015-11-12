from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from nylas import APIClient
from va_utility import VA
from access_db import *
import requests
import redis
import datetime
import json

APP_ID = 'b332w8abw872n3vv0nhn6vgno'
APP_SECRET = '745sx53h64dtur6svq26f8c7b'
passw = "planck_test"
va = VA('credentials')

def log_out(request):
	request.session.flush()
	return HttpResponseRedirect(reverse('index', args=()))

def make_event(request):
	try:
		thread_id = request.GET['thread']
		event_details = eval(get_from_database(va.credentials['namespace'],thread_id,'thread'))
		if(event_details is not None):
			if(event_details.has_key('event_done')):
				return render(request, 'make_event.html', {'done':True})
		va.make_meeting_event(event_details['sender'], event_details['participants'], long(request.GET['starttime']), long(request.GET['endtime']), event_details['location'])
		return render(request, 'make_event.html', {'done':False})
	except E:
		return HttpResponse("An error has occured. Please try again later")

def index(request):
	return HttpResponse("Welcome to Planck Labs.")
	
def view_availability(request):
	st = long(request.GET.get('start_time'))
	startdatetime = datetime.datetime.fromtimestamp(st)
	email = request.GET.get('email')
	duration = int(request.GET.get('timeframe'))

	occupied_slots = get_slots(email, startdatetime.strftime("%d-%m-%Y"), duration)['intervals']

	for interval in occupied_slots:
		print datetime.datetime.fromtimestamp(interval[0]), datetime.datetime.fromtimestamp(interval[1])

	freeslots = va.invert_time_ranges(occupied_slots) 
	email=request.GET['email']
	print email

	startdate = startdatetime.date()	
	days = []
	for i in range(duration):
		days.append(startdate)
		startdate+=datetime.timedelta(days=1)

	timepref, locpref, nomeetpref = get_from_database(va.credentials['namespace'], email, 'pref')
	print 'tp',timepref
	if(timepref is None or timepref==''):
		timepref=[(datetime.time(8,0), datetime.time(19,0))]
	else:
		timepref=va.parse_time_preferences(timepref)

	preferred_slots = va.expand_recurrence(timepref, days)

	available_slots = va.intersect_time_ranges(preferred_slots,freeslots)
	for interval in available_slots:
		print datetime.datetime.fromtimestamp(interval[0]), datetime.datetime.fromtimestamp(interval[1])
	return render(request, 'weeklyav.html', {'done':False})


def get_slots(email, st, duration):
	result = {}
	try:
		starttime = datetime.datetime.strptime(st,"%d-%m-%Y").date()
	except Exception as e2:
		result['success']='false'
		result['msg']='start_time is in wrong format'
		return result

	if(email is None and starttime is None and duration is None):
		result['success']='false'
		result['msg']='Date provided is in wrong format'
	else:
		occupied_slots = va.get_occupied_timeslots(email, starttime, duration)
		result['success']='true'
		result['intervals']=occupied_slots
		print occupied_slots
		return result
		# print email, starttime, duration

@csrf_exempt
def get_availability(request):
	'''
		This function returns the available slots in the calendar of a user whose email is provided.
		If the email does not exist in the redis database, an Error message is shown
	'''
	try:
		email = request.POST.get('email')
		st = request.POST.get('start_time')
		duration = int(request.POST.get('timeframe'))
		return HttpResponse(json.dumps(get_slots(email, st, duration), indent=4))
	except Exception as e:
	 	result['success']='false'
		result['msg']='Fatal error occured, Please contact the administrator'
		return result
	



	
