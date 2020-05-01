import pandas as pd
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.utils import shuffle
import pickle
import joblib
import time


class CFPClassifier():

    def __init__(self, corpus, dump_model=False, model_name="trained_model.sav", vectorizer_name="vectorizer.sav"):
        """
        Function to load a labelled dataset from a CSV file, and split it into a training set and a testing set.

        Args:
            corpus: the CSV file corpus upon which the classifier will be trained against.
            dump_model: boolean value, if set to True, the classifier will be dumped as .sav files.
            model_name: if dump_model is set to true, the model will be saved with this parameter as a filename.
            vectorizer_name: if dump_model is set to true, the vectorizer will be saved with this parameter as a filename.
        Returns:
            CFPClassifier: an instance of a CFPClassifier object
        """
        self.data_train, self.data_test = self.load_data(corpus)
        self.train_counts, self.test_counts = self.vectorize()
        self.vectorizer
        self.dump_model = dump_model
        self.model_name = model_name
        self.vectorizer_name = vectorizer_name
        self.classifier = self.train_classifier(dump_model)

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
        dataframe = shuffle(pd.read_csv(data, encoding="latin-1").fillna(" "))
        new_df = dataframe[['text', 'class']].copy()
        new_df.to_html("results/new_df.docs")
        data_train, data_test = train_test_split(new_df, test_size=test_size)
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

    def train_classifier(self, dump_model=False, model_name="trained_model.sav", vectorizer_name="vectorizer.sav"):
        """
        Function to train the classifier on the data provided.

        Args:
            dump_model: if set to True, will dump the trained classifier and vectorizer as .sav files.
            model_name: if dump_model is set to true, the model will be saved with this parameter as a filename.
            vectorizer_name: if dump_model is set to true, the vectorizer will be saved with this parameter as a filename.
        Returns:
            MultinomialNB: a trained instance of an sklearn MultinomialNB object.
        """
        classifier = MultinomialNB()
        targets = self.data_train["class"]
        classifier.fit(self.train_counts, targets)
        if self.dump_model:
            joblib.dump(self.vectorizer, self.vectorizer_name)
            joblib.dump(classifier, self.model_name)
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

    def evaluate(self, model_path=None, vectorizer_path=None):
        """
        Function to run the trained classifier on the test set of data and evaluate its performance.
        Also exports the results of the evaluation to an HTML document, which is saved in the /results subfolder.

        Args:
            model_path: if you want to use a dumped model, set this parameter to that model's file path
            model_path: if you want to use a dumped vectorizer, set this parameter to that vectorizer's file path
        """
        # Run the classifier on test set and report performance
        test_counts, test_set = self.test_counts, self.data_test
        if model_path:
            print ("Using trained model '{}' and vectorizer '{}'".format(model_path, vectorizer_path))
            loaded_model = joblib.load(model_path)
            loaded_vectorizer = joblib.load(vectorizer_path)
            test_counts = loaded_vectorizer.transform(self.data_test['text'])
            predictions = loaded_model.predict(test_counts)
        else:
            predictions = self.classifier.predict(test_counts)
        print(classification_report(test_set["class"], predictions, digits=6))
        print("ACCURACY: {:.2%}".format(accuracy_score(test_set["class"], predictions)))

        # Add the new labels to the DataFrame and save as an HTML document
        predictions_df = pd.DataFrame(predictions)
        test_set["prediction"] = predictions_df.values
        filename = "results/classifier_results{}.docs".format(time.time())
        test_set.to_html(filename)
        print("Saved results to file {}".format(filename))

        # plot confusion matrix as heatmap
        conf = confusion_matrix(predictions, test_set["class"])
        print(conf)

        # 10-fold cross validation score
        cross_validation_scores = cross_val_score(self.classifier, test_counts, test_set['class'], cv=10)
        print(cross_validation_scores.mean())

    """
    def scatter_plot(self):
        svd = TruncatedSVD(n_components=2).fit(self.train_counts)
        data2D = svd.transform(self.train_counts)
        plt.scatter(data2D[:, 0], data2D[:, 1])
        plt.show()
    """

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
    cfp_classifier = CFPClassifier("data/corpus.csv")
    cfp_classifier.evaluate()
