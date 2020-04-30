from __future__ import unicode_literals, print_function

import dateparser
import pandas
import pprint
import re
import spacy
from cfp import Cfp
import time

# Load CFP data and convert dates from strings into Datetime objects
dataframe = pandas.read_csv('C:/Users/Richard/PycharmProjects/cfp_project/information_extraction/data/final_test_set.csv', encoding="latin-1")
dataframe['start_date']= pandas.to_datetime(dataframe['start_date'], format='%d/%m/%Y')
dataframe['end_date']= pandas.to_datetime(dataframe['end_date'], format='%d/%m/%Y')
dataframe['submission_deadline']= pandas.to_datetime(dataframe['submission_deadline'], format='%d/%m/%Y')
dataframe['notification_due']= pandas.to_datetime(dataframe['notification_due'], format='%d/%m/%Y')
dataframe['final_version_deadline']= pandas.to_datetime(dataframe['final_version_deadline'], format='%d/%m/%Y')

# Regex patterns for identifying which date is which
CONFERENCE_DATES_REGEX = re.compile("|".join(["when", "workshop", "held", "conference", "held"]))
SUBMISSION_DEADLINE_REGEX = re.compile("|".join(["submit", "submission", "paper", "due", "deadline"]))
FINAL_VERSION_DEADLINE_REGEX = re.compile("|".join(["final", "camera", "ready", "camera-ready", "last", "manuscript"]))
NOTIFICATION_DEADLINE_REGEX = re.compile("|".join(["notice", "notices", "notified", "notification", "notifications", "acceptance"]))
CONFERENCE_NAME_REGEX = re.compile("|".join(["workshop", "conference", "meeting", "theme", "international", "symposium", "forum"]))
ORDINAL_REGEX = re.compile(
    "|".join(["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "nineth",
              "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th"]), re.IGNORECASE)
