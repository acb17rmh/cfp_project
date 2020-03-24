import pprint
import pandas
import spacy
from cfp import Cfp

# Create a pandas dataframe for the CFPs
nlp = spacy.load("en_core_web_sm")
pp = pprint.PrettyPrinter(indent=4)
dataframe = pandas.read_csv("data/wikicfp_sorted.csv")
cfps = []

# dictionaries containing locations and dates
cfp_to_location = {}
cfp_to_dates = {}

score = 0
accuracy = 0

# converts each row in the sample data into a CFP object
# if the determined location is included in the labelled location, consider it correct
for row in dataframe.itertuples():
    cfp = Cfp(row[3], row[5], row[6], row[7], row[9], row[10], row[11], row[14])
    cfp_to_location[cfp] = cfp.extract_locations(nlp)
    cfp_dict = cfp.as_dict()

    # Gets the first location extracted and uses that as the location (not final)
    if cfp_to_location[cfp]:
        detected_location = cfp_to_location[cfp][0]
        if detected_location in cfp.location:
            score += 1

    cfp_dict['detected_location'] = detected_location
    cfps.append(cfp_dict)

accuracy = score / len(cfp_to_location.keys())

results_dataframe = pandas.DataFrame(cfp for cfp in cfps)
results_dataframe.to_html("results/location_results.html")

print("TOTAL CORRECT LOCATIONS: " + str(score))
print("TOTAL CFPs: " + str(len(cfp_to_location.keys())))
print("ACCURACY: " + str(accuracy))
