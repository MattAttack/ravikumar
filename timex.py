# Code for tagging temporal expressions in text
# For details of the TIMEX format, see http://timex2.mitre.org/

import re
import string
import os
import sys
from time import gmtime, strftime
import pdb
from datetime import *
# Requires eGenix.com mx Base Distribution
# http://www.egenix.com/products/python/mxBase/
try:
    from mx.DateTime import *
except ImportError:
    print """
Requires eGenix.com mx Base Distribution
http://www.egenix.com/products/python/mxBase/"""



# Predefined strings.
#
# Modified to have a lookahead and lookbehind. Lookahead is (?=\W|$) and lookbehind is (?<!\w).

#not being used
# exp1 = "((?<!\w)before(?=\W|$)|(?<!\w)after(?=\W|$)|(?<!\w)earlier(?=\W|$)|(?<!\w)later(?=\W|$)|(?<!\w)ago(?=\W|$))"
# exp2 = "((?<!\w)this(?=\W|$)|(?<!\w)next(?=\W|$)|(?<!\w)last(?=\W|$))"
# iso = "\d+[/-]\d+[/-]\d+ \d+:\d+:\d+\.\d+"
# regxp1 = "((\d+(?=\W|$)|(?<!\w)(" + numbers + "[-\s]?)+) " + dmy + "s? " + exp1 + ")"
# regxp2 = "(" + exp2 + " (" + dmy + "(?=\W|$)|(?<!\w)" + week_day + "(?=\W|$)|(?<!\w)" + month + "))"
# dmy = "((?<!\w)year(?=\W|$)|(?<!\w)day(?=\W|$)|(?<!\w)week(?=\W|$)|(?<!\w)month(?=\W|$))"


#year
year = "((?<=\s)\d{4}(?=\W|$)|(?<!\w)^\d{4})"
reg1 = re.compile(year, re.IGNORECASE)

#month
month = "((?<!\w)january(?=\W|$)|(?<!\w)february(?=\W|$)|(?<!\w)march(?=\W|$)|(?<!\w)april(?=\W|$)|(?<!\w)may(?=\W|$)|(?<!\w)june(?=\W|$)|(?<!\w)july(?=\W|$)|(?<!\w)august(?=\W|$)|(?<!\w)september(?=\W|$)|(?<!\w)october(?=\W|$)|(?<!\w)november(?=\W|$)|(?<!\w)december(?=\W|$))"
reg2 = re.compile(month, re.IGNORECASE)

#day
day = "((?<!\w)monday(?=\W|$)|(?<!\w)tuesday(?=\W|$)|(?<!\w)wednesday(?=\W|$)|(?<!\w)thursday(?=\W|$)|(?<!\w)friday(?=\W|$)|(?<!\w)saturday(?=\W|$)|(?<!\w)sunday(?=\W|$))"
week_day = "((?<!\w)monday(?=\W|$)|(?<!\w)tuesday(?=\W|$)|(?<!\w)wednesday(?=\W|$)|(?<!\w)thursday(?=\W|$)|(?<!\w)friday(?=\W|$)|(?<!\w)saturday(?=\W|$)|(?<!\w)sunday(?=\W|$))"
reg3 = re.compile(day, re.IGNORECASE)

# Update: 2/28 - don't assign relative values with time, let probability/algorithm identify what this time means
rel_days = "((?<!\w)today(?=\W|$)|(?<!\w)tomorrow(?=\W|$)|(?<!\w)tonight(?=\W|$)|(?<!\w)tonite(?=\W|$))"
reg4 = re.compile(rel_days, re.IGNORECASE)

#hour
rel_hours = "((?<!\w)morning(?=\W|$)|(?<!\w)today(?=\W|$)|(?<!\w)tonight(?=\W|$)|(?<!\w)tonite(?=\W|$)|(?<!\w)noon(?=\W|$)|(?<!\w)night(?=\W|$))"
numbers = "(^a(?=\s)(?=\W|$)|(?<!\w)one(?=\W|$)|(?<!\w)two(?=\W|$)|(?<!\w)three(?=\W|$)|(?<!\w)four(?=\W|$)|(?<!\w)five(?=\W|$)|(?<!\w)six(?=\W|$)|(?<!\w)seven(?=\W|$)|(?<!\w)eight(?=\W|$)|(?<!\w)nine(?=\W|$)|(?<!\w)ten(?=\W|$)|(?<!\w)eleven(?=\W|$)|(?<!\w)twelve(?=\W|$))"
reg5 = re.compile(rel_hours, re.IGNORECASE)
reg6 = re.compile(numbers, re.IGNORECASE)

