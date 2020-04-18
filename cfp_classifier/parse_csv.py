import pandas, os, csv, json, numpy
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

df1 = pandas.read_csv("data/corpus.csv", encoding="latin-1").fillna(' ')

df_emails = df1.loc[df1['class'] == "email"]
print (df_emails)

df_cfps = df1.loc[df1['class'] == "cfp"]
print (df_cfps)


def preprocess_text(text):
    """
    Function to preprocess input texts before being vectorized. Performs tokenisation and stopword removal,
    and removes punctuation from the text.

    Args:
        text: the input text to be preprocessed
    Returns:
        list: a string of preprocessed text
    """
    # get the stoplist from the NLTK corpus
    stoplist = (stopwords.words("english"))
    stoplist.append('the')
    # uses NLTK to tokenise the input email
    text = word_tokenize(text)
    # removes any punctuation or words if they are in the stoplist
    text_words = [word for word in text if word not in stoplist]
    text_as_sent = (" ").join(text_words)
    return text_as_sent


def get_top_n_words(corpus, n=None):
    text = corpus.apply(preprocess_text)
    vec = CountVectorizer().fit(corpus)
    bag_of_words = vec.transform(corpus)
    sum_words = bag_of_words.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
    words_freq = sorted(words_freq, key = lambda x: x[1], reverse=True)
    return words_freq[:n]

common_words = get_top_n_words(df1['cfp_text'], 10)
for word, freq in common_words:
    print(word, freq)

dataframe = pandas.DataFrame(common_words, columns=['cfp_text', 'count'])
axes = dataframe.plot(kind="bar", x="cfp_text", y="count")
axes.set_xlabel("word")
axes.set_ylabel("frequency of corpus")
axes.set_title("Most frequent words in corpus with no stopword removal")

plt.show()

