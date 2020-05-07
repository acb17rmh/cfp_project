import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.utils import shuffle
import matplotlib.pyplot as plt
from sklearn.decomposition import TruncatedSVD
from sklearn import svm

dataframe = shuffle(pd.read_csv("data/corpus.csv", encoding="latin-1").fillna(" "))
new_df = dataframe[['text', 'class_label']].copy()

"""
email_df = pd.read_pickle("data/personal_emails")
df2 = email_df[['text', 'class_label']].copy()
new_df = new_df.append(df2)

"""
print (new_df)


data_train, data_test = train_test_split(new_df, random_state=20, train_size=0.9, shuffle=True, stratify=new_df['class_label'])
vectorizer = CountVectorizer(stop_words=stopwords.words("english"), lowercase=True)
train_counts = vectorizer.fit_transform(data_train['text'])
test_counts = vectorizer.transform(data_test['text'])

classifierNB = svm.SVC()
targets = data_train["class_label"]
classifierNB.fit(train_counts, data_train["class_label"])
predictionsNB = classifierNB.predict(test_counts)

feature_array = vectorizer.get_feature_names()
print('Top frequency in train set: \n', sorted(list(zip(vectorizer.get_feature_names(),
                                       train_counts.sum(0).getA1())),
                              key=lambda x: x[1], reverse=True)[:10])
print('Top frequency in test set: \n', sorted(list(zip(vectorizer.get_feature_names(),
                                       test_counts.sum(0).getA1())),
                              key=lambda x: x[1], reverse=True)[:10])

print(classification_report(data_test["class_label"], predictionsNB, digits=6))
print("ACCURACY: {:.2%}".format(accuracy_score(data_test["class_label"], predictionsNB)))
# 10-fold cross validation score
cross_validation_scores = cross_val_score(classifierNB, test_counts, data_test['class_label'], cv=10)
print(cross_validation_scores.mean())

# Add the new labels to the DataFrame and save as an HTML document
predictions_df = pd.DataFrame(predictionsNB)
data_test["prediction"] = predictions_df.values

cm = confusion_matrix(data_test["class_label"], predictionsNB)
print (cm)

misclassifieds = data_test.loc[data_test['prediction'] != data_test["class_label"]]
filename = "results/NEW_classifier_results{}.docs"
misclassifieds.to_html(filename)

