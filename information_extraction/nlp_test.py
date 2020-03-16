from __future__ import unicode_literals, print_function
import pandas
import spacy
import re
import pprint
from cfp import Cfp

# Load CFP data and convert dates from strings into Datetime objects
dataframe = pandas.read_csv('data/wikicfp_sorted.csv').head(1)
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
nlp = spacy.load("en_core_web_sm")

for row in dataframe.itertuples():
    cfp = Cfp(row[3], row[5], row[6], row[7], row[9], row[10], row[11], row[14])
    cfps.append(cfp)

sample_cfp = cfps[0]

document = nlp(sample_cfp.cfp_text)

print (document)