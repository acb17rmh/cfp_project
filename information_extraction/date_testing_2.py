from __future__ import unicode_literals, print_function

import dateparser
import pandas
import pprint
import re
import spacy
from cfp import Cfp
import time


# Load CFP data and convert dates from strings into Datetime objects
dataframe = pandas.read_csv('data/wikicfp_sorted.csv')
dataframe['start_date']= pandas.to_datetime(dataframe['start_date'], format='%d/%m/%Y')
dataframe['end_date']= pandas.to_datetime(dataframe['end_date'], format='%d/%m/%Y')
dataframe['submission_deadline']= pandas.to_datetime(dataframe['submission_deadline'], format='%d/%m/%Y')
dataframe['notification_due']= pandas.to_datetime(dataframe['notification_due'], format='%d/%m/%Y')
dataframe['final_version_deadline']= pandas.to_datetime(dataframe['final_version_deadline'], format='%d/%m/%Y')

# Regex patterns for identifying which date is which
CONFERENCE_DATES_REGEX = re.compile("|".join(["when", "date", "workshop", "held", "conference", "symposium"]))
SUBMISSION_DEADLINE_REGEX = re.compile("|".join(["submit", "submission", "paper", "due", "deadline"]))
FINAL_VERSION_DEADLINE_REGEX = re.compile("|".join(["final", "camera", "ready", "camera-ready", "last"]))
NOTIFICATION_DEADLINE_REGEX = re.compile("|".join(["notice", "notices", "notified", "notification", "notifications"]))
cfps = []
pp = pprint.PrettyPrinter(indent=4)

"""
example_date1 = ("27-30 March 2020")
example_date2 = ("December 9-11, 2010")
example_date3 = ("November 16 and 17 2010")



# Takes a split date and returns a tuple of (start date, end date)
def split_date(date):
    x = date.split(" ")
    for token in x:
        if "-" in token:
            split_days = token.split("-")
            x.remove(token)
            x.append(split_days[0])
            x.append(split_days[1])
        x.sort(key = len)
        if token == "and" or token == "-" or token == "":
            x.remove(token)

    start_date = x[0] + " " + x[3] + " " + x[2]
    end_date = x[1] + " " +  x[3] + " " + x[2]

    return dateparser.parse(start_date), dateparser.parse(end_date)


print (split_date(example_date1))
print (split_date(example_date2))
print (split_date(example_date3))
"""
total_words = 0
counter = 0

for row in dataframe.itertuples():

    # Turn each row of raw data into a CFP object
    cfp = Cfp(row[3], row[5], row[6], row[7], row[9], row[10], row[11], row[14])
    (cfp.preprocess_text())






















