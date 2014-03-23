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
    mail.select("INBOX") # connect to inbox.

    print 'Successfully connected to email and calendar!'

def load_variables():
    # TODO: Load previous data:
    #   - seen emails
    #   - time vectors
    #   - log stuff
    pass

# Returns the body of the user's most recent email
# TODO: Matt
def get_most_recent_emails():
    return []

def parse_email(email_body):
    days = get_possible_days(email)
    times = get_possible_times(day)

    # Create a list of days and times
    possible_times = [] # [(day, time)]

    free_times = filter_out_conflicts(possible_times)

    return free_timess # Already ranked

    # TODO: Jay
    def get_possible_days():
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

def main():
    create_connection()

    load_variables()                        # TODO: Both

    # Get all new emails
    new_emails = get_most_recent_emails()
    for email in new_emails:
        times = parse_email(email)
        user_selection = prompt_user(times)
        log_updates()

if __name__ == '__main__':
    main()
