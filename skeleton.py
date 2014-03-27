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

# Keeping track of data
import pickle
import os.path

# Email Connection
import imaplib
import email

# Work with other scripts
import timex

# Debugging
import pdb

# Global variables for authentication
seen_emails = []
time_vectors = []
output_log  = []

# Credentials to log into Gmail/GCal API
client = gdata.calendar.client.CalendarClient(source='Where\'s A-wheres-a-v1')  # Dummy Google API Key
mail = imaplib.IMAP4_SSL('imap.gmail.com')
username = 'utcaldummy'
password = 'utcaldummy123'


# Authenticate for the calendar and email to be able to access the user's
# email and access the calendarb
def create_connection():
    # Connect to the calendar
    client.ClientLogin(username, password, client.source)

    mail.login(username+'@gmail.com', password)
    mail.list()
    mail.select("INBOX")

    print 'Successfully connected to email and calendar!'


def load_variables():
    global seen_emails, time_vectors, output_log

    # Loads data if it already exists, creates pickle file otherwise
    def load(fileName, data):
        # If the file doesn't exists, make a new file for it
        if not os.path.isfile(fileName):
            with open(fileName, 'wb') as f:
                pickle.dump(data, f)

        # Return the data from the file
        with open(fileName,'rb') as f:
                return pickle.load(f)

    time_vectors = load("time_vectors.p", time_vectors)
    seen_emails  = load("seen_emails.p", seen_emails)
    output_log   = load("output_log.p", output_log)

def log_updates():
    global seen_emails, time_vectors, output_log

    def save(file_name, data):
        with open(file_name, 'wb') as f:
            pickle.dump(data, f)

    save("time_vectors.p", time_vectors)
    save("seen_emails.p", seen_emails)
    save("output_log.p", output_log)

def time_object(year, month, day, hour, minute, second):
    month  = "%02d" % int(month)
    day    = "%02d" % int(day)
    hour   = "%02d" % int(hour)
    minute = "%02d" % int(minute)
    second = "%02d" % int(second)

    return '%s-%s-%sT%s:%s:%s-06:00' % (year, month, day, hour, minute, second)

def parse_email(email_body):

    days = get_possible_days(email) #two lists of ints representing days to schedule and the month
    times = get_possible_times(day)

    # days = get_possible_days(email)
    # possible_times = get_possible_times()

    # Create a list of days and times
    possible_times = combine_days_with_possible_times(days)
    free_times = filter_out_conflicts(possible_times)

    # TODO: Rank the times

    return free_times

    def get_possible_days(email_body):
        return parse(email_body)

    def get_possible_times(possible_days):
        possible_times = []         # Stores tuples (start_time, end_time)
        duration = 60               # Currently duration of event is an hour

        # Generate all the possible times for all the possible days
        for possible_day in possible_days:
            day_start_str = time_object(possible_day[0], possible_day[1],
                                        possible_day[2], 0, 0, 0)
            day_end_str   = time_object(possible_day[0], possible_day[1],
                                        possible_day[2], 23, 59, 59)

            day_start_time = parser.parse(day_start_str)
            day_end_time   = parser.parse(day_end_str)

            while(day_start_time < day_end_time):
                new_possible_time = (day_start_time, day_start_time + datetime.timedelta(minutes=duration))
                possible_times.append(new_possible_time)
                day_start_time += datetime.timedelta(minutes=30)

            # Faster to filter out conflicts on per day basis than at the end
            for e_conflict in findConflicts(day_start_str, day_end_str):
                conflict_start = parser.parse(e_conflict.when[0].start)
                conflict_end   = parser.parse(e_conflict.when[0].end)

                # Filter out the bad times for that event
                possible_times = filter(lambda time: (time[1] <= conflict_start or conflict_end <= time[0]), possible_times)

        return possible_times

    def findConflicts(start_date, end_date):
        # Construct the calendar query
        query = gdata.calendar.client.CalendarEventQuery()
        query.start_min = start_date
        query.start_max = end_date

        feed = client.GetCalendarEventFeed(q=query) # Execute the query

        return feed.entry

    # Acutal function logic
    days = get_possible_days(email)
    possible_times = get_possible_times(days)

    # Create a list of days and times
    possible_times = combine_days_with_possible_times(days)
    free_times = filter_out_conflicts(possible_times)

    # TODO: Rank the times

    return free_times



def prompt_user(times):
    # Print out the possible times, with an associated index
    print 'Please select a start time for your event: '
    for i, possible_time in enumerate(possible_times):
        print '%02d :: %s - %s' % (i, possible_time[0].strftime("%a %m-%d %I:%M%p"), possible_time[1].strftime("%I:%M%p"))


    print               # Prompt user for a selection
    user_selection = int(input("Please select the most optimal time: "))
    return user_selection

def check_for_new_emails_and_prompt():
    status, data = mail.search(None, 'ALL')     # Grab all the emails
    email_ids = data[0].split()                 # and their email ids

    # Scan the list from new to old.
    for i in xrange(len(email_ids) - 1, 0, -1):
        email_id = email_ids[i]             # Fetch that email
        result, data = mail.fetch(email_id, "(RFC822)")

        raw_email = data[0][1]              # Turn it into an email object
        email_obj = email.message_from_string(raw_email)

        # Payload can either be a list (HTML & Reg Version), or just Reg
        if isinstance(email_obj._payload, list):
            body = email_obj._payload[0]._payload
        else:
            body = email_obj._payload

        subj   = email_obj["Subject"]
        sender = email_obj["From"]

        # Seen this email before? -> Seen all older. Terminate
        if (subj, body) in seen_emails:
            return

        # If you haven't seen this before handle accordingly
        process_email(subj, body, sender)

def process_email(subject, body, sender):
    print "Processing Email:"
    print "\nSubject: %s" % subject
    print "From: %s" % sender
    print "%s" % body

    possible_times = parse_email(body)
    user_selection = prompt_user(possible_times)

    # TODO: Append that body to the appropriate time vector
    # TODO: Log the email accordingly

    seen_emails.append(subject, body)

def main():
    create_connection()
    load_variables()
    check_for_new_emails_and_prompt()

if __name__ == '__main__':
    main()
