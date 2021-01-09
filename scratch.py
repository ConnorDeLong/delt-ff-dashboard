import requests
import pandas as pd
import numpy as np

from ratelimit import limits, sleep_and_retry

pd.options.display.max_columns = None

teamId_dict = {'2019': [
    [1, "Connor DeLong", "DeLong"],
    [2, "Shawn Fulford", "Fulfi"],
    [3, "Kevin Perelstein", "K-Train"],
    [4, "Mario Bynum", "Mario"],
    [5, "Brendan Elliot", "Brendan"],
    [6, "Josh Nadeau", "Germany"],
    [7, "Kieth Kaplan", "Kieth"],
    [8, "Jonathan Kaunert", "Jon"],
    [9, "Brock Corsi", "Brock"],
    [10, "Travis Hohman", "Travis"],
    [11, "Keanu Hines", "Keanu"],
    [12, "Matt Fleisher", "Fleish"]
],
    '2020': [
        [1, "Connor DeLong", "DeLong"],
        [2, "Shawn Fulford", "Fulfi"],
        [3, "Kevin Perelstein", "K-Train"],
        [4, "Mario Bynum", "Mario"],
        [5, "Brian Solomon", "Solomon"],
        [6, "Josh Nadeau", "Germany"],
        [7, "Kieth Kaplan", "Kieth"],
        [8, "Jonathan Kaunert", "Jon"],
        [9, "Alex Darr", "Darr"],
        [10, "Travis Hohman", "Travis"],
        [11, "Keanu Hines", "Keanu"],
        [12, "Matt Fleisher", "Fleish"]
    ]
}


# @sleep_and_retry
# @limits(calls=6000, period=600)
def pull_data(year, league_id=0, dict_params={}):
    """ Returns a JSON object containing the data pulled APIs url """
    if league_id == 0:
        url = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/" + str(year)
    else:
        if year < 2020:
            url = "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/" + \
                  str(league_id) + "?seasonId=" + str(year)
        else:
            url = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/" + \
                  str(year) + "/segments/0/leagues/" + str(league_id)

    r = requests.get(url, params=dict_params)

    status_code = r.status_code

    if r.status_code == 200:
        pass
    else:
        if r.status_code == 429:
            print("429 error")

        return None

        # 2020 url returns JSON object while prior years return it in a list
    if year < 2020:
        d = r.json()[0]
    else:
        d = r.json()

    r.close()

    return d


# file_dir = 'Simulation-Work/Leagues_Found.csv'
file_dir = 'simulation_work/CheckThis.csv'

def find_leagues(startId, endId, seasonId):
    active_leagues = []

    for leagueId in range(startId, endId):
        general_league_data = pull_data(seasonId, league_id=leagueId)

        columns = ['leagueId', 'number_of_teams', 'startId', 'endId', 'seasonId', 'status_code']

        if general_league_data == None:
            pass
        else:
            num_teams = len(general_league_data['members'])

            current_league = [leagueId, num_teams, startId, endId, seasonId, 200]

            df_current_league = pd.DataFrame(data=[current_league], columns=columns)
            df_current_league.to_csv(file_dir, mode='a', header=False)

            active_leagues.append(current_league)

    df_current_league = pd.DataFrame(data=active_leagues, columns=columns)

    return df_current_league


for_start = 61647491

new = pd.DataFrame()
new.to_csv(file_dir)

get_leagues = find_leagues(for_start, for_start + 100000, 2020)
print(get_leagues)
