import datetime

import dateparser

raw_dates = ["Sept 12-15", "10th October 2020", "16-18 August 2010", "17 - 19 August 2011", "October 10-11 2011", "February 15-17, 2012", "12th-15th December 2010", "January 17th-20th 2020"]

def split_dates(raw_date):
    """
    Function to split a date range into a separate start date and end date.
    Args:
        raw_date: the raw text date range to split
    Returns:
        (start_date, end_date): a tuple of DateTime objects
    """

    print (raw_date)
    start_date = None
    end_date = None

    if "-" not in raw_date:
        start_date = (dateparser.parse(raw_date))
        end_date = (dateparser.parse(raw_date))
    elif raw_date[0].isdigit():
        split = (raw_date.split("-"))
        start_date = (dateparser.parse(raw_date))
        end_date = (dateparser.parse(split[1]))
    else:
        split = (raw_date.split(" "))
        print (split)
        for data in split:
            if "-" in data:
                split_days = data.split("-")
                if len(split) == 3:
                    start_date_string = split_days[0] + " " + split[0] + " " + split[2]
                    end_date_string = split_days[1] + " " + split[0] + " " + split[2]
                else:
                    # year defaults to current year if none supplied
                    now = datetime.datetime.now()
                    start_date_string = split_days[0] + " " + split[0] + " " + str(now.year)
                    end_date_string = split_days[1] + " " + split[0] + " " + str(now.year)
                start_date = dateparser.parse(start_date_string)
                end_date = dateparser.parse(end_date_string)

    return (start_date, end_date)


for date in raw_dates:
    print (split_dates(date))

