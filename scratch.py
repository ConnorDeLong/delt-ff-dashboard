import requests
import pandas as pd
import numpy as np

from ratelimit import limits, sleep_and_retry

pd.options.display.max_columns = None

slotcodes = {
    0: 'QB', 2: 'RB', 4: 'WR',
    6: 'TE', 16: 'Def', 17: 'K',
    20: 'Bench', 21: 'IR', 23: 'Flex'
}


@sleep_and_retry
@limits(calls=6000, period=600)
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

    #         return None

    # 2020 url returns JSON object while prior years return it in a list
    if year < 2020:
        d = r.json()[0]
    else:
        d = r.json()

    r.close()

    return [d, status_code]

file = '/home/cdelong/python_projects/ff_web_app/delt_ff_standings/Leagues_Found.csv'

leagues_found = pd.read_csv(file)

leagueIds = list(leagues_found['leagueId'])

status_codes = []
for league in leagueIds:
    status_code = pull_data(2020, league_id=league)[1]

    status_codes.append([league, status_code])

d_status_codes = pd.DataFrame(status_codes, columns=['leagueId', 'status_codes'])

new_file = '/home/cdelong/python_projects/ff_web_app/delt_ff_standings/temp.csv'

d_status_codes.to_csv(new_file)
