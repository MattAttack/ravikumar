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


# Authenticate for the calendar
client = gdata.calendar.client.CalendarClient(source='Where\'s A-wheres-a-v1')
client.ClientLogin('jaysdummy', 'jaysdummy123', client.source) 

# Figure out what calendars that user has
feed = client.GetAllCalendarsFeed()
print feed.title.text