hashweekdays = {
        'mon': 0,
        'tue': 1,
        'wed': 2,
        'thu': 3,
        'fri': 4,
        'sat': 5,
        'sun': 6}


    # Hash function for months to simplify the grounding task.
    # [Jan..Dec] -> [1..12]
hashmonths = {
        'january': 1,
        'february': 2,
        'march': 3,
        'april': 4,
        'may': 5,
        'june': 6,
        'july': 7,
        'august': 8,
        'september': 9,
        'october': 10,
        'november': 11,
        'december': 12}

#Info about right now
currentYear = int(strftime("%Y"))
currentMonth = int(strftime("%m"))
currentDay = int(strftime("%d"))
currentDayofWeek = int(hashweekdays[strftime("%a").lower()])
currentHour = int(strftime("%H"))
currentMinute = int(strftime("%M"))
currentSecond = int(0)


relHours = {
    'today':currentHour,
    'noon':12,
    'tonight':20,
    'tonite':20,
    'morning':9,
    'night':20
}

relDays = {
    'today':currentDay,
    'tomorrow': int((date.today()+timedelta(days=1)).day),
    'tonight':currentDay,
    'tonite':currentDay
}

# array we will use to store date objects
days = [0]*7


#Keep track of all the temporal words we have found
timex_found = []

year_object = []
month_object = []
day_object = [] #returns a number which represents which date in a month, IE: 31 = march 31st
hour_object = []
minute_object = []
second_object = []

stopwordDictionary = {}
#loads stopwords and accesses them in real time
def loadStopwords():
    global stopwordDictionary
    ins = open ("stopwords.txt","r")
    for line in ins:
        stopwordDictionary[line.strip('\n')] = True
    ins.close()

#searches text for relevant fields, if no fields are found, current time field(s) are returned
def tag(text):

    def findYear(text):
        found = reg1.findall(text)
        for timex in found:
            year_object.append(str(timex))

        if not year_object:
            year_object.append(str(currentYear))

        return year_object

    def findMonth(text):
        found = reg2.findall(text)
        for timex in found:
            cTimex = hashmonths[timex.lower()]
            month_object.append(str(cTimex))
        if not month_object:
            month_object.append(str(currentMonth))

        return month_object

    #Always looks towards the future
    def findDay(text):
        found = reg3.findall(text)
        for timex in found:
            cTimex = hashweekdays[timex[0:3].lower()]
            cTimex = days[cTimex]
            day_object.append(str(cTimex))

        found = reg4.findall(text)
        for timex in found:
            cTimex = relDays[timex.lower()]
            day_object.append(str(cTimex))
        # if not day_object:
        #     day_object.append(str(currentDay))
        return day_object

    def findHour(text):
        found = reg6.findall(text)
        for timex in found:
            cTimex = hashnum(timex)
            hour_object.append(str(cTimex))
        #return empty array if no hour object found
        # if not hour_object:
        #     hour_object.append(str(currentHour))
        return hour_object

    def findMin(text):
        minute_object.append("00")
        return minute_object

    def findSecond(text):
        second_object.append("00")
        return second_object

    def findRelative(text):
        found = reg5.findall(text)
        return found

    #method which returns which month each day value corresponds to
    def findMonth_temp(days):
        months = []
        today = date.today()
        for day in days:
            if day < currentDay:
                append.months(int((today+timedelta(days=32)).month))
            else:
                months.append(int(today.month))
        return months
    #remove stopwords and return block of text
    def stripText(text):
        text = text.split()
        output = []
        for word in text:
            #remove all formatting from word
            word = ''.join(s for s in word if ord(s) >31 and ord(s) <126)
            if stopwordDictionary.get(str(word),False) != True:
                output.append(word)
        return output

    # return [findYear(text),findMonth(text),findDay(text),findHour(text),findMin(text),findSecond(text),findRelative(text)], stripText(text)
    #Changed to only return the day
    daysOut = findDay(text)
    monthsOut = findMonth_temp(daysOut)
    return daysOut, monthsOut

