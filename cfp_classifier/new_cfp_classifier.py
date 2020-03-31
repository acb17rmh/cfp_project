import pandas as pd
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import  accuracy_score
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
import time

class CFPClassifier():

    def __init__(self):
        self.data_train, self.data_test = self.load_data("data/new_labelled_data.csv")
        self.train_counts, self.test_counts = self.vectorize()
        self.vectorizer
        self.classifier = self.train_classifier()

    def load_data(self, data):
        dataframe = pd.read_csv(data).dropna()
        data_train, data_test = train_test_split(dataframe, test_size=0.25)
        return data_train, data_test

    def vectorize(self):
        vectorizer = CountVectorizer(analyzer=preprocess_text)
        self.vectorizer = vectorizer
        train_counts = vectorizer.fit_transform(self.data_train['text'])
        test_counts = vectorizer.transform(self.data_test['text'])
        return train_counts, test_counts

    def train_classifier(self):
        classifier = MultinomialNB()
        targets = self.data_train["class"]
        classifier.fit(self.train_counts, targets)
        return classifier

    def classify_text(self, input_text_array):
        input_counts = self.vectorizer.transform(input_text_array)
        predictions = self.classifier.predict(input_counts)
        return predictions

    def evaluate(self):
        test_counts, test_set = self.test_counts, self.data_test
        predictions = self.classifier.predict(test_counts)
        print(classification_report(test_set["class"], predictions))
        print("ACCURACY: {:.2%}".format(accuracy_score(test_set["class"], predictions)))
        predictions_df = pd.DataFrame(predictions)
        test_set["prediction"] = predictions_df.values
        filename = "results/classifier_results{}.html".format(time.time())
        test_set.to_html(filename)
        print("Saved results to file {}".format(filename))

def preprocess_text(text):
    # uses NLTK to tokenise the input email
    text = word_tokenize(text)
    # removes any punctuation or words if they are in the stoplist
    text_words = [word for word in text if word not in stoplist and word not in string.punctuation]
    return text_words

# get the stoplist from the NLTK corpus
stoplist = (stopwords.words("english"))

cfp_classifier = CFPClassifier()
cfp_classifier.evaluate()
