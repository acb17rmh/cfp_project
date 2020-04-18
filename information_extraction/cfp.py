import dateparser
import re

class Cfp:

    """
    Class representing a Call for Paper (CFP) object. Each CFP object contains attributes corresponding to its labels
    in the dataset, as well as a field containing the CFP's text.
    """
    def __init__(self, name="DEFAULT NAME", start_date="01/01/1970", end_date="02/01/1970",
                 location="Lowestoft", submission_deadline="31/12/1969", notification_due="31/12/1969",
                 final_version_deadline="31/12/1969", cfp_text="DEFAULT CFP_TEXT", url="https://google.com"):
        """
        Constructs a CFP object.

        Attributes:
            name: The conference's name as a string.
            start_date: The conference's start date, as a string in DD/MM/YYYY format.
            end_date: The conferenece's end date, as a string in DD/MM/YYYY format.
            location: The place the conference is being held, as a string.
            submission_deadline: The date of the conference's submission deadline, as a string in DD/MM/YYYY format.
            notification_due: The notification due date of the conference, as a string in DD/MM/YYYY format.
            final_version_deadline: The conference's final version deadline, as a string in DD/MM/YYYY format.
            cfp_text: The CFP's body text.
            url: The web address of the conference.
        """

        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.location = location
        self.submission_deadline = submission_deadline
        self.notification_due = notification_due
        self.final_version_deadline = final_version_deadline
        self.cfp_text = cfp_text
        self.url = url

    def __str__(self):
        """
        Function to better display the attributes of a CFP when printed.
        Overrides the build in __str__ method.
        """
        return "NAME: {} START: {} END: {} LOCATION: {} \n SUBMISSION DEADLINE: {} " \
               "NOTIFICATION DUE: {} FINAL VERSION DEADLINE: {} URL: {}".format(self.name, self.start_date, self.end_date,
                                                                        self.location, self.submission_deadline,
                                                                        self.notification_due,
                                                                        self.final_version_deadline, self.url)


    def as_dict(self):
        """
        Returns the CFP object as a dictionary.
        Returns:
            dict: A dictionary representing the CFP object.
        """
        return {'name': self.name,
                'start_date': self.start_date,
                'end_date': self.end_date,
                'location': self.location,
                'submission_deadline': self.submission_deadline,
                'notification_due': self.notification_due,
                'final_version_deadline': self.final_version_deadline,
                'cfp_text': self.cfp_text,
                'url': self.url}


    def extract_locations(self, nlp):
        """
        Extracts all locations mentioned in the CFP's text.

        Args:
            nlp: An instance of a Spacy NLP object.
        Returns:
            list: A list of all locations mentioned in the CFP's text.
        """
        doc = nlp(self.cfp_text)

        # Initialise lists for the locations within a given CFP
        cfp_locations = []

        for entity in doc.ents:
            if entity.label_ == "GPE":
                cfp_locations.append(entity.text)

        return cfp_locations

    def extract_dates(self, nlp):
        """
        Function which extracts mentions of dates from the CFP's text.

        Args:
            nlp: An instance of a Spacy NLP object.
        Returns:
            dict: A dictionary of form {date -> sentence containing that date}.
        """
        # a dictionary mapping a date to the sentence it is in
        date_to_sentence = {}
        # returns a list of sentences, split on line breaks.
        split_cfp_text = self.cfp_text.splitlines()

        for sent in split_cfp_text:
            doc = nlp(sent)

            # for each sentence in the cfp, NER tag it.
            # if there is a data in the sentence, store the data and the sentence it is contained in,
            # and map date -> sentence.

            for entity in doc.ents:
                if entity.label_ == "DATE" and len(entity.text) >= 10:
                    date = entity.text
                    date_to_sentence[date] = sent

        # removes any dates that cannot be parsed, i.e are incomplete, and makes sentence lowercase for next step
        date_to_sentence = {date: sent.lower() for date, sent in date_to_sentence.items() if
                            dateparser.parse(date) is not None}
        # returns a dictionary of form (date -> sentence)
        return date_to_sentence



    # TODO: improve conference name extraction
    def extract_conference_name(self, conference_name_regex=re.compile('$^'), ordinal_regex=re.compile('$^'),
                                conjunction_regex=re.compile('$^'), url_regex=re.compile('$^')):

        """
        Function to extract the conference name from a CFP text. Uses rule-based patterns to assign scores to substrings
        of the CFP's text, and returns the one with the highest score. Takes regex patterns containing key words to filter
        by as parameters. By default, these regexes will match any string.

        Args:
            conference_name_regex: a regular expression matching key terms in a conference's name.
                                   By default, it will match any string.
            ordinal_regex: a regular expression matching ordinal numbers in a conference's name.
                           By default, it will match any string.
            conjunction_name_regex: a regular expression matching terms signifying a conference is a joint conference.
                                    By default, it will match any string.
            url_regex: a regular expression matching URLs. By default, it will match any string.

        Returns:
            str: The highest ranking string in the text.
        """
        # a dictionary of form (sentence -> score)
        candidate_names = {}
        split_cfp_text = self.preprocess_text()
        print (split_cfp_text)
        counter = 0

        for sent in split_cfp_text:
            score = 0
            if len(sent.split()) < 4 or len(sent.split()) > 20:
                score -= 50
            if counter < 5:
                counter += 10 - (2 * counter)
            for word in sent.split():
                if conference_name_regex.search(word):
                    score += 8
                if ordinal_regex.search(word) and counter < 10:
                    score += 10
                if conjunction_regex.search(word):
                    score -= 5
                if url_regex.search(word):
                    score -= 5

            candidate_names[sent] = score
            counter += 1

        # return the sentence with the highest score
        highest_score = (max(candidate_names, key=candidate_names.get)) if candidate_names else 0
        return highest_score


    def extract_urls(self, web_url_regex=re.compile('$^')):
        """
        Method to extract any URLs from a CFP's text.

        Args:
            web_url_regex: a regular expression matching URLs. By default, it will match any string.
        Returns:
            list: A list of all mentions of URLs in the CFP's text.
        """
        urls = []
        split_cfp_text = self.preprocess_text()
        for sent in split_cfp_text:
            if web_url_regex.search(sent):
                urls.append(web_url_regex.search(sent).group(0))
        return urls


    def preprocess_text(self):
        """
        Method to preprocess text for information extraction. Text is split on newlines and commas,
        and any conference names split over 2 lines are merged into one.

        Returns:
            list: a list of preprocessed sentences.
        """
        text = self.cfp_text.replace("\n", ". ")
        text = self.cfp_text.replace("\t", ". ")
        text = self.cfp_text.replace("  ", ". ")
        split_text = text.split(". ")
        split_text = [sent for sent in split_text if sent is not ""]
        """
        for index, sent in enumerate(split_text):
            if sent == "":
                split_text.remove(sent)
            if "  " in sent:
                split_text.remove(sent)
            if sent.endswith(" on") and ("conference" in sent.lower() or "workshop" in sent.lower() or
                                         "international" in sent.lower() or "symposium" in sent.lower()):
                full_name = (split_text[index] + " " + split_text[index + 1])
                return [full_name] + split_text
        """
        return split_text
