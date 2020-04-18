import pandas as pd
import matplotlib.pyplot as plt
import string
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

data = 'C:/Users/Richard/PycharmProjects/cfp_project/cfp_classifier/data/new_labelled_data.csv'
dataframe = pd.read_csv(data, encoding="utf-8").head(100)

dataframe.drop("filename", axis=1, inplace=True)

dataframe['word_count'] = dataframe['text'].apply(lambda x: len(str(x).split()))
newdf = dataframe['text'].apply(lambda y: (y).decode('ascii', errors='ignore'))

print (newdf)

def get_top_n_words(corpus, n=None):
    vec = CountVectorizer().fit(corpus)
    bag_of_words = vec.transform(corpus)
    sum_words = bag_of_words.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
    words_freq =sorted(words_freq, key = lambda x: x[1], reverse=True)
    return words_freq[:n]


common_words = get_top_n_words(dataframe['text'], 20)
for word, freq in common_words:
    print(word, freq)
dataframe = pd.DataFrame(common_words, columns = ['text' , 'count'])
axes = dataframe.plot(kind="bar", x="text", y="count")
axes.set_xlabel("word")
axes.set_ylabel("frequency in corpus")

plt.show()