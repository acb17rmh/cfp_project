import unittest
import pandas
from cfp_classifier import CFPClassifier

class TestClassifier(unittest.TestCase):

    def setUp(self):
        self.classifier = CFPClassifier("../data/corpus.csv")

    def tearDown(self):
        pass

    def test_load_data(self):
        all_data = pandas.read_csv("../data/corpus.csv")
        data_train = self.classifier.data_train
        data_test = self.classifier.data_test

        self.assertGreater(all_data.shape[0], 0) #test case 1, Table 5.4
        self.assertEqual(data_train.shape[0] + data_test.shape[0], all_data.shape[0]) #test case 2, Table 5.4
        self.assertEqual((pandas.merge(data_train, data_test, how='inner')).empty, True) #test case 3, Table 5.4

    def test_preprocessing(self):
        features = self.classifier.vectorizer.get_feature_names()
        words_with_capitals = [x.isupper() for x in features]
        stopwords = self.classifier.vectorizer.get_stop_words()

        self.assertEqual(any(words_with_capitals), False) #test case 4, Table 5.4
        self.assertEqual(list(set(features) & set(stopwords)), []) #test case 5, Table 5.4

if __name__ == '__main__':
    unittest.main()
