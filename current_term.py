import datetime
import requests
import json
import pandas as pd
import bs4
import re

# Call return_current_term() to get the current term name

keys = ["classes+begin", "examinations"]
year_standardization = {
    "Jan." : "01",
    "Feb." : "02",
    "Mar." : "03",
    "Apr." : "04",
    "May" : "05",
    "June" : "06",
    "Jul." : "07",
    "Aug." : "08",
    "Sep." : "09",
    "Oct." : "10",
    "Nov." : "11",
    "Dec." : "12",
}
semester_standardization = {
    "Fall" : "FA",
    "Winter" : "WN",
    "Spring/Summer" : "SP/SU",
} 

def clean_date_from_new_terms(dates, last_term_year):
    new_date = {
        "start" : {
            "month" : "",
            "day" : int("".join(re.findall(r'\d+', dates[0]))),
            "year" : last_term_year
        },
        "end" : {
            "month" : "",
            "day" : int("".join(re.findall(r'\d+', dates[1]))),
            "year" : last_term_year
        }
    }
    for date in dates:
        for key in year_standardization:
            if key in date:
                if new_date["start"]["month"] == "":
                    new_date["start"]["month"] = year_standardization[key]
                    print(new_date["start"]["month"])   
                else:
                    new_date["end"]["month"] = year_standardization[key]
                    print (new_date["end"]["month"])
    return new_date
        


def get_new_terms(last_term_id):
    term_start_end_dates = []
    new_term_id = last_term_id + 1
    url = f"https://ro.umich.edu/calendars?term={new_term_id}&type%5B107%5D=107&keys={keys[0]}"

    response = requests.get(url)
    for key in keys:
        url = f"https://ro.umich.edu/calendars?term={new_term_id}&type%5B107%5D=107&keys={key}"
        response = requests.get(url)

        pattern = r'<h5 class="text-2xl md:text-4xl leading-normal font-bold font-secondary pt-8 mb-2 border-t border-gray-200 w-full">\s*(.*?)\s*</h5>'
        pattern2 = r'<h3 class="md:text-275">\s*(.*?)\s*</h3>'

        # Search for the pattern and extract the text
        match = re.search(pattern, response.content.decode('utf-8'))
        match2 = re.search(pattern2, response.content.decode('utf-8'))

        if match:
            extracted_text = match.group(1)
            term_start_end_dates.append(extracted_text[-7:])
            print(extracted_text[-7:])
        else:
            print("Text not found.")
        if match2:
            new_term_name = match2.group(1)

            for key, replacement in semester_standardization.items():
                if key in new_term_name:
                    new_term_name = new_term_name.replace(key, replacement)
                    print(new_term_name)
    return [term_start_end_dates, new_term_name]


def return_current_term():
# create terms.csv with 3 columns (term_id, term_name, term_start_date, term_end_date)
# check current date within the last term start and end date
    check_csv = pd.read_csv("terms.csv")
    last_term_id = check_csv["term_id"].iloc[-1]
    last_term_start_date = check_csv["term_start_date"].iloc[-1]
    last_term_end_date = check_csv["term_end_date"].iloc[-1]
    last_term_end_date = datetime.datetime.strptime(last_term_end_date, "%Y-%m-%d")
    while datetime.datetime.now() > last_term_end_date:
        last_term_id = check_csv["term_id"].iloc[-1]
        last_term_start_date = check_csv["term_start_date"].iloc[-1]
        last_term_end_date = check_csv["term_end_date"].iloc[-1]
        if isinstance(last_term_end_date, str):
            last_term_end_date = datetime.datetime.strptime(last_term_end_date, "%Y-%m-%d")
        else:
            last_term_end_date = last_term_end_date.to_pydatetime()
        if datetime.datetime.now() > last_term_end_date:
            new_terms = get_new_terms(last_term_id)
            new_dates = clean_date_from_new_terms(new_terms[0], last_term_end_date.year)
            # change new dates to datetime
            # extract years from new_terms[1] (the only integers in the string)
            years = re.findall(r'\d+', new_terms[1])
            years = "".join(years)
            new_dates["start"] = datetime.datetime(int(years), int(new_dates["start"]["month"]), new_dates["start"]["day"]).strftime("%Y-%m-%d")
            new_dates["end"] = datetime.datetime(int(years), int(new_dates["end"]["month"]), new_dates["end"]["day"]).strftime("%Y-%m-%d")
            new_term_id = last_term_id + 1
            new_term_name = new_terms[1]
            new_row = {
                "term_id": new_term_id,
                "term_name": new_term_name,
                "term_start_date": new_dates["start"],
                "term_end_date": new_dates["end"]
            }

            # Convert the dictionary to a DataFrame and use pd.concat to add it as a new row
            check_csv.loc[len(check_csv)] = new_row    # write new csv to terms.csv
    check_csv.to_csv("terms.csv", index=False)
    return check_csv["term_name"].iloc[-1]