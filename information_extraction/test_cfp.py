import unittest
import spacy
from cfp import Cfp

class TestCfp(unittest.TestCase):

    def setUp(self):
        self.cfp1 = Cfp("The 1st Test Workshop", "25/03/2020", "30/03/2020", "Sheffield", "25/02/2020",
                        "26/02/2020", "27/02/2020", "The 1st Test Workshop, 25th - 30th March 2020, http://www.sheffield.ac.uk/",
                        "http://www.sheffield.ac.uk/")
        self.cfp2 = Cfp(cfp_text = "The 4th Annual Conference for NLP, London, England, 25-29 June 2018.")
        self.nlp = spacy.load("en_core_web_sm")

    def tearDown(self):
        pass

    def test_as_dict(self):
        self.assertEqual(self.cfp1.as_dict(), {'name': "The 1st Test Workshop",
                                            'start_date': "25/03/2020",
                                            'end_date': "30/03/2020",
                                            'location': "Sheffield",
                                            'submission_deadline': "25/02/2020",
                                            'notification_due': "26/02/2020",
                                            'final_version_deadline': "27/02/2020",
                                            'url': "http://www.sheffield.ac.uk/"})

        self.assertEqual(self.cfp2.as_dict(), {'name': "DEFAULT NAME",
                                            'start_date': "01/01/1970",
                                            'end_date': "02/01/1970",
                                            'location': "Lowestoft",
                                            'submission_deadline': "31/12/1969",
                                            'notification_due': "31/12/1969",
                                            'final_version_deadline': "31/12/1969",
                                            'url': "https://google.com"})

    def test_extract_locations(self):
        nlp = spacy.load("en_core_web_sm")
        self.assertEqual(self.cfp1.extract_locations(nlp), [])
        self.assertEqual(self.cfp2.extract_locations(nlp), ["London", "England"])

    def test_extract_dates(self):
        nlp = spacy.load("en_core_web_sm")
        self.assertEqual(self.cfp1.extract_dates(nlp), {"25th - 30th March 2020": "the 1st test workshop, 25th - 30th march 2020, http://www.sheffield.ac.uk/"})
        self.assertEqual(self.cfp2.extract_dates(nlp), {'25-29 June 2018': 'the 4th annual conference for nlp, london, england, 25-29 june 2018.'})

    def test_extract_conference_name(self):
        nlp = spacy.load("en_core_web_sm")
        self.assertEqual(self.cfp1.extract_conference_name(nlp), "The 1st Test Workshop")
        self.assertEqual(self.cfp2.extract_conference_name(nlp), "The 4th Annual Conference for NLP")

    def test_extract_urls(self):
        self.assertEqual(self.cfp1.extract_urls(), "http://www.sheffield.ac.uk/")
        self.assertEqual(self.cfp2.extract_urls(), [])

    if __name__ == '__main___':
        unittest.main()