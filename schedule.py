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
import datetime
from dateutil import parser

from time import gmtime, strftime

# Email Connection
import imaplib
import email

# Work with other scripts
import pull_email
import timex

# Debugging
import pdb

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
    email_text = pull_email.getEmail()
    print "Email text: \n" + email_text
    return email_text

#NLP to detect events from email
def parse_email(email_body):
    # the desired time format is: %Y-%m-%DT%H:%M:%S

    #t is an array of relative time objects, time objects, day_objects, month objects, and year objects detected in text
    t = timex.parse(email_body)

    def findYear(t):
        print "Year: " + str(t[0])

    def findMonth(t):
        print "Month: "+ str(t[1])

    def findDay(t):
        print "Day: "+ str(t[2])

    def findHour(t):
        print "Hour: " +str(t[3])

    def findMinute(t):
        print "Minute: "+ str(t[4])

    def findSecond(t):
        print "Second: " + str(t[5])

    print "Parsed entities: Y:%s M:%s D:%s H:%s M:%s S:%s" % (t[0], t[1], t[2], t[3], t[4], t[5])
    return t




# check_availability comments..
def check_availability(start_date, end_date):
    query = gdata.calendar.client.CalendarEventQuery()
    query.start_min = start_date
    query.start_max = end_date

    print 'Grabbing events between %s -- %s' % (start_date, end_date)
    feed = client.GetCalendarEventFeed(q=query)
    # for i, an_event in enumerate(feed.entry):
    #     print '\t%s. %s' % (i, an_event.title.text)
    #     print 'Begins at %s' % (str(an_event.when[0]))


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


# Check for calendar conflicts.
def findConflicts(start_date, end_date):
    # Construct the calendar query
    query = gdata.calendar.client.CalendarEventQuery()
    query.start_min = start_date
    query.start_max = end_date

    print
    print 'Grabbing events between %s -- %s' % (start_date, end_date)
    feed = client.GetCalendarEventFeed(q=query)
    for i, an_event in enumerate(feed.entry):   # Go over the calendar and pring out the events
        print '\t%s. %s' % (i, an_event.title.text)

    # TODO: Modify to return the events if needed
    print

    return feed.entry


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
    print start_time, end_time
    new_event = calendar_client.InsertEvent(event)
    print 'New single event inserted: %s' % (new_event.id.text,)
    print '\tEvent edit URL: %s' % (new_event.GetEditLink().href,)
    print '\tEvent HTML URL: %s' % (new_event.GetHtmlLink().href,)
    return new_event

# Takes the entities and constructs them appropriately in the format
# google's API accepts and likes
def time_object(year, month, day, hour, minute, second):
    month = "%02d" % int(month)
    day = "%02d" % int(day)
    hour = "%02d" % int(hour)
    minute = "%02d" % int(minute)
    second = "%02d" % int(second)

    return '%s-%s-%sT%s:%s:%s-06:00' % (year, month, day, hour, minute, second)

def prompt_user_for_time(parsed, duration):
    day_start_str = time_object(parsed[0][0], parsed[1][0], parsed[2][0], 0, 0, 0)
    day_end_str   = time_object(parsed[0][0], parsed[1][0], parsed[2][0], 23, 59, 59)
    day_start_time = parser.parse(day_start_str)
    day_end_time = parser.parse(day_end_str)

    possible_times = []             # Generate a list of all the possible times that day
    while (day_start_time < day_end_time):
        possible_time = (day_start_time, day_start_time + datetime.timedelta(minutes=duration))   # Duration will be an hour
        possible_times.append(possible_time)
        day_start_time = day_start_time + datetime.timedelta(minutes=30)

    # Filter out the times that are not valid
    for e_conflict in findConflicts(day_start_str, day_end_str):
        conflict_start = parser.parse(e_conflict.when[0].start)
        conflict_end   = parser.parse(e_conflict.when[0].end)

        possible_times = filter(lambda time: (time[1] <= conflict_start or conflict_end <= time[0]), possible_times)

    # Print out the possible times, with an associated index
    print 'Please select a start time for your event: '
    for i, possible_time in enumerate(possible_times):
        print '%02d :: %s - %s' % (i, possible_time[0].strftime("%a %m-%d %I:%M%p"), possible_time[1].strftime("%I:%M%p"))


    print               # Prompt user for a selection
    user_selection = int(input("Please select the most optimal time: "))
    print 'The user selected the following time: %s' % possible_times[user_selection][0]
    return possible_times[user_selection]


def main():
    create_connection()                 # need to connect to calendar now
    email_body = check_email()
    parsed = parse_email(email_body)

    # Prompt the user to schedule an event
    should_schedule = raw_input("Would you like to schedule an event? ")
    if (should_schedule[0] == 'y' or should_schedule[0] == 'Y'):
        event_name = raw_input('Name of the event: ')       # The event needs some name
        event_duration = int(raw_input('Duration of the event (minutes): '))

        print "Scheduling an event now.."
        if len(parsed[3]) == 1:
            possible_time = prompt_user_for_time(parsed, event_duration)
            pdb.set_trace()
            InsertSingleEvent(client,
                              event_name,
                              None,
                              None,
                              possible_time[0].strftime("%Y-%m-%dT%H:%M:%S") + "-06:00", # This is hacky. %:z gives me what I want
                              possible_time[1].strftime("%Y-%m-%dT%H:%M:%S") + "-06:00"  # but I was unable to get it to work
                              )
        else:
            start_time = time_object(parsed[0][0], parsed[1][0], parsed[2][0], parsed[3][0], parsed[4][0], parsed[5][0])
            pdb.set_trace()
            end_time = time_object(parsed[0][0], parsed[1][0], parsed[2][0], str(int(parsed[3][0]) + 1), parsed[4][0], parsed[5][0])
            InsertSingleEvent(client, event_name, None, None, start_time, end_time)

if __name__ == "__main__":
    main()
