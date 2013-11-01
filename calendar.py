#!/usr/bin/python 
try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata.calendar.data
import gdata.calendar.client
import gdata.acl.data
import atom.data
import time

#global variables used for authentication
client = gdata.calendar.client.CalendarClient(source='Where\'s A-wheres-a-v1')
username = 'utcaldummy'
password = 'utcaldummy123'

# Authenticate for the calendar
def createConnection():
	client.ClientLogin(username, password, client.source) 

def setUpCalendars():
	# Figure out what calendars that user has
	feed = client.GetAllCalendarsFeed()
	print feed.title.text

	# Grab that user's calendars
	for i, a_calendar in enumerate(feed.entry):
  		print '\t%s. %s' % (i, a_calendar.title.text)

	# Get calendar event's on a specific day/range
	start_date = '2013-10-31'
	end_date = '2013-11-29'

	query = gdata.calendar.client.CalendarEventQuery()
	query.start_min = start_date
	query.start_max = end_date

	print 'Grabbing events between %s -- %s' % (start_date, end_date)
	feed = client.GetCalendarEventFeed(q=query)
	for i, an_event in enumerate(feed.entry):
		print '\t%s. %s' % (i, an_event.title.text)


createConnection()
setUpCalendars()