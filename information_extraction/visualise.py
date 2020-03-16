import pandas
import random
import spacy
from cfp import Cfp
from spacy import displacy

"""
Script to display a random CFP from the corpus and show its NER tags.
The NER visualiser will be served on localhost:5000.
"""

nlp = spacy.load("en_core_web_sm")
dataframe = pandas.read_csv('data/wikicfp_sorted.csv').head(100)
cfps = []

for row in dataframe.itertuples():
    cfp = Cfp(row[3], row[5], row[6], row[7], row[8], row[9], row[10], row[14])
    cfps.append(cfp)

random_cfp = random.choice(cfps)
document = nlp(random_cfp.cfp_text)
displacy.serve(document, style="ent")
