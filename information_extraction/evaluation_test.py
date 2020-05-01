from __future__ import unicode_literals, print_function

import dateparser
import pandas
import pprint
import re
import spacy
from cfp import Cfp
import time

# Load extraction datas
results_df = pandas.read_csv('NEW_RESULTS/new_results1588289488.4452426.csv', encoding="latin-1")

results_df['correct_start_date'] = results_df['start_date'] == results_df['detected_start_date']
results_df['correct_notification_due'] = results_df['notification_due'] == results_df['detected_notification_due']
results_df['correct_submission_deadline'] = results_df['submission_deadline'] == results_df['detected_submission_deadline']
results_df['correct_final_version_deadline'] = results_df['final_version_deadline'] == results_df['detected_final_version_deadline']






number_of_records = len(results_df.index)



print (number_of_records)
print ("START DATE PERFORMANCE: \n CORRECT RECORDS {} \n ACCURACY {:.2%}"
       .format(results_df.correct_start_date.sum(), results_df.correct_start_date.sum()/number_of_records))
print ("SUBMISSION DEADLINE PERFORMANCE: \n CORRECT RECORDS {} \n ACCURACY {:.2%}"
       .format(results_df.correct_submission_deadline.sum(), results_df.correct_submission_deadline.sum()/number_of_records))
print ("NOTIFICATION DUE PERFORMANCE: \n CORRECT RECORDS {} \n ACCURACY {:.2%}"
       .format(results_df.correct_notification_due.sum(), results_df.correct_notification_due.sum()/number_of_records))
print ("FINAL VERSION DEADLINE PERFORMANCE: \n CORRECT RECORDS {} \n ACCURACY {:.2%}"
       .format(results_df.correct_final_version_deadline.sum(), results_df.correct_final_version_deadline.sum()/number_of_records))