# Hash function for week days to simplify the grounding task.
# [Mon..Sun] -> [0..6]

def prepareHashMaps():
    today = date.today()
    t = timedelta(days=6)
    days[currentDayofWeek] = int( (today+timedelta(days=7)).day)

    #fill in the days earlier in the week
    for i in range(currentDayofWeek-1,-1,-1):
            days[i] = int((today+t).day)
            t = t - timedelta(days=1)

    #fill in the days later in the week
    t = timedelta(days=1)
    for i in range(currentDayofWeek+1,7,1):
        days[i] = int((today+t).day)
        t = t + timedelta(days=1)

# Hash number in words into the corresponding integer value
def hashnum(number):
    if re.match(r'one(?=\W|$)|(?<!\w)^a\b', number, re.IGNORECASE):
        return 1
    if re.match(r'two', number, re.IGNORECASE):
        return 2
    if re.match(r'three', number, re.IGNORECASE):
        return 3
    if re.match(r'four', number, re.IGNORECASE):
        return 4
    if re.match(r'five', number, re.IGNORECASE):
        return 5
    if re.match(r'six', number, re.IGNORECASE):
        return 6
    if re.match(r'seven', number, re.IGNORECASE):
        return 7
    if re.match(r'eight', number, re.IGNORECASE):
        return 8
    if re.match(r'nine', number, re.IGNORECASE):
        return 9
    if re.match(r'ten', number, re.IGNORECASE):
        return 10
    if re.match(r'eleven', number, re.IGNORECASE):
        return 11
    if re.match(r'twelve', number, re.IGNORECASE):
        return 12
    if re.match(r'thirteen', number, re.IGNORECASE):
        return 13
    if re.match(r'fourteen', number, re.IGNORECASE):
        return 14
    if re.match(r'fifteen', number, re.IGNORECASE):
        return 15
    if re.match(r'sixteen', number, re.IGNORECASE):
        return 16
    if re.match(r'seventeen', number, re.IGNORECASE):
        return 17
    if re.match(r'eighteen', number, re.IGNORECASE):
        return 18
    if re.match(r'nineteen', number, re.IGNORECASE):
        return 19
    if re.match(r'twenty', number, re.IGNORECASE):
        return 20
    if re.match(r'thirty', number, re.IGNORECASE):
        return 30
    if re.match(r'forty', number, re.IGNORECASE):
        return 40
    if re.match(r'fifty', number, re.IGNORECASE):
        return 50
    if re.match(r'sixty', number, re.IGNORECASE):
        return 60
    if re.match(r'seventy', number, re.IGNORECASE):
        return 70
    if re.match(r'eighty', number, re.IGNORECASE):
        return 80
    if re.match(r'ninety', number, re.IGNORECASE):
        return 90
    if re.match(r'hundred', number, re.IGNORECASE):
        return 100
    if re.match(r'thousand', number, re.IGNORECASE):
      return 1000

