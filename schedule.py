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

# Email Connection
import imaplib
import email

# Global variables for authentication
client = gdata.calendar.client.CalendarClient(source='Where\'s A-wheres-a-v1')  # Dummy Google API Key
mail = imaplib.IMAP4_SSL('imap.gmail.com')
username = 'utcaldummy'
password = 'utcaldummy123'

# Authenticate for the calendar and email to be able to access the user's
# email and access the calendarb
def create_connection():
    # Connect to the calendar
    client.ClientLogin(username, password, client.source)

    # Connect to email inbox
    mail.login(username+'@gmail.com', password)
    mail.list()
    mail.select("INBOX")        # Connect to the inbox

    print "Succesfully Connected to Calendar and Inbox! \n"

def set_up_calendars():
    # Figure out what calendar the user has
    feed = client.GetAllCalendarsFeed()
    # print feed.title.text

    # # Grab that user's calendars
    # for i, a_calendar in enumerate(feed.entry):
    #     print '\t%s. %s' % (i, a_calendar.title.text)

    # # Get calendar event's on a specific day/range
    # start_date = '2013-10-31'
    # end_date = '2013-11-29'

    # query = gdata.calendar.client.CalendarEventQuery()
    # query.start_min = start_date
    # query.start_max = end_date

    # # Documentation on calendar events can be found at the following:
    # # http://sourcecodebrowser.com/python-gdata/1.0.9/classgdata_1_1calendar_1_1_calendar_event_entry.html#a0ad621c0a499ab19727a136aa35d5ab7

    # print 'Grabbing events between %s -- %s' % (start_date, end_date)
    # feed = client.GetCalendarEventFeed(q=query)
    # for i, an_event in enumerate(feed.entry):
    #     print '\t%s. %s' % (i, an_event.title.text)
    #     print 'Begins at %s' % (str(an_event.when[0]))

# The loop that takes in an input and parses it and then executes the appropraite event
# Currently called 'initiate loop', needs a better name but should work for basic implementation
def initiate_loop():
    user_input = raw_input("Enter event title, event will automatically be made for right now: ")

    # Create the event. Currently using Google's quick add feature which handles the extensive
    # parsing for you. Information on how to use this can be found here:
    # https://developers.google.com/google-apps/calendar/v2/developers_guide_python#CreatingSingle
    event = gdata.calendar.data.CalendarEventEntry()
    event.content = atom.data.Content(text=user_input)
    event.quick_add = gdata.calendar.data.QuickAddProperty(value='true')

    # Send the request and receive the response
    new_event = client.InsertEvent(event)

def parse():
    # Parse is currently undefined by the different parameters that could be parsed for are:
    # - title, conent, where, start_time, end_time. These will then be passed in order to insert a single
    # event. RIght now there is currently no parse support for this.
    return

# Found here: https://developers.google.com/google-apps/calendar/v2/developers_guide_python#CreatingSingle
#
# Not currently used, but should be used once we better understand how to parse the information.
def InsertSingleEvent(calendar_client=client,
                                title=None,
                                content=None,
                                where=None,
                                start_time=None,
                                end_time=  None):
    event = gdata.calendar.data.CalendarEventEntry()
    event.title = atom.data.Title(text=title)
    event.content = atom.data.Content(text=content)
    event.where.append(gdata.calendar.data.CalendarWhere(value=where))

    if start_time is None:
      # Use current time for the start_time and have the event last 1 hour
      start_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
      end_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(time.time() + 3600))
    event.when.append(gdata.calendar.data.When(start=start_time, end=end_time))

    new_event = calendar_client.InsertEvent(event)

    print 'New single event inserted: %s' % (new_event.id.text,)
    print '\tEvent edit URL: %s' % (new_event.GetEditLink().href,)
    print '\tEvent HTML URL: %s' % (new_event.GetHtmlLink().href,)

    return new_event

def main():
    create_connection()
    set_up_calendars()
    initiate_loop()

if __name__ == "__main__":
    main()
