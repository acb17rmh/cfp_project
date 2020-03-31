import csv
import os
import pandas

"""
Script to convert source Enron .txt files into a CSV file to be loaded by the classifier.
"""

def get_csv_data(directory):
    data = []
    files_list = os.listdir(directory)
    print(files_list)
    for file in files_list:
        print(file)
        file = directory + "/" + file
        email = open(file, 'r', encoding="utf8").read()
        data.append((file, email.encode("utf-8")))
    return data


with open('enron.csv', 'w') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerows(get_csv_data("enron-bass-e"))

csvFile.close()

files_list = os.listdir("../source_data/wikicfp/raw_text_files")
data = pandas.DataFrame(files_list)
data.to_csv('wikicfp.csv', index=False)

