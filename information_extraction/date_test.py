from __future__ import unicode_literals, print_function

import dateparser
import pandas
import pprint
import re
import spacy
from cfp import Cfp

# Load CFP data and convert dates from strings into Datetime objects
dataframe = pandas.read_csv('data/wikicfp_sorted.csv').head(5)
dataframe['start_date']= pandas.to_datetime(dataframe['start_date'], format='%d/%m/%Y')
dataframe['end_date']= pandas.to_datetime(dataframe['end_date'], format='%d/%m/%Y')
dataframe['submission_deadline']= pandas.to_datetime(dataframe['submission_deadline'], format='%d/%m/%Y')
dataframe['notification_due']= pandas.to_datetime(dataframe['notification_due'], format='%d/%m/%Y')
dataframe['final_version_deadline']= pandas.to_datetime(dataframe['final_version_deadline'], format='%d/%m/%Y')

# Regex patterns for identifying which date is which
CONFERENCE_DATES_REGEX = re.compile("|".join(["when", "date", "workshop", "held", "conference"]))
SUBMISSION_DEADLINE_REGEX = re.compile("|".join(["submit", "submission", "paper", "due"]))
FINAL_VERSION_DEADLINE_REGEX = re.compile("|".join(["final", "camera", "ready", "camera-ready", "last"]))
NOTIFICATION_DEADLINE_REGEX = re.compile("|".join(["notice", "notices", "notified", "notification", "notifications"]))

cfps = []
pp = pprint.PrettyPrinter(indent=4)

for row in dataframe.itertuples():
    cfp = Cfp(row[3], row[5], row[6], row[7], row[9], row[10], row[11], row[14])
    cfps.append(cfp)

nlp = spacy.load("en")

# dictionary mapping a cfp to the dates within in
cfp_to_dates = {}
submission_score = 0
notification_score = 0
final_version_score = 0


for cfp in cfps:

    date_to_sentence = cfp.extract_dates(nlp)
    cfp_to_dates[cfp] = date_to_sentence

    submission_deadline = None
    notification_due = None
    final_version_deadline = None

    for date in date_to_sentence:
        sentence = date_to_sentence[date]
        date_object = dateparser.parse(date)

        if SUBMISSION_DEADLINE_REGEX.search(sentence):
            if submission_deadline is None:
                submission_deadline = date_object
            print("MATCHED SUBMISSION REGEX: " + str(submission_deadline))
        elif NOTIFICATION_DEADLINE_REGEX.search(sentence):
            if notification_due is None:
                notification_due = date_object
            print("MATCHED NOTIFICATION REGEX: " + str(notification_due))
        elif FINAL_VERSION_DEADLINE_REGEX.search(sentence):
            if final_version_deadline is None:
                final_version_deadline = date_object
            print("MATCHED FINAL VERSION REGEX: " + str(final_version_deadline))

    if submission_deadline == cfp.submission_deadline:
       submission_score += 1
    if notification_due == cfp.notification_due:
        notification_score += 1
    if final_version_deadline == cfp.final_version_deadline:
        final_version_score += 1

print (submission_score, notification_score, final_version_score)
