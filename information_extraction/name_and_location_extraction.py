import pandas
import spacy
from cfp import Cfp
import re
import time

# Create a pandas dataframe for the CFPs
nlp = spacy.load("en_core_web_sm")
dataframe = pandas.read_csv("data/wikicfp_sorted.csv")
cfps = []

CONFERENCE_NAME_REGEX = re.compile("|".join(["workshop", "conference", "meeting", "theme", "international"]), re.IGNORECASE)
ORDINAL_REGEX = re.compile("|".join(["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "nineth",
                                     "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th"]), re.IGNORECASE)
CONJUNCTION_REGEX = re.compile("|".join(["conjunction", "assosciate", "joint", "located"]), re.IGNORECASE)
URL_REGEX = re.compile("|".join(["http", ".co.uk", ".com"]), re.IGNORECASE)
WEB_URL_REGEX = re.compile(r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))""")

# dictionaries containing locations and dates
cfp_to_conference_name = {}
cfp_to_location = {}
cfp_to_url = {}

conference_name_score = 0
location_score = 0
url_score = 0

# converts each row in the sample data into a CFP object
# if the determined location is included in the labelled location, consider it correct


for row in dataframe.itertuples():
    cfp = Cfp(row[3], row[5], row[6], row[7], row[9], row[10], row[11], row[14], str(row[13]))
    cfp_to_conference_name[cfp] = cfp.extract_conference_name(nlp, CONFERENCE_NAME_REGEX, ORDINAL_REGEX,
                                                                   CONJUNCTION_REGEX)
    cfp_to_location[cfp] = cfp.extract_locations(nlp)
    cfp_to_url[cfp] = cfp.extract_urls(WEB_URL_REGEX)
    cfp_dict = cfp.as_dict()


    if cfp_to_conference_name[cfp]:
        detected_conference_name = cfp_to_conference_name[cfp]
        if detected_conference_name in cfp.name or cfp.name in detected_conference_name:
            conference_name_score += 1

    # Gets the first location extracted and uses that as the location (not final)
    if cfp_to_location[cfp]:
        detected_location = cfp_to_location[cfp][0]
        if detected_location in cfp.location:
            location_score += 1

    if cfp_to_url[cfp]:
        detected_url = cfp_to_url[cfp][0]
        if detected_url in cfp.url or cfp.url in detected_url:
            url_score += 1

    cfp_dict['detected_location'] = detected_location
    cfp_dict['detected_conference_name'] = detected_conference_name
    cfp_dict['detected_url'] = detected_url
    cfps.append(cfp_dict)

conference_name_accuracy = conference_name_score / len(cfp_to_conference_name.keys())
location_accuracy = location_score / len(cfp_to_location.keys())
url_accuracy = url_score / len(cfp_to_url.keys())

# write result to an HTML page
results_dataframe = pandas.DataFrame(cfp for cfp in cfps)
filename = "results/name_and_location_results{}.html".format(time.time())
results_dataframe.to_html(filename)
print ("Saved results to file {}".format(filename))

print("TOTAL CORRECT CONFERENCE NAMES: " + str(conference_name_score))
print("ACCURACY: " + str(conference_name_accuracy))

print("TOTAL CORRECT LOCATIONS: " + str(location_score))
print("ACCURACY: " + str(location_accuracy))

print("TOTAL CORRECT URLS: " + str(url_score))
print("ACCURACY: " + str(url_accuracy))

print("TOTAL CFPs: " + str(len(cfp_to_conference_name.keys())))