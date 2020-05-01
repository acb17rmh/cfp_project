from __future__ import unicode_literals, print_function

import dateparser
import pandas
import pprint
import re
import spacy
from cfp import Cfp
import time

# Load CFP data and convert dates from strings into Datetime objects
dataframe = pandas.read_csv('C:/Users/Richard/PycharmProjects/cfp_project/information_extraction/data/final_test_set.csv', encoding="latin-1", usecols=["text", "location", "name", "start_date", "submission_deadline", "notification_due", "final_version_deadline"])


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


def extract_locations(doc):
    """
    Extracts all locations mentioned in the CFP's text.

    Args:
        doc: a spaCy document
    Returns:
        location: the first location mentioned in the text
    """

    # Initialise lists for the locations within a given CFP
    cfp_locations = []

    for entity in doc.ents:
        if entity.label_ == "GPE":
            return entity.text

    return None

def extract_conference_name(split_cfp_text):

    """
    Function to extract the conference name from a CFP text. Uses rule-based patterns to assign scores to substrings
    of the CFP's text, and returns the one with the highest score. Takes regex patterns containing key words to filter
    by as parameters. By default, these regexes will match any string.

    Returns:
        str: The highest ranking string in the text.
    """
    # a dictionary of form (sentence -> score)
    candidate_names = {}
    counter = 0

    conference_name_regex = re.compile(
        "|".join(["workshop", "conference", "meeting", "theme", "international", "symposium", "forum"]))
    ordinal_regex = re.compile(
        "|".join(["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "nineth",
                  "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th"]), re.IGNORECASE)
    conjunction_regex = re.compile("|".join(["conjunction", "assosciate", "joint", "located"]), re.IGNORECASE)
    url_regex = re.compile(
        r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))""")

    for index, sent in enumerate(split_cfp_text):
        score = 0
        sent = sent.strip()
        next_sentence_bonus = False
        if len(sent.split()) < 4 or len(sent.split()) > 20:
            score -= 50
        if counter < 5:
            score += 10 - (2 * counter)
        if next_sentence_bonus:
            score += 10
        if "call for papers" in sent.lower():
            next_sentence_bonus = True
        if sent.endswith(" on") or sent.endswith(" for"):
           sent += " " + split_cfp_text[index + 1]
           print ("COMBINED STRING: " + sent)

        if re.search(conference_name_regex, sent.lower()):
            score += 8
        if re.search(ordinal_regex, sent.lower()) and counter < 10:
            score += 10
        if re.search(conjunction_regex, sent.lower()):
            score -= 5
        if re.search(url_regex, sent.lower()):
            score -= 5

        candidate_names[sent] = score
        counter += 1

    # return the sentence with the highest score
    highest_score = (max(candidate_names, key=candidate_names.get)) if candidate_names else 0

    return highest_score

def preprocess_text(text):
    """
    Method to preprocess text for information extraction. Text is split on newlines and commas,
    and any conference names split over 2 lines are merged into one.

    Returns:
        list: a list of preprocessed sentences.
    """

    text = text.replace('. ', '\n')
    text = text.splitlines()
    text = [substring for substring in text if substring is not ""]
    return text

def extract_dates(split_cfp_text):
    """
    Function which extracts mentions of dates from the CFP's text.

    Args:
        nlp: An instance of a Spacy NLP object.
    Returns:
        dict: A dictionary of form {date -> sentence containing that date}.
    """
    # a dictionary mapping a date to the sentence it is in
    date_to_sentence = {}

    for sentence_doc in nlp.pipe(split_cfp_text, batch_size=len(split_cfp_text), disable=["tagger", "parser"]):
        for entity in sentence_doc.ents:
            if entity.label_ == "DATE" and len(entity.text) >= 6:
                date = entity.text
                date_to_sentence[date] = sentence_doc.text[:]

        # removes any dates that cannot be parsed, i.e are incomplete, and makes sentence lowercase for next step
    date_to_sentence = {date: sent.lower() for date, sent in date_to_sentence.items() if
                        dateparser.parse(date) is not None}
    # returns a dictionary of form (date -> sentence)
    return date_to_sentence

def get_start_date(date_to_sentence):
    conference_start = None

    for date in date_to_sentence:
        sentence = date_to_sentence[date].lower()
        date_object = dateparser.parse(date)

        if re.search(CONFERENCE_DATES_REGEX, sentence):
            conference_start = date_object

    # if no date found for start date, then use the first one found
    if conference_start is None:
        conference_start = list(date_to_sentence)[0]
        conference_start = dateparser.parse(conference_start)

    return conference_start

def get_submission_deadline(date_to_sentence):
    submission_deadline = None
    for date in date_to_sentence:
        sentence = date_to_sentence[date].lower()
        date_object = dateparser.parse(date)

        if re.search(SUBMISSION_DEADLINE_REGEX, sentence):
            if submission_deadline is None:
                submission_deadline = date_object
    return submission_deadline

def get_notification_due(date_to_sentence):
    notification_due = None
    for date in date_to_sentence:
        sentence = date_to_sentence[date].lower()
        date_object = dateparser.parse(date)

        if re.search(NOTIFICATION_DEADLINE_REGEX, sentence):
            if notification_due is None:
                notification_due = date_object
    return notification_due

def get_final_version_deadline(date_to_sentence):
    final_version_deadline = None
    for date in date_to_sentence:
        sentence = date_to_sentence[date].lower()
        date_object = dateparser.parse(date)

        if re.search(FINAL_VERSION_DEADLINE_REGEX, sentence):
            if final_version_deadline is None:
                final_version_deadline = date_object
    return final_version_deadline


documents = []
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


for doc in nlp.pipe(dataframe['text']):
    documents.append(doc)

dataframe['document'] = documents
dataframe['detected_location'] = dataframe['document'].apply(extract_locations)
dataframe['split_cfp_text'] = dataframe['text'].apply(preprocess_text)
dataframe['detected_conference_name'] = dataframe['split_cfp_text'].apply(extract_conference_name)
dataframe['date_to_sentence'] = dataframe['split_cfp_text'].apply(extract_dates)
dataframe['detected_start_date'] = dataframe['date_to_sentence'].apply(get_start_date)
dataframe['detected_submission_deadline'] = dataframe['date_to_sentence'].apply(get_submission_deadline)
dataframe['detected_notification_due'] = dataframe['date_to_sentence'].apply(get_notification_due)
dataframe['detected_final_version_deadline'] = dataframe['date_to_sentence'].apply(get_final_version_deadline)

dataframe.to_csv('C:/Users/Richard/PycharmProjects/cfp_project/information_extraction/NEW_RESULTS/new_results{}.csv'.format(time.time()),
                  columns=["name", "location", "start_date", "submission_deadline", "notification_due", "final_version_deadline",
                           "detected_conference_name", "detected_location", "detected_start_date", "detected_submission_deadline",
                           "detected_notification_due", "detected_final_version_deadline"], date_format='%d/%m/%Y')

