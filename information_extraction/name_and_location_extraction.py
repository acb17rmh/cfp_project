import pandas
import spacy
from cfp import Cfp
import re
import time

# Create a pandas dataframe for the CFPs
nlp = spacy.load("en_core_web_sm")
dataframe = pandas.read_csv("data/wikicfp_sorted.csv")
cfps = []

CONFERENCE_NAME_REGEX = re.compile("|".join(["workshop", "conference", "meeting", "theme"]), re.IGNORECASE)
ORDINAL_REGEX = re.compile("|".join(["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "nineth",
                                     "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th"]), re.IGNORECASE)
CONJUNCTION_REGEX = re.compile("|".join(["conjunction", "assosciate", "joint"]), re.IGNORECASE)
URL_REGEX = re.compile("|".join(["http", ".co.uk", ".com"]), re.IGNORECASE)

# dictionaries containing locations and dates
cfp_to_conference_name = {}
cfp_to_location = {}

conference_name_score = 0
location_score = 0

# converts each row in the sample data into a CFP object
# if the determined location is included in the labelled location, consider it correct


for row in dataframe.itertuples():
    cfp = Cfp(row[3], row[5], row[6], row[7], row[9], row[10], row[11], row[14])
    cfp_to_conference_name[cfp] = cfp.extract_conference_name(nlp, CONFERENCE_NAME_REGEX, ORDINAL_REGEX,
                                                                   CONJUNCTION_REGEX)
    cfp_to_location[cfp] = cfp.extract_locations(nlp)
    cfp_dict = cfp.as_dict()

    # Gets the first location extracted and uses that as the location (not final)
    if cfp_to_conference_name[cfp]:
        detected_conference_name = cfp_to_conference_name[cfp]
        if detected_conference_name in cfp.name or cfp.name in detected_conference_name:
            conference_name_score += 1

    if cfp_to_location[cfp]:
        detected_location = cfp_to_location[cfp][0]
        if detected_location in cfp.location:
            location_score += 1

    cfp_dict['detected_location'] = detected_location
    cfp_dict['detected_conference_name'] = detected_conference_name
    cfps.append(cfp_dict)

conference_name_accuracy = conference_name_score / len(cfp_to_conference_name.keys())
location_accuracy = location_score / len(cfp_to_location.keys())

# write result to an HTML page
results_dataframe = pandas.DataFrame(cfp for cfp in cfps)
results_dataframe.to_html("results/name_and_location_results{}.html".format(time.time()))

print("TOTAL CORRECT CONFERENCE NAMES: " + str(conference_name_score))
print("TOTAL CFPs: " + str(len(cfp_to_conference_name.keys())))
print("ACCURACY: " + str(conference_name_accuracy))

print("TOTAL CORRECT LOCATIONS: " + str(location_score))
print("TOTAL CFPs: " + str(len(cfp_to_location.keys())))
print("ACCURACY: " + str(location_accuracy))