# Given a timex_tagged_text and a Date object set to base_date,
# returns timex_grounded_text
def ground(tagged_text, base_date):

    # Find all identified timex and put them into a list
    timex_regex = re.compile(r'<TIMEX2>.*?</TIMEX2>', re.DOTALL)
    timex_found = timex_regex.findall(tagged_text)
    timex_found = map(lambda timex:re.sub(r'</?TIMEX2.*?>', '', timex), \
                timex_found)

    # Calculate the new date accordingly
    for timex in timex_found:
        timex_val = 'UNKNOWN' # Default value

        timex_ori = timex   # Backup original timex for later substitution

        # If numbers are given in words, hash them into corresponding numbers.
        # eg. twenty five days ago --> 25 days ago
        if re.search(numbers, timex, re.IGNORECASE):
            split_timex = re.split(r'\s(?=days?(?=\W|$)|(?<!\w)months?(?=\W|$)|(?<!\w)years?(?=\W|$)|(?<!\w)weeks?)', \
                                                              timex, re.IGNORECASE)
            value = split_timex[0]
            unit = split_timex[1]
            num_list = map(lambda s:hashnum(s),re.findall(numbers + '+', \
                                          value, re.IGNORECASE))
            timex = `sum(num_list)` + ' ' + unit

        # If timex matches ISO format, remove 'time' and reorder 'date'
        if re.match(r'\d+[/-]\d+[/-]\d+ \d+:\d+:\d+\.\d+', timex):
            dmy = re.split(r'\s', timex)[0]
            dmy = re.split(r'/(?=\W|$)|(?<!\w)-', dmy)
            timex_val = str(dmy[2]) + '-' + str(dmy[1]) + '-' + str(dmy[0])

        # Specific dates
        elif re.match(r'\d{4}', timex):
            timex_val = str(timex)

        # Relative dates
        elif re.match(r'tonight(?=\W|$)|(?<!\w)tonite(?=\W|$)|(?<!\w)today', timex, re.IGNORECASE):
            timex_val = str(base_date)
        elif re.match(r'yesterday', timex, re.IGNORECASE):
            timex_val = str(base_date + RelativeDateTime(days=-1))
        elif re.match(r'tomorrow', timex, re.IGNORECASE):
            timex_val = str(base_date + RelativeDateTime(days=+1))

        # Weekday in the previous week.
        elif re.match(r'last ' + week_day, timex, re.IGNORECASE):
            day = hashweekdays[timex.split()[1]]
            timex_val = str(base_date + RelativeDateTime(weeks=-1, \
                            weekday=(day,0)))

        # Weekday in the current week.
        elif re.match(r'this ' + week_day, timex, re.IGNORECASE):
            day = hashweekdays[timex.split()[1]]
            timex_val = str(base_date + RelativeDateTime(weeks=0, \
                            weekday=(day,0)))

        # Weekday in the following week.
        elif re.match(r'next ' + week_day, timex, re.IGNORECASE):
            day = hashweekdays[timex.split()[1]]
            timex_val = str(base_date + RelativeDateTime(weeks=+1, \
                              weekday=(day,0)))

        # Last, this, next week.
        elif re.match(r'last week', timex, re.IGNORECASE):
            year = (base_date + RelativeDateTime(weeks=-1)).year

            # iso_week returns a triple (year, week, day) hence, retrieve
            # only week value.
            week = (base_date + RelativeDateTime(weeks=-1)).iso_week[1]
            timex_val = str(year) + 'W' + str(week)
        elif re.match(r'this week', timex, re.IGNORECASE):
            year = (base_date + RelativeDateTime(weeks=0)).year
            week = (base_date + RelativeDateTime(weeks=0)).iso_week[1]
            timex_val = str(year) + 'W' + str(week)
        elif re.match(r'next week', timex, re.IGNORECASE):
            year = (base_date + RelativeDateTime(weeks=+1)).year
            week = (base_date + RelativeDateTime(weeks=+1)).iso_week[1]
            timex_val = str(year) + 'W' + str(week)

        # Month in the previous year.
        elif re.match(r'last ' + month, timex, re.IGNORECASE):
            month = hashmonths[timex.split()[1]]
            timex_val = str(base_date.year - 1) + '-' + str(month)

        # Month in the current year.
        elif re.match(r'this ' + month, timex, re.IGNORECASE):
            month = hashmonths[timex.split()[1]]
            timex_val = str(base_date.year) + '-' + str(month)

        # Month in the following year.
        elif re.match(r'next ' + month, timex, re.IGNORECASE):
            month = hashmonths[timex.split()[1]]
            timex_val = str(base_date.year + 1) + '-' + str(month)
        elif re.match(r'last month', timex, re.IGNORECASE):

            # Handles the year boundary.
            if base_date.month == 1:
                timex_val = str(base_date.year - 1) + '-' + '12'
            else:
                timex_val = str(base_date.year) + '-' + str(base_date.month - 1)
        elif re.match(r'this month', timex, re.IGNORECASE):
                timex_val = str(base_date.year) + '-' + str(base_date.month)
        elif re.match(r'next month', timex, re.IGNORECASE):

            # Handles the year boundary.
            if base_date.month == 12:
                timex_val = str(base_date.year + 1) + '-' + '1'
            else:
                timex_val = str(base_date.year) + '-' + str(base_date.month + 1)
        elif re.match(r'last year', timex, re.IGNORECASE):
            timex_val = str(base_date.year - 1)
        elif re.match(r'this year', timex, re.IGNORECASE):
            timex_val = str(base_date.year)
        elif re.match(r'next year', timex, re.IGNORECASE):
            timex_val = str(base_date.year + 1)
        elif re.match(r'\d+ days? (ago(?=\W|$)|(?<!\w)earlier(?=\W|$)|(?<!\w)before)', timex, re.IGNORECASE):

            # Calculate the offset by taking '\d+' part from the timex.
            offset = int(re.split(r'\s', timex)[0])
            timex_val = str(base_date + RelativeDateTime(days=-offset))
        elif re.match(r'\d+ days? (later(?=\W|$)|(?<!\w)after)', timex, re.IGNORECASE):
            offset = int(re.split(r'\s', timex)[0])
            timex_val = str(base_date + RelativeDateTime(days=+offset))
        elif re.match(r'\d+ weeks? (ago(?=\W|$)|(?<!\w)earlier(?=\W|$)|(?<!\w)before)', timex, re.IGNORECASE):
            offset = int(re.split(r'\s', timex)[0])
            year = (base_date + RelativeDateTime(weeks=-offset)).year
            week = (base_date + \
                            RelativeDateTime(weeks=-offset)).iso_week[1]
            timex_val = str(year) + 'W' + str(week)
        elif re.match(r'\d+ weeks? (later(?=\W|$)|(?<!\w)after)', timex, re.IGNORECASE):
            offset = int(re.split(r'\s', timex)[0])
            year = (base_date + RelativeDateTime(weeks=+offset)).year
            week = (base_date + RelativeDateTime(weeks=+offset)).iso_week[1]
            timex_val = str(year) + 'W' + str(week)
        elif re.match(r'\d+ months? (ago(?=\W|$)|(?<!\w)earlier(?=\W|$)|(?<!\w)before)', timex, re.IGNORECASE):
            extra = 0
            offset = int(re.split(r'\s', timex)[0])

            # Checks if subtracting the remainder of (offset / 12) to the base month
            # crosses the year boundary.
            if (base_date.month - offset % 12) < 1:
                extra = 1

            # Calculate new values for the year and the month.
            year = str(base_date.year - offset // 12 - extra)
            month = str((base_date.month - offset % 12) % 12)

            # Fix for the special case.
            if month == '0':
                month = '12'
            timex_val = year + '-' + month
        elif re.match(r'\d+ months? (later(?=\W|$)|(?<!\w)after)', timex, re.IGNORECASE):
            extra = 0
            offset = int(re.split(r'\s', timex)[0])
            if (base_date.month + offset % 12) > 12:
                extra = 1
            year = str(base_date.year + offset // 12 + extra)
            month = str((base_date.month + offset % 12) % 12)
            if month == '0':
                month = '12'
            timex_val = year + '-' + month
        elif re.match(r'\d+ years? (ago(?=\W|$)|(?<!\w)earlier(?=\W|$)|(?<!\w)before)', timex, re.IGNORECASE):
            offset = int(re.split(r'\s', timex)[0])
            timex_val = str(base_date.year - offset)
        elif re.match(r'\d+ years? (later(?=\W|$)|(?<!\w)after)', timex, re.IGNORECASE):
            offset = int(re.split(r'\s', timex)[0])
            timex_val = str(base_date.year + offset)

        # Remove 'time' from timex_val.
        # For example, If timex_val = 2000-02-20 12:23:34.45, then
        # timex_val = 2000-02-20
        timex_val = re.sub(r'\s.*', '', timex_val)

        # Substitute tag+timex in the text with grounded tag+timex.
        tagged_text = re.sub('<TIMEX2>' + timex_ori + '</TIMEX2>', '<TIMEX2 val=\"' \
            + timex_val + '\">' + timex_ori + '</TIMEX2>', tagged_text)

    return tagged_text

####

def parse(text):
    prepareHashMaps()
    loadStopwords()
    return tag(text)
    # print "Day object found: " + str(day_object)
    # print "Time object found: " + str(time_object)
    # print "Month object found: " + str(month_object)
    # print "Year object found: " + str(year_object)

    # return rel_object,time_object, day_object, month_object, year_object





