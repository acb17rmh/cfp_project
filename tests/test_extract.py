import unittest
import extract
import spacy
import datetime
import dateparser

class TestExtract(unittest.TestCase):

    def setUp(self):
        self.locations_example = "Barcelona, New York, London"
        self.preprocess_example = "Is this a test? This is a test! I'm testing. Line break \n here."
        self.dates_example = "Dissertation submission date: 13th May 2020. Hello world!"
        self.nlp = spacy.load("en_core_web_sm")

        self.submission_date_example = datetime.datetime(2020, 5, 13, 0, 0, 0)
        self.submission_date_example2 = datetime.datetime(2016, 5, 14, 0, 0, 0)
        self.submission_date_string = "13th May 2020"

    def tearDown(self):
        pass

    def test_location(self):
        doc = self.nlp(self.locations_example)
        self.assertEqual(extract.extract_locations(doc), "Barcelona") #test case 1, Table 5.4

    def test_preprocessing(self):
        preprocessed_text = extract.preprocess_text(self.preprocess_example)

        # test case 2, Table 5.4
        self.assertEqual(preprocessed_text, ['Is this a test', 'This is a test', "I'm testing", 'Line break ', ' here.'])

    def test_date_extraction(self):
        doc = extract.preprocess_text(self.dates_example)
        date_to_sentence = extract.extract_dates(doc, self.nlp)

        # test case 3, Table 5.4
        self.assertEqual(date_to_sentence, {"13th May 2020" : "dissertation submission date: 13th may 2020"})

    def test_datetime(self):
        as_datetime = dateparser.parse(self.submission_date_string)

        self.assertFalse(self.submission_date_example == self.submission_date_example2) # test case 4, Table 5.4
        self.assertTrue(self.submission_date_example == as_datetime) # test case 5, Table 5.4

if __name__ == '__main__':
    unittest.main()