CONJUNCTION_REGEX = re.compile("|".join(["conjunction", "assosciate", "joint", "located"]), re.IGNORECASE)
WEB_URL_REGEX = re.compile(
    r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))""")

# Takes a split date in the form DD-DD Month Year
# and returns a tuple of datetime objects
# TODO: split conference dates into start and end
def split_date(date):
    date = str(date)
    if "-" in date:
        new_date = date.split("-")[1]
        return (dateparser.parse(date), dateparser.parse(new_date))
    else:
        return (dateparser.parse(date), None)


cfps = []
pp = pprint.PrettyPrinter(indent=4)

# dictionary mapping a cfp to the dates within it
cfp_to_dates = {}
conference_start_score = 0
conference_end_score = 0
submission_score = 0
notification_score = 0
final_version_score = 0
conference_name_score = 0
location_score = 0
url_score = 0
joint_score = 0
triggers = 0
counter = 0


nlp = spacy.load('en_core_web_sm', disable=['tagger', 'parser', 'textcat'])
print (nlp.pipe_names)

for row in dataframe.itertuples():

    # Turn each row of raw data into a CFP object
    cfp = Cfp(row.name, row.start_date, row.end_date, row.location, row.submission_deadline, row.notification_due,
              row.final_version_deadline, row.text, str(row.link))
    cfp_dict = cfp.as_dict()
    counter += 1

    detected_location = ""
    detected_url = ""
    detected_conference_name = ""

    if cfp.extract_locations(nlp):
        detected_location = cfp.extract_locations(nlp)[0]
    if cfp.extract_urls():
        detected_url = cfp.extract_urls()[0]
    if cfp.extract_conference_name(CONFERENCE_NAME_REGEX, ORDINAL_REGEX,  CONJUNCTION_REGEX, WEB_URL_REGEX):
        detected_conference_name = cfp.extract_conference_name(CONFERENCE_NAME_REGEX, ORDINAL_REGEX,
                                                              CONJUNCTION_REGEX, WEB_URL_REGEX)

    cfp_dict["split_text"] = cfp.extract_useful_sentences()

    if str(detected_conference_name) in cfp.name or cfp.name in str(detected_conference_name):
        conference_name_score += 1
        cfp_dict["correct_conference_name"] = True

    # Gets the first location extracted and uses that as the location (not final)
    if str(detected_location) in cfp.location or cfp.location in str(detected_location):
        location_score += 1
        cfp_dict["correct_location"] = True

    if str(detected_url) in cfp.url or cfp.url in str(detected_url):
        url_score += 1
        cfp_dict["correct_URL"] = True


    date_to_sentence = {}
    if cfp.extract_dates(nlp):
        date_to_sentence = cfp.extract_dates(nlp)
        cfps.append(cfp_dict)

    cfp_to_dates[cfp] = date_to_sentence
    cfp_dict["date_to_sentence"] = date_to_sentence

    conference_start = None
    submission_deadline = None
    notification_due = None
    final_version_deadline = None

    for date in date_to_sentence:
        sentence = date_to_sentence[date].lower()
        date_object = dateparser.parse(date)

        if re.search(CONFERENCE_DATES_REGEX, sentence):
            if conference_start is None:
                conference_start = date_object
        if re.search(SUBMISSION_DEADLINE_REGEX, sentence):
            if submission_deadline is None:
                submission_deadline = date_object
            # print("MATCHED SUBMISSION REGEX: " + str(submission_deadline))
        if re.search(NOTIFICATION_DEADLINE_REGEX, sentence):
            if notification_due is None:
                notification_due = date_object
            # print("MATCHED NOTIFICATION REGEX: " + str(notification_due))
        if re.search(FINAL_VERSION_DEADLINE_REGEX, sentence):
            if final_version_deadline is None:
                final_version_deadline = date_object
            # print("MATCHED FINAL VERSION REGEX: " + str(final_version_deadline))

    # if no date found for start date, then use the first one found
    if conference_start is None and cfp.extract_dates(nlp):
        conference_start = list(date_to_sentence)[0]
        conference_start = dateparser.parse(conference_start)

    cfp_dict['detected_start_date'] = conference_start
    cfp_dict['detected_submission_deadline'] = submission_deadline
    cfp_dict['detected_notification_due'] = notification_due
    cfp_dict['detected_final_version'] = final_version_deadline
    cfp_dict['detected_location'] = detected_location
    cfp_dict['detected_conference_name'] = detected_conference_name
    cfp_dict['detected_url'] = detected_url

    if conference_start == cfp.start_date:
        conference_start_score += 1
        cfp_dict["correct_start_date"] = True
    if submission_deadline == cfp.submission_deadline:
       submission_score += 1
    cfp_dict["correct_submission_deadline"] = True
    if notification_due == cfp.notification_due:
        notification_score += 1
        cfp_dict["correct_notification_due"] = True
    if final_version_deadline == cfp.final_version_deadline:
        final_version_score += 1
        cfp_dict["correct_final_version_deadline"] = True
    if {'correct_start_date', 'correct_location', 'correct_conference_name'} <= cfp_dict.keys():
       joint_score += 1
       cfp_dict['joint_accuracy'] = True

results_dataframe = pandas.DataFrame(cfp for cfp in cfps)
results_dataframe.to_csv('C:/Users/Richard/PycharmProjects/cfp_project/information_extraction/results/full_results{}.csv'.format(time.time()), date_format='%d/%m/%Y')


count = len(results_dataframe)
print (conference_start_score, submission_score, notification_score, final_version_score, conference_name_score, location_score, url_score, joint_score)
print("CONFERENCE START DATE ACCURACY: {:.2%}".format(conference_start_score/count))
print("SUBMISSION DATE ACCURACY: {:.2%}".format(submission_score/count))
print("NOTIFICATION DATE ACCURACY: {:.2%}".format(notification_score/count))
print("FINAL VERSION DEADLINE ACCURACY: {:.2%}".format(final_version_score/count))
print("CONFERENCE NAME ACCURACY: {:.2%}".format(conference_name_score/count))
print("LOCATION ACCURACY: {:.2%}".format(location_score/count))
print("URL ACCURACY: {:.2%}".format(url_score/count))
print("JOINT PERCENTAGE: {:.2%}".format(joint_score/count))