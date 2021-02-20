from datetime import datetime
from datetime import timedelta

def create_week_number_dates(str_first_prelim_date='9/15/2020'):
    """
    - Returns dictionary containing the week numbers (value) associated with each day in
      the regular season (this actually might extend out a bit, but this should be fine)
    - Intending to use this as a way to update the app with the appropriate week
    """

    week_number_dates_dict = {}

    date_prelim_date = datetime.strptime(str_first_prelim_date, "%m/%d/%Y").date()
    for week_number in range(1, 15):
        for day_number in range(1, 8):
            str_prelim_date = date_prelim_date.strftime("%m/%d/%Y")
            week_number_dates_dict[str_prelim_date] = week_number

            date_prelim_date += timedelta(days=1)

    return week_number_dates_dict

def get_current_week_number():

    week_number_dates_dict = create_week_number_dates()

    current_date = datetime.now().date()

    # Creating this as a default
    current_week_number = 13

    current_date_str = current_date.strftime("%m/%d/%Y")
    for key, value in week_number_dates_dict.items():
        if current_date_str == key:
            current_week_number = value
            break

    return current_week_number

