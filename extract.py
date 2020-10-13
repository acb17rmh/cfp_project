import datetime

import dateparser
import pandas
import re
import spacy
import argparse
import os.path

# Handles loading in files via command line arguments
def is_valid_file(parser, arg):
    """
    Given a file path, checks that the file exists.
    Args:
        arg: the path to the file
    Returns:
          str: the file path as a string (if the file does exist)
          error: an error (if the file does not exist)
    """
    if not os.path.isfile(arg):
        parser.error("ERROR: file %s does not exist." % arg) # if no file throw error
    else:
        return arg  # else return file path

parser = argparse.ArgumentParser(description='Extracts information from a CSV file of labelled CFPs.')
parser._action_groups.pop()
required = parser.add_argument_group('required arguments')
optional = parser.add_argument_group('optional arguments')
required.add_argument('-i', '-input', dest="input_file", required=True, help='a labelled CSV file to read from',
                    type=lambda x: is_valid_file(parser, x))
optional.add_argument('-o', '-output', dest="output_file", default="results/extracted_info.csv",
                    help='a CSV file to write to. By default, will write to results/extracted_info.csv')
args = parser.parse_args()

# Load CFP data and convert dates from strings into Datetime objects
dataframe = pandas.read_csv(args.input_file, encoding="latin-1", usecols=["text", "location", "name", "start_date", "end_date", "submission_deadline", "notification_due", "final_version_deadline"])

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

def extract_locations(doc):
    """
    Extracts the first location mentioned in the CFP's text
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
    Args:
        split_cfp_text: A list containing strings, where each string is a sentence in the original text.
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
    Args:
        split_cfp_text: A list containing strings, where each string is a sentence in the original text.
    Returns:
        list: a list of preprocessed sentences.
    """

    text = text.replace('. ', '\n')
    text = text.replace('? ', '\n')
    text = text.replace('! ', '\n')
    text = text.splitlines()
    text = [substring for substring in text if substring != ""]
    return text

