import dateparser
import pandas
import pprint
import re
import spacy
from cfp import Cfp
import time
import nltk



dataframe = pandas.read_csv('data/test_set.csv', encoding="latin-1").fillna(" ").head(10)
nlp = spacy.load("en_core_web_sm")

CONFERENCE_DATES_REGEX = re.compile("|".join(["when", "date", "workshop", "held", "conference"]))
SUBMISSION_DEADLINE_REGEX = re.compile("|".join(["submit", "submission", "paper", "due", "deadline"]))
FINAL_VERSION_DEADLINE_REGEX = re.compile("|".join(["final", "camera", "ready", "camera-ready", "last", "manuscript"]))
NOTIFICATION_DEADLINE_REGEX = re.compile("|".join(["notice", "notices", "notified", "notification", "notifications", "acceptance"]))
CONFERENCE_NAME_REGEX = re.compile("|".join(["workshop", "conference", "meeting", "theme", "international", "symposium"]))

cfps = []
for row in dataframe.itertuples():
    # Turn each row of raw data into a CFP object
    cfp = Cfp(row.name, row.start_date, row.end_date, row.location, row.submission_deadline, row.notification_due,
              row.final_version_deadline, row.text, str(row.link))
    cfps.append(cfp)

# a dictionary mapping a date to the sentence it is in
date_to_sentence = {}

example_cfp = cfps[3]

print (example_cfp.extract_locations(nlp))
print (example_cfp.cfp_text)
