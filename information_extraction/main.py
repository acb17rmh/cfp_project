import pprint
import pandas
import spacy
from cfp import Cfp

# Create a pandas dataframe for the CFPs
nlp = spacy.load("en_core_web_sm")
pp = pprint.PrettyPrinter(indent=4)
dataframe = pandas.read_csv(r'C:\Users\Richard\Documents\project\information_extraction\new_cfps.csv')
cfps = []

# dictionaries containing locations and dates
cfp_to_location = {}
cfp_to_dates = {}

# converts each row in the sample data into a CFP object
for row in dataframe.itertuples():
    cfp = Cfp(row[3], row[5], row[6], row[7], row[9], row[10], row[11], row[14])
    cfps.append(cfp)

for cfp in cfps:
    cfp_to_location[cfp] = cfp.extract_locations(nlp)

score = 0
accuracy = 0

# if the determined location is included in the labelled location, consider it correct
for cfp in cfp_to_location:

    # dates = str(cfp_to_dates[cfp]).strip("[]")

    # print (cfp.start_date + " - " + cfp.end_date + " ------------- " + dates)
    # Gets the first location extracted and uses that as the location (not final)
    if cfp_to_location[cfp]:
        print(cfp.location + " --------- " + cfp_to_location[cfp][0])
        if cfp_to_location[cfp][0] in cfp.location:
            score += 1
    else:
        print(cfp.name)

accuracy = score / len(cfp_to_location.keys())

print("TOTAL CORRECT LOCATIONS: " + str(score))
print("TOTAL CFPs: " + str(len(cfp_to_location.keys())))
print("ACCURACY: " + str(accuracy))