def extract_dates(split_cfp_text):
    """
    Function which extracts mentions of dates from the CFP's text.
    Args:
        split_cfp_text: A list containing strings, where each string is a sentence in the original text.
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
    # returns a dictionary of form (date -
    return date_to_sentence

def get_start_date(date_to_sentence):
    """
    Function to extract the start date of a conference from a Call for Paper.
    Args:
        date_to_sentence: a dictionary mapping each date in the text to the sentence containing it.
    Returns:
        conference_start: The date the conference starts, as a DateTime object.
    """

    if not date_to_sentence:
        return None

    conference_start = None

    for date in date_to_sentence:
        sentence = date_to_sentence[date].lower()
        if re.search(CONFERENCE_DATES_REGEX, sentence):
            conference_start = split_dates(date)[0]

    # if no date found for start date, then use the first one found
    if conference_start is None:
        conference_start = list(date_to_sentence)[0]
        conference_start = dateparser.parse(conference_start)

    return conference_start

def get_end_date(date_to_sentence):
    """
    Function to extract the end date of a conference from a Call for Paper.
    Args:
        date_to_sentence: a dictionary mapping each date in the text to the sentence containing it.
    Returns:
        conference_start: The date the conference ends, as a DateTime object.
    """

    if not date_to_sentence:
        return None

    conference_end = None

    for date in date_to_sentence:
        sentence = date_to_sentence[date].lower()
        if re.search(CONFERENCE_DATES_REGEX, sentence):
            conference_end = split_dates(date)[1]

    return conference_end

def get_submission_deadline(date_to_sentence):
    """
    Function to extract the submission deadline of a conference from a Call for Paper.
    Args:
        date_to_sentence: a dictionary mapping each date in the text to the sentence containing it.
    Returns:
        submission_deadline: The submission deadline date, as a DateTime object.
    """
    if not date_to_sentence:
        return None
    submission_deadline = None
    for date in date_to_sentence:
        sentence = date_to_sentence[date].lower()
        date_object = dateparser.parse(date)

        if re.search(SUBMISSION_DEADLINE_REGEX, sentence):
            if submission_deadline is None:
                submission_deadline = date_object
    return submission_deadline

def get_notification_due(date_to_sentence):
    """
    Function to extract the submission deadline of a conference from a Call for Paper.
    Args:
        date_to_sentence: a dictionary mapping each date in the text to the sentence containing it.
    Returns:
        notification_due: The notification due date, as a DateTime object.
    """
    if not date_to_sentence:
        return None
    notification_due = None
    for date in date_to_sentence:
        sentence = date_to_sentence[date].lower()
        date_object = dateparser.parse(date)

        if re.search(NOTIFICATION_DEADLINE_REGEX, sentence):
            if notification_due is None:
                notification_due = date_object
    return notification_due

def get_final_version_deadline(date_to_sentence):
    """
    Function to extract the submission deadline of a conference from a Call for Paper.
    Args:
        date_to_sentence: a dictionary mapping each date in the text to the sentence containing it.
    Returns:
        final_version_deadline: The final version deadline date, as a DateTime object.
    """
    if not date_to_sentence:
        return None
    final_version_deadline = None
    for date in date_to_sentence:
        sentence = date_to_sentence[date].lower()
        date_object = dateparser.parse(date)

        if re.search(FINAL_VERSION_DEADLINE_REGEX, sentence):
            if final_version_deadline is None:
                final_version_deadline = date_object
    return final_version_deadline


def split_dates(raw_date):
    """
    Function to split a date range into a separate start date and end date.
    Args:
        raw_date: the raw text date range to split
    Returns:
        (start_date, end_date): a tuple of DateTime objects
    """

    print (raw_date)
    start_date = None
    end_date = None

    if "-" not in raw_date:
        start_date = (dateparser.parse(raw_date))
        end_date = (dateparser.parse(raw_date))
    elif raw_date[0].isdigit():
        split = (raw_date.split("-"))
        start_date = (dateparser.parse(raw_date))
        end_date = (dateparser.parse(split[1]))
    else:
        split = (raw_date.split(" "))
        print (split)
        for data in split:
            if "-" in data:
                split_days = data.split("-")
                if len(split) == 3:
                    start_date_string = split_days[0] + " " + split[0] + " " + split[2]
                    end_date_string = split_days[1] + " " + split[0] + " " + split[2]
                else:
                    # year defaults to current year if none supplied
                    now = datetime.datetime.now()
                    start_date_string = split_days[0] + " " + split[0] + " " + str(now.year)
                    end_date_string = split_days[1] + " " + split[0] + " " + str(now.year)
                start_date = dateparser.parse(start_date_string)
                end_date = dateparser.parse(end_date_string)

    return (start_date, end_date)

if __name__ == "__main__":

    nlp = spacy.load('en_core_web_sm', disable=['tagger', 'parser', 'textcat'])
    documents = []

    for doc in nlp.pipe(dataframe['text']):
        documents.append(doc)

    dataframe['document'] = documents
    dataframe['detected_location'] = dataframe['document'].apply(extract_locations)
    dataframe['split_cfp_text'] = dataframe['text'].apply(preprocess_text)
    dataframe['detected_conference_name'] = dataframe['split_cfp_text'].apply(extract_conference_name)
    dataframe['date_to_sentence'] = dataframe['split_cfp_text'].apply(extract_dates)
    dataframe['detected_start_date'] = dataframe['date_to_sentence'].apply(get_start_date)
    dataframe['detected_end_date'] = dataframe['date_to_sentence'].apply(get_end_date)
    dataframe['detected_submission_deadline'] = dataframe['date_to_sentence'].apply(get_submission_deadline)
    dataframe['detected_notification_due'] = dataframe['date_to_sentence'].apply(get_notification_due)
    dataframe['detected_final_version_deadline'] = dataframe['date_to_sentence'].apply(get_final_version_deadline)

    dataframe.to_csv(args.output_file, columns=["text", "notification_due", "start_date", "end_date", "location",
                                                "final_version_deadline", "name", "submission_deadline",
                                                "detected_conference_name", "detected_location", "detected_start_date", "detected_end_date",
                                                "detected_submission_deadline", "detected_notification_due",
                                                "detected_final_version_deadline"], date_format='%d/%m/%Y')
    print ("Extracted data saved to {}".format(args.output_file))

