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

    # Load up each of the values needed
    time_vectors = load("time_vectors.p", time_vectors)
    #   seen emails
    #   log stuff

def parse_email(email_body):
    days = get_possible_days(email)
    times = get_possible_times(day)

    # Create a list of days and times
    possible_times = [] # [(day, time)]

    free_times = filter_out_conflicts(possible_times)

    return free_times # Already ranked

    # TODO: Jay
    def get_possible_days(email_body):
        # Return a list of the possible days
        pass

    # TODO: Matt
    def get_possible_times():
        # Generate all of the times and rank them
        pass

    # TODO: Matt
    def filter_out_conflicts(possible_times):
        # Filter out all of the times with conflicts
        pass

# TODO: Matt
def prompt_user(times):
    # Prompt the user for a time
    pass

# TODO: Matt
def log_updates():
    # Update read emails
    # Update time vectors
    # Update output_log
    pass

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
        if isinstance(em._payload, list):
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
        pdb.set_trace()

def process_email(subject, body, sender):

    pass

def main():
    create_connection()
    load_variables()
    check_for_new_emails_and_prompt()

if __name__ == '__main__':
    main()
