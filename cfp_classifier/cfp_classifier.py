import pandas as pd
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
import time


class CFPClassifier():

    def __init__(self):
        self.data_train, self.data_test = self.load_data("data/new_labelled_data.csv")
        self.train_counts, self.test_counts = self.vectorize()
        self.vectorizer
        self.classifier = self.train_classifier()

    def load_data(self, data, test_size=0.3):
        """
        Function to load a labelled dataset from a CSV file, and split it into a training set and a testing set.

        Args:
            data: the CSV file to be loaded
            test_size: If float, should be between 0.0 and 1.0 and represent the proportion of the dataset to include in the test split.
                       If int, represents the absolute number of test samples.
                       If None, the value is set to the complement of the train size.
                       If train_size is also None, it will be set to 0.25.
        Returns:
            (DataFrame, DataFrame): a tuple of Pandas DataFrames, where the first DataFrame is the training data,
                                    and the second DataFrame is the training data.
        """
        dataframe = pd.read_csv(data).dropna().head(1000)
        data_train, data_test = train_test_split(dataframe, test_size=test_size)
        return data_train, data_test

    def vectorize(self):
        """
        Function to train the classifier on the data provided.
        Returns:
            (sparse matrix, sparse matrix): a tuple of sparse matrices, where the first matrix is the document-term
                                            matrix for the training data, and the second matrix is the document-term
                                            matrix for the testing data.
        """
        vectorizer = CountVectorizer(analyzer=preprocess_text)
        self.vectorizer = vectorizer
        train_counts = vectorizer.fit_transform(self.data_train['text'])
        test_counts = vectorizer.transform(self.data_test['text'])
        return train_counts, test_counts

    def train_classifier(self):
        """
        Function to train the classifier on the data provided.
        Returns:
            MultinomialNB: a trained instance of an sklearn MultinomialNB object.
        """
        classifier = MultinomialNB()
        targets = self.data_train["class"]
        classifier.fit(self.train_counts, targets)
        return classifier

    def classify_text(self, input_text_list):
        """
        Function to classify a set of input sets.
        Args:
            input_text_list: a list of strings to be classified.
        Returns:
            list: a list of predicted labels corresponding to the input list's elements.
        """
        input_counts = self.vectorizer.transform(input_text_list)
        predictions = self.classifier.predict(input_counts)
        return predictions

    def evaluate(self):
        """
        Function to run the trained classifier on the test set of data and evaluate its performance.
        Also exports the results of the evaluation to an HTML document, which is saved in the /results subfolder.
        """
        # Run the classifier on test set and report performance
        test_counts, test_set = self.test_counts, self.data_test
        predictions = self.classifier.predict(test_counts)
        print(classification_report(test_set["class"], predictions))
        print("ACCURACY: {:.2%}".format(accuracy_score(test_set["class"], predictions)))

        # Add the new labels to the DataFrame and save as an HTML document
        predictions_df = pd.DataFrame(predictions)
        test_set["prediction"] = predictions_df.values
        filename = "results/classifier_results{}.html".format(time.time())
        test_set.to_html(filename)
        print("Saved results to file {}".format(filename))

def preprocess_text(text):
    """
    Function to preprocess input texts before being vectorized. Performs tokenisation and stopword removal,
    and removes punctuation from the text.

    Args:
        text: the input text to be preprocessed
    Returns:
        list: a list of words in the text
    """
    # get the stoplist from the NLTK corpus
    stoplist = (stopwords.words("english"))
    # uses NLTK to tokenise the input email
    text = word_tokenize(text)
    # removes any punctuation or words if they are in the stoplist
    text_words = [word for word in text if word not in stoplist and word not in string.punctuation]
    return text_words

if __name__ == "__main__":
    cfp_classifier = CFPClassifier()
    cfp_classifier.evaluate()
