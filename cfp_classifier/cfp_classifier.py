import pandas as pd
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score, f1_score, precision_score
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelBinarizer, LabelEncoder

"""
Naive bayes classifier for CFP emails.
@author: Richard Hindes
@data: 18/11/2019
@resource: labelled_data.csv - a csv file containing each email and its label
"""

"""
@function preprocess_text

Given an input string, removes commas, punctuation and any words
that are in the stoplist.

@param text - text as a string to be pre-processed
@return text_words - a tokenised list of words in the input
"""


def preprocess_text(text):
    # uses NLTK to tokenise the input email
    text = word_tokenize(text)
    # removes any punctuation or words if they are in the stoplist
    text_words = [word for word in text if word not in stoplist and word not in string.punctuation]
    return text_words


# get the stoplist from the NLTK corpus
stoplist = (stopwords.words("english"))

# load in the labelled data
# TODO: ability to specify own dataset from the command line
data = pd.read_csv('data/new_labelled_data.csv').head(100).dropna()

# Splits the text into a feature vector where each feature is a word
email_vectors = CountVectorizer(analyzer=preprocess_text).fit_transform(data['text'])

"""
Splits the data into 4 sets:
data_training: training data
data_test: testing data
label_train: class labels for all the training data
label_test: class labels for all the testing data
test_size parameter specifies that 25% of the data is used for testing, 75% used for training
"""

data_train, data_test, label_train, label_test = train_test_split(email_vectors, data['class'], test_size=0.25,
                                                                  random_state=0)


# Initilialises the naive bayes classifier and supplies it with the training data
# Which is then used to trjain the classifier

# classifier = svm.SVC(gamma = "scale")
classifier = MultinomialNB()
classifier.fit(data_train, label_train)

# Predict the class (cfp or email) of the testing data
predictions = classifier.predict(data_test)

# print accuracy, recall, precision and f-measure
print("ACCURACY: " + str(accuracy_score(label_test, predictions)))
print("RECALL: " + str(recall_score(label_test, predictions, pos_label="cfp")))
print("PRECISION " + str(precision_score(label_test, predictions, pos_label="cfp")))
print("F-MEASURE " + str(f1_score(label_test, predictions, pos_label="cfp")))

# plot confusion matrix as heatmap
confusion_matrix = confusion_matrix(predictions, label_test)
print(confusion_matrix)

# 10-fold cross validation score
cross_validation_scores = cross_val_score(classifier, email_vectors, data['class'], cv=10)
print(cross_validation_scores.mean())

"""
# load CFP csv
test_df = pd.read_csv('../information_extraction/data/wikicfp_sorted.csv')
test_df = test_df['description']
vectorizer = CountVectorizer()
test_dataset = vectorizer.transform(test_df)
print (classifier.predict(test_dataset))
"""

"""
# Code for plotting the confusion matrix
axes = plt.subplot()
sns.heatmap(confusion_matrix, annot=True, ax=axes, cmap="Blues", fmt="g")
axes.set_xlabel('True labels')
axes.set_ylabel('Predicted labels')
axes.set_title('Confusion Matrix')
axes.xaxis.set_ticklabels(['CFP', 'non CFP'])
axes.yaxis.set_ticklabels(['CFP', 'non CFP'])
plt.show()
"""