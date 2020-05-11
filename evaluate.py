import pandas
import argparse
import os.path

# Handles loading in files via command line arguments
def is_valid_file(parser, arg):
    """
    Given a file path, checks that the file exists.
    Args:
        arg: the path to the file
    Returns:
          str: the file path as a string (if the file does exist)
          error: an error (if the file does not exist)
    """
    if not os.path.isfile(arg):
        parser.error("ERROR: file %s does not exist." % arg) # if no file throw error
    else:
        return arg  # else return file path

parser = argparse.ArgumentParser(description='Evaluates the performance of the information extraction system, '
                                             'given a CSV output file produced by extract.py.')
parser.add_argument('-i', '-input', dest="input_file", default="results/extracted_info.csv",
                    help='a output CSV file created by extract.py. By default, will read from results/extracted_info.csv.',
                    type=lambda x: is_valid_file(parser, x))
args = parser.parse_args()

def eval_location(locations_df):
    """
    Evaluates the performance of location extraction.
    Args:
        locations_df: a Pandas DataFrame of 2 columns, one for the labelled locations and the other for the
                    detected location. Of the form: DataFrame['actual_location', 'detected_location'].
    Returns:
        bool: True if one location is a substring of the other, else False.
    """
    actual_loc = str(locations_df[0])
    detected_loc = str(locations_df[1])

    if actual_loc in detected_loc or detected_loc in actual_loc:
        return True
    return False

def eval_names(names_df):
    score = 0
    actual_names_tokens = str(names_df[0]).split()
    detected_names_tokens = str(names_df[1]).split()

    for token in detected_names_tokens:
        if token in actual_names_tokens:
            score += 1

    return score / len(actual_names_tokens)



def evaluate(results_df):
    """
    Evaluates the performance of the information extraction system. Prints the number of correct samples and the
    accuracy for each data label that was extracted.
    Args:
        results_df: a Pandas DataFrame of results, as returned in extract.py
    """
    # Write new columns for each record, True if detected information is correct else False
    results_df['correct_start_date'] = results_df['start_date'] == results_df['detected_start_date']
    results_df['correct_notification_due'] = results_df['notification_due'] == results_df['detected_notification_due']
    results_df['correct_submission_deadline'] = results_df['submission_deadline'] == results_df['detected_submission_deadline']
    results_df['correct_final_version_deadline'] = results_df['final_version_deadline'] == results_df['detected_final_version_deadline']
    results_df['correct_location'] = results_df[['location', 'detected_location']].apply(eval_location, axis=1)
    results_df['conference_name_score'] = results_df[['name', 'detected_conference_name']].apply(eval_names, axis=1)
    results_df['conference_name_match'] = results_df["conference_name_score"] == 1


    number_of_records = len(results_df.index)
    print ("NUMBER OF RECORDS: {}".format(number_of_records))

    # Print the number and accuracy of extraction for each piece of data
    print ("CONFERENCE NAME PERFORMANCE: \n SCORE: {}  \n PERFECT MATCHES: {} \n AVERAGE SCORE: {:.2%}"
       .format(results_df.conference_name_score.sum(), results_df.conference_name_match.sum(), results_df.conference_name_score.sum()/number_of_records))
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
    joint_score = (sum((results_df['correct_start_date']) & (results_df['correct_location'] & results_df['conference_name_match'] &
                                                 results_df['correct_final_version_deadline'] &
                                                 results_df['correct_notification_due'] &
                                                 results_df['correct_submission_deadline'])))
    print ("JOINT SCORE: {}, {:.2%}".format(joint_score, joint_score/number_of_records))

    key_joint_score = (sum((results_df['correct_start_date']) & (results_df['correct_location'] & results_df['conference_name_match'])))
    print ("KEY DATA JOINT SCORE: {}, {:.2%}".format(key_joint_score, key_joint_score/number_of_records))

if __name__ == "__main__":
    results_df = pandas.read_csv(args.input_file, encoding="latin-1")
    evaluate(results_df)