from __future__ import unicode_literals, print_function

import dateparser
import pandas
import pprint
import re
import spacy
from cfp import Cfp

# Load CFP data and convert dates from strings into Datetime objects
dataframe = pandas.read_csv('data/wikicfp_sorted.csv')
dataframe['start_date']= pandas.to_datetime(dataframe['start_date'], format='%d/%m/%Y')
dataframe['end_date']= pandas.to_datetime(dataframe['end_date'], format='%d/%m/%Y')
dataframe['submission_deadline']= pandas.to_datetime(dataframe['submission_deadline'], format='%d/%m/%Y')
dataframe['notification_due']= pandas.to_datetime(dataframe['notification_due'], format='%d/%m/%Y')
dataframe['final_version_deadline']= pandas.to_datetime(dataframe['final_version_deadline'], format='%d/%m/%Y')

# Regex patterns for identifying which date is which
CONFERENCE_DATES_REGEX = re.compile("|".join(["when", "date", "workshop", "held", "conference"]))
SUBMISSION_DEADLINE_REGEX = re.compile("|".join(["submit", "submission", "paper", "due", "deadline"]))
FINAL_VERSION_DEADLINE_REGEX = re.compile("|".join(["final", "camera", "ready", "camera-ready", "last"]))
NOTIFICATION_DEADLINE_REGEX = re.compile("|".join(["notice", "notices", "notified", "notification", "notifications"]))

cfps = []
pp = pprint.PrettyPrinter(indent=4)
nlp = spacy.load("en_core_web_sm")

# dictionary mapping a cfp to the dates within it
cfp_to_dates = {}
conference_start_score = 0
submission_score = 0
notification_score = 0
final_version_score = 0
triggers = 0

# TODO: find more readable way of creating CFP list?
for row in dataframe.itertuples():

    # Turn each row of raw data into a CFP object
    cfp = Cfp(row[3], row[5], row[6], row[7], row[9], row[10], row[11], row[14])
    cfp_dict = cfp.as_dict()
    cfps.append(cfp_dict)

    date_to_sentence = cfp.extract_dates(nlp)
    cfp_to_dates[cfp] = date_to_sentence

    conference_start = None
    submission_deadline = None
    notification_due = None
    final_version_deadline = None

    # Naive method, use first detected date as conference start date
    # TODO: find a better way to extract conference dates
    conference_start = list(date_to_sentence.keys())[0]
    conference_start = dateparser.parse(conference_start)

    for date in date_to_sentence:
        sentence = date_to_sentence[date]
        date_object = dateparser.parse(date)

        if SUBMISSION_DEADLINE_REGEX.search(sentence):
            if submission_deadline is None:
                submission_deadline = date_object
            # print("MATCHED SUBMISSION REGEX: " + str(submission_deadline))
        if NOTIFICATION_DEADLINE_REGEX.search(sentence):
            if notification_due is None:
                notification_due = date_object
            # print("MATCHED NOTIFICATION REGEX: " + str(notification_due))
        if FINAL_VERSION_DEADLINE_REGEX.search(sentence):
            if final_version_deadline is None:
                final_version_deadline = date_object
            # print("MATCHED FINAL VERSION REGEX: " + str(final_version_deadline))

    if conference_start == cfp.start_date:
        conference_start_score += 1
    if submission_deadline == cfp.submission_deadline:
       submission_score += 1
    if notification_due == cfp.notification_due:
        notification_score += 1
    if final_version_deadline == cfp.final_version_deadline:
        final_version_score += 1

    cfp_dict['detected_start_date'] = conference_start
    cfp_dict['detected_submission_deadline'] = submission_deadline
    cfp_dict['detected_notification_due'] = notification_due
    cfp_dict['detected_final_version_deadline'] = final_version_deadline

results_dataframe = pandas.DataFrame(cfp for cfp in cfps)
results_dataframe.to_html("results/date_results.html")

print (conference_start_score, submission_score, notification_score, final_version_score)
