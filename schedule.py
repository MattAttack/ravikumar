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

# Work with other scripts
import pull_email

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

#retrieves email
def check_email():
    print pull_email.getEmail()

#NLP to detect events from email
def parse_email(email_body):
    # Parse is currently undefined by the different parameters that could be parsed for are:
    # - title, conent, where, start_time, end_time. These will then be passed in order to insert a single
    # event. RIght now there is currently no parse support for this.
    return

# check_availability comments..
def check_availability(start_date, end_date):
    query = gdata.calendar.client.CalendarEventQuery()
    query.start_min = start_date
    query.start_max = end_date

    print 'Grabbing events between %s -- %s' % (start_date, end_date)
    feed = client.GetCalendarEventFeed(q=query)
    for i, an_event in enumerate(feed.entry):
        print '\t%s. %s' % (i, an_event.title.text)
        print 'Begins at %s' % (str(an_event.when[0]))


# The loop that takes in an input and parses it and then executes the appropraite event
# Currently called 'initiate loop', needs a better name but should work for basic implementation
def manual_input():
    user_input = raw_input("Enter event title, event will automatically be made for right now: ")

    # Create the event. Currently using Google's quick add feature which handles the extensive
    # parsing for you. Information on how to use this can be found here:
    # https://developers.google.com/google-apps/calendar/v2/developers_guide_python#CreatingSingle
    event = gdata.calendar.data.CalendarEventEntry()
    event.content = atom.data.Content(text=user_input)
    event.quick_add = gdata.calendar.data.QuickAddProperty(value='true')

    # Send the request and receive the response
    new_event = client.InsertEvent(event)



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
    check_email()

    # parse those emails

    check_availability('2014-01-24', '2014-01-29')



if __name__ == "__main__":
    main()
