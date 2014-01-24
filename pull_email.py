#!/usr/bin/python
try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata.calendar.data
import gdata.calendar.client
import gdata.acl.data
import email

# Email Connection
import imaplib

# Notes: (Add notes here as you encounter things):
# 	- Google's Calendar API interacts with dates in RFC 3339 format
#	- Calendar API Concepts and Use Cases: https://developers.google.com/google-apps/calendar/concepts


# Global variables for authenication
# TODO: Consider having these passed in our functions
client = gdata.calendar.client.CalendarClient(source='Where\'s A-wheres-a-v1')
mail = imaplib.IMAP4_SSL('imap.gmail.com')
username = 'utcaldummy'
password = 'utcaldummy123'

# Authenticate for the calendar and email
def createConnection():
	# connect to calendar
	client.ClientLogin(username, password, client.source)
	# connect to email inbox
	mail.login(username+'@gmail.com', password)
	mail.list()
	mail.select("INBOX") # connect to inbox.
	print "Succesfully Connected to Calendar and Inbox! \n"

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

	# Documentation on calendar events can be found at the following:
	# http://sourcecodebrowser.com/python-gdata/1.0.9/classgdata_1_1calendar_1_1_calendar_event_entry.html#a0ad621c0a499ab19727a136aa35d5ab7

	print 'Grabbing events between %s -- %s' % (start_date, end_date)
	feed = client.GetCalendarEventFeed(q=query)
	for i, an_event in enumerate(feed.entry):
		print '\t%s. %s' % (i, an_event.title.text)
		print 'Begins at %s' % (str(an_event.when[0]))

#Returns the body of the most recent email
def accessEmail():
	status, data = mail.search(None, 'ALL')
	ids = data[0] # data is a list.
	id_list = ids.split() # ids is a space separated string
	latest_email_id = id_list[-1] # get the latest
	result, data = mail.fetch(latest_email_id, "(RFC822)") # fetch the email body (RFC822) for the given ID
	raw_email = data[0][1] #this variable is an "email" object

	#hack to find the text quickly, had trouble parsing MIME object
	msg = raw_email.split("--")
	return msg[2]

def getEmail():
	createConnection()
	setUpCalendars()
	return accessEmail()
	

