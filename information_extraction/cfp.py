import dateparser
import re
from bs4 import BeautifulSoup

"""
Class representing a Call for Paper.
@author Richard Hindes

"""

class Cfp:

    def __init__(self, name="DEFAULT NAME", start_date="01/01/1970", end_date="02/01/1970",
                 location="Lowestoft", submission_deadline="31/12/1969", notification_due="31/12/1969",
                 final_version_deadline="31/12/1969", cfp_text="DEFAULT CFP_TEXT"):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.location = location
        self.submission_deadline = submission_deadline
        self.notification_due = notification_due
        self.final_version_deadline = final_version_deadline
        self.cfp_text = self.remove_noise(cfp_text)

    """
    Function to better display the attributes of a CFP when printed.
    Overrides the build in __str__ method.
    """

    def __str__(self):
        return "NAME: {} START: {} END: {} LOCATION: {} \n SUBMISSION DEADLINE: {} " \
               "NOTIFICATION DUE: {} FINAL VERSION DEADLINE: {}".format(self.name, self.start_date, self.end_date,
                                                                        self.location, self.submission_deadline,
                                                                        self.notification_due,
                                                                        self.final_version_deadline)

    def as_dict(self):
        return {'name': self.name,
                'start_date': self.start_date,
                'end_date': self.end_date,
                'location': self.location,
                'submission_deadline': self.submission_deadline,
                'notification_due': self.notification_due,
                'final_version_deadline': self.final_version_deadline}

    # given a CFP object, return a list of the locations it contains
    def extract_locations(self, nlp):
        doc = nlp(self.cfp_text)

        # Initialise lists for the locations within a given CFP
        cfp_locations = []

        for entity in doc.ents:
            if entity.label_ == "GPE":
                cfp_locations.append(entity.text)
                break

        return cfp_locations

    def extract_dates(self, nlp):
        # a dictonary mapping a date to the sentence it is in
        date_to_sentence = {}
        # returns a list of sentences, split on line breaks.
        split_cfp_text = self.cfp_text.splitlines()

        for sent in split_cfp_text:
            doc = nlp(sent)

            # for each sentence in the cfp, NER tag it.
            # if there is a data in the sentence, store the data and the sentence it is contained in,
            # and map date -> sentence.

            for entity in doc.ents:
                if entity.label_ == "DATE":
                    date = entity.text
                    date_to_sentence[date] = sent

        # removes any dates that cannot be parsed, i.e are incomplete, and makes sentence lowercase for next step
        date_to_sentence = {date: sent.lower() for date, sent in date_to_sentence.items() if
                            dateparser.parse(date) is not None}
        # returns a dictionary of form (date -> sentence)
        return date_to_sentence

    def extract_conference_name(self, nlp, CONFERENCE_NAME_REGEX = re.compile('$^'), ORDINAL_REGEX = re.compile('$^'),
                                           CONJUNCTION_REGEX = re.compile('$^'), URL_REGEX = re.compile('$^')):
        # a dictionary of form (sentence -> score)
        candidate_names = {}
        split_cfp_text = self.cfp_text.splitlines()
        counter = 0

        for sent in split_cfp_text:
            score = 0
            if counter < 5:
                counter += 10 - (2*counter)
            if CONFERENCE_NAME_REGEX.search(sent):
                score += 10
            if ORDINAL_REGEX.search(sent) and counter < 5:
                score += 5
            if CONJUNCTION_REGEX.search(sent):
                score -= 5
            if URL_REGEX.search(sent):
                score -= 3
            if len(sent.split()) < 4 or len(sent.split()) > 20:
                score -= 15
            candidate_names[sent] = score
            counter += 1

        # return the sentence with the highest score
        highest_score = (max(candidate_names, key=candidate_names.get))
        return highest_score

    def remove_noise(self, text):
        text = BeautifulSoup(text, "html.parser").get_text()  # removes any HTML tags
        # text = re.sub("(\\W|\\d)", " ", text)  # removes any non-ASCII characters
        # text = text.replace("\n", "")
        text = text.strip()
        return text

