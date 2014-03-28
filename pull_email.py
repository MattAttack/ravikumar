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

import pdb

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

	print 'Successfully connected to email and calendar!'


#Returns the body of the most recent email
def accessEmail():
	status, data = mail.search(None, 'ALL')
	ids = data[0] # data is a list.
	id_list = ids.split() # ids is a space separated string
	latest_email_id = id_list[-1] # get the latest
	result, data = mail.fetch(latest_email_id, "(RFC822)") # fetch the email body (RFC822) for the given ID


	raw_email = data[0][1] #this variable is an "email" object
	em = email.message_from_string(raw_email)

	if isinstance(em._payload, list):
		body = em._payload[0]._payload
	else:
		body = em._payload

	return body


def getEmail():
	createConnection()
	return accessEmail()


