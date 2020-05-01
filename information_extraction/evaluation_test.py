import pandas

# Load extraction data
results_df = pandas.read_csv('NEW_RESULTS/new_results1588289488.4452426.csv', encoding="latin-1")

def eval_location(dataframe):
    actual_loc = str(dataframe[0])
    detected_loc = str(dataframe[1])

    if actual_loc in detected_loc or detected_loc in actual_loc:
        return True
    return False

# Write new columns for each record, True if detected information is correct else False
results_df['correct_start_date'] = results_df['start_date'] == results_df['detected_start_date']
results_df['correct_notification_due'] = results_df['notification_due'] == results_df['detected_notification_due']
results_df['correct_submission_deadline'] = results_df['submission_deadline'] == results_df['detected_submission_deadline']
results_df['correct_final_version_deadline'] = results_df['final_version_deadline'] == results_df['detected_final_version_deadline']
results_df['correct_location'] = results_df[['location', 'detected_location']].apply(eval_location, axis=1)
results_df['correct_conference_name'] = results_df[['name', 'detected_conference_name']].apply(eval_location, axis=1)

number_of_records = len(results_df.index)
print (number_of_records)

# Print the number and accuracy of extraction for each piece of data
print ("CONFERENCE NAME PERFORMANCE: \n CORRECT RECORDS {} \n ACCURACY {:.2%}"
       .format(results_df.correct_conference_name.sum(), results_df.correct_conference_name.sum()/number_of_records))
print ("LOCATION PERFORMANCE: \n CORRECT RECORDS {} \n ACCURACY {:.2%}"
       .format(results_df.correct_location.sum(), results_df.correct_location.sum()/number_of_records))
print ("START DATE PERFORMANCE: \n CORRECT RECORDS {} \n ACCURACY {:.2%}"
       .format(results_df.correct_start_date.sum(), results_df.correct_start_date.sum()/number_of_records))
print ("SUBMISSION DEADLINE PERFORMANCE: \n CORRECT RECORDS {} \n ACCURACY {:.2%}"
       .format(results_df.correct_submission_deadline.sum(), results_df.correct_submission_deadline.sum()/number_of_records))
print ("NOTIFICATION DUE PERFORMANCE: \n CORRECT RECORDS {} \n ACCURACY {:.2%}"
       .format(results_df.correct_notification_due.sum(), results_df.correct_notification_due.sum()/number_of_records))
print ("FINAL VERSION DEADLINE PERFORMANCE: \n CORRECT RECORDS {} \n ACCURACY {:.2%}"
       .format(results_df.correct_final_version_deadline.sum(), results_df.correct_final_version_deadline.sum()/number_of_records))

# Print joint accuracies (key data and all data)
print (sum((results_df['correct_start_date']) & (results_df['correct_location'] & results_df['correct_conference_name'] &
                                                 results_df['correct_final_version_deadline'] &
                                                 results_df['correct_notification_due'] &
                                                 results_df['correct_submission_deadline'])))

print (sum((results_df['correct_start_date']) & (results_df['correct_location'] & results_df['correct_conference_name'])))