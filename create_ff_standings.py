# https://opensource.com/article/18/1/step-step-guide-git
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta

def pull_data(year, league_id=0, dict_params=None):
    """ Returns a JSON object containing the data pulled APIs url """
    if dict_params is None:
        dict_params = {}
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

    # 2020 url returns JSON object while prior years return it in a list
    if year < 2020:
        d = r.json()[0]
    else:
        d = r.json()

    r.close()

    return d

def create_matchup_df(matchup_data, playoff_week_start=14):
    """ Returns a week/matchup level dataframe containing the total scores of each team
        Note that this requires the mMatchup filtered data
    """

    data = []

    for i, matchup_dict in enumerate(matchup_data['schedule']):
        #     print(check.keys(), "AND ", choose_data['schedule'][i]['matchupPeriodId'])

        week_number = matchup_dict['matchupPeriodId']

        # bye weeks cause the "away" key to be missing for the team with a bye
        try:
            teamId_away = int(matchup_dict['away']['teamId'])
            score_away = matchup_dict['away']['totalPoints']
        except KeyError:
            teamId_away = None
            score_away = None

        # applying this here just in case
        try:
            teamId_home = int(matchup_dict['home']['teamId'])
            score_home = matchup_dict['home']['totalPoints']
        except KeyError:
            teamId_home = None
            score_home = None

        data.append([week_number, teamId_away, score_away, teamId_home, score_home])

    df_matchup = pd.DataFrame(data, columns=['week_number', 'teamId_away', 'score_away',
                                             'teamId_home', 'score_home']
                              )

    df_matchup['week_type'] = ['Regular' if w <= playoff_week_start else 'Playoffs' \
                               for w in df_matchup['week_number']]

    return df_matchup

def expand_matchup_data(matchup_data):
    """ Expands data to the week/team level """

    # create dataset from the perspective of the away team
    df_away_data = matchup_data.copy()
    df_away_data.rename(columns={'teamId_away': 'teamId',
                                 'score_away': 'score',
                                 'teamId_home': 'teamId_opp',
                                 'score_home': 'score_opp'
                                 },
                        inplace=True)
    df_away_data['home_or_away'] = 'away'

    # create dataset from the perspective of the home team
    df_home_data = matchup_data.copy()
    df_home_data.rename(columns={'teamId_home': 'teamId',
                                 'score_home': 'score',
                                 'teamId_away': 'teamId_opp',
                                 'score_away': 'score_opp'
                                 },
                        inplace=True)
    df_home_data['home_or_away'] = 'home'

    # stack data and filter out the null teamIds (this is from bye weeks)
    df_expanded = pd.concat([df_home_data, df_away_data])
    df_expanded = df_expanded[df_expanded['teamId'].notnull()]

    # replace null values in teamId_opp and with sentinel value (-1)
    # so it can be converted to integer and score_opp with 0
    df_expanded['teamId_opp'].fillna(-1, inplace=True)
    df_expanded['score_opp'].fillna(0, inplace=True)

    # convert the teamIds to integers
    df_expanded['teamId'] = df_expanded['teamId'].astype('int')
    df_expanded['teamId_opp'] = df_expanded['teamId_opp'].astype('int')

    return df_expanded


def add_win_loss_ind(matchup_data):
    """
    Returns Week/Team level dataframe with win, loss, tie indicators added
    """
    matchup_data = matchup_data.copy()
    # create list for the np.select parameter to create win and loss flags
    conditions = [
        (matchup_data['score'] > matchup_data['score_opp']),
        (matchup_data['score'] < matchup_data['score_opp'])
    ]

    matchup_data['win_ind'] = np.select(conditions, [1, 0])
    matchup_data['loss_ind'] = np.select(conditions, [0, 1])

    # create list for the np.select parameter to create tie flag
    conditions = [
        (matchup_data['score'] == matchup_data['score_opp']),
        (matchup_data['score'] != matchup_data['score_opp'])
    ]

    matchup_data['tie_ind'] = np.select(conditions, [1, 0])

    # create a metric that combines wins and ties (1 for win and .5 for tie)
    matchup_data['total_wins'] = matchup_data['win_ind'] + .5 * matchup_data['tie_ind']

    return matchup_data

def add_all_play(matchup_data):
    """
    Returns Week/Team level dataframe with all play wins and losses added
    """
    matchup_data = matchup_data.copy()

    number_of_teams = len(matchup_data.groupby(['teamId'], as_index=False).size().index)

    # Get the week_number/scores freq and sort in ascending order (lowest score to highest)
    # Note that this will allow for a more robust calculation for ties given that all ties in a given
    # week will be grouped together
    get_size = matchup_data.groupby(['week_number', 'score'], as_index=False).size()
    get_size.sort_values(by=['week_number', 'score'], inplace=True, ascending=True)

    # Create the cumulative sum of the week_number/scores freq
    # (i.e. number of scores the ith score beats + the number of i scores)
    get_size['cum_sum'] = get_size.groupby(['week_number'])['size'].cumsum()

    # create variable that accounts for ties - if no ties, then 0. Otherwise, 1/number of likewise scores
    get_size['add_tie_amount'] = 0
    get_size.loc[get_size['size'] > 1, 'add_tie_amount'] = 1 / get_size['size']
    get_size['all_play_wins'] = get_size['cum_sum'] - get_size['size'] + get_size['add_tie_amount']

    # merge all_play_wins onto main dataset and add all_play_losses
    matchup_data = pd.merge(matchup_data, get_size[['week_number', 'score', 'all_play_wins']],
                            on=['week_number', 'score'], how='outer')

    matchup_data['all_play_losses'] = number_of_teams - matchup_data['all_play_wins'] - 1
    matchup_data.sort_values(by=['week_number', 'teamId'], inplace=True, ascending=True)

    return matchup_data


def add_cum_metrics(matchup_data, cum_metrics_dict, by_group='teamId', cum_group='week_number'):
    """
    Returns Week/Team level dataframe with cumulative metrics added to it
    """
    matchup_data = matchup_data.copy()

    # need to rethink how this by_group get passed - currently, if more than one by_group needs to be included,
    # you need to pass them all as strings separated by commas. It would make more sense for this to be
    # stored in an actual data structure (e.g. a list)
    matchup_data.sort_values(by=[by_group, cum_group], inplace=True)

    for cum_metric, new_col_name in cum_metrics_dict.items():
        matchup_data[new_col_name] = matchup_data.groupby([by_group])[cum_metric].cumsum()

    return matchup_data


def merge_on_team_data(matchup_data, team_df):
    """
    Returns Week/Team level dataframe with team information merged on
    @param matchup_data: matchup data
    @type team_df: dataframe
    """
    matchup_data = matchup_data.copy()
    team_df = team_df.copy()

    matchup_data = pd.merge(matchup_data, team_df, on=['teamId'])
    matchup_data.sort_values(by=['week_number', 'teamId'], inplace=True, ascending=True)

    return matchup_data

def add_standings(matchup_data, week_number,
                  rank_metrics_by_week_range={'1-12': [['cum_total_wins', 'cum_score'],
                                                       [False, False]]}):
    """
    Returns one week of team level data that includes the standings for that week
    @type week_number: Dictionary
    @param matchup_data: matchup data
    @type rank_metrics_by_week_range: Dictionary
    """
    # filter matchup_data on the week_number of interest
    matchup_data = matchup_data.copy()
    matchup_data = matchup_data.loc[matchup_data['week_number'] == week_number]

    # get the number of teams and number of different ranking tiers
    number_of_teams = len(matchup_data.groupby(['teamId'], as_index=False).size().index)
    # num_rank_ranges = len(rank_metrics_by_week_range.keys())

    # get the column names into a list and add 'rank'
    columns = list(matchup_data.columns)
    columns.append('standings')

    # create an empty dataframe containing all of columns from matchup_data plus 'rank'
    df_matchup_data_stacked = pd.DataFrame(columns=columns)

    for key, value in rank_metrics_by_week_range.items():
        # pull the lower and upper rank numbers
        rank_range_lower = int(key[0:key.find('-')].strip())
        rank_range_upper = int(key[key.find('-') + 1:].strip())

        # create list of all the ranks that will be calculated in the loop
        rank_list = []
        for i in range(rank_range_lower, rank_range_upper + 1):
            rank_list.append(i)

        # create an index number to filter out the remaining matchup data
        index_upper = rank_range_upper - rank_range_lower + 1

        primary_rank_metric = value[0][0]
        secondary_rank_metric = value[0][1]

        primary_ascending = value[1][0]
        secondary_ascending = value[1][1]

        # sort the remaining matchup data according to current tiers' metrics
        matchup_data.sort_values([primary_rank_metric, secondary_rank_metric],
                                 ascending=(primary_ascending, secondary_ascending), inplace=True)

        #         matchup_data.reset_index(inplace=True)
        df_append = matchup_data.iloc[:index_upper].copy()

        df_append.reset_index(inplace=True)

        # create the rank variable
        for i in range(0, index_upper):
            df_append.loc[i, 'standings'] = rank_list[i]

        # filter out the matchup data used for df_append so it doesn't get used in the next iteration
        if rank_range_upper < number_of_teams:
            matchup_data = matchup_data.iloc[index_upper:]

        df_matchup_data_stacked = df_matchup_data_stacked.append(df_append)

    df_matchup_data_stacked['standings'] = df_matchup_data_stacked['standings'].astype('int')
    df_matchup_data_stacked.reset_index(inplace=True)

    return df_matchup_data_stacked


def add_all_standings(df_matchup_data, number_of_weeks=13,
                      rank_metrics_by_week_range={'1-12': [['cum_total_wins', 'cum_score'],
                                                           [False, False]]}):
    """
    Returns Week/Team level dataframe that includes week level standings
    @type rank_metrics_by_week_range: dictonary
    """
    df_matchup_data = df_matchup_data.copy()

    # get the column names into a list and add 'rank'
    columns = list(df_matchup_data.columns)
    columns.append('standings')

    # create an empty dataframe containing all of columns from matchup_data plus 'rank'
    df_matchup_data_stacked = pd.DataFrame(columns=columns)

    # create the standings for each ith week and append the data to the stack dataframe
    for i in range(1, number_of_weeks + 1):
        df_matchup_data_w_standings = add_standings(df_matchup_data, i, rank_metrics_by_week_range)

        df_matchup_data_stacked = df_matchup_data_stacked.append(df_matchup_data_w_standings)

    df_matchup_data_stacked.reset_index(inplace=True, drop=True)

    return df_matchup_data_stacked

def survivor_challenge(df_matchup_data, week_number):
    """
    Returns a DataFrame containing the remaining teams left in the survivor challenge through
    week specified by the "week_number" param and the loser of that week
    """
    df_matchup_data = df_matchup_data.copy()

    # create a dataframe containing all of the team names
    df_remaining_teams = df_matchup_data.groupby(['full_name'], as_index=False).size()
    df_remaining_teams = df_remaining_teams['full_name']

    for week in range(1, week_number + 1):
        # create a dataframe containing the current week's data
        df_matchup_data_week = df_matchup_data.loc[df_matchup_data['week_number'] == week].copy()

        # merge the dataframe onto the remaining teams df so that only the teams still alive are considered
        df_matchup_data_week = pd.merge(df_remaining_teams, df_matchup_data_week,
                                        on=['full_name'], how='left')

        # sort the values so that the lowest scoring team is listed at the top
        df_matchup_data_week.sort_values(by=['score', 'cum_score'], inplace=True, ascending=True)

        survivor_loser = df_matchup_data_week.iloc[0]
        survivor_loser = survivor_loser['full_name']

        df_remaining_teams = df_remaining_teams.loc[df_remaining_teams != survivor_loser]

    return (df_remaining_teams, survivor_loser)

def create_week_number_dates(str_first_prelim_date='9/15/2020'):
    '''
    - Returns dictionary containing the week numbers (value) associated with their
      first day of valid rankings
    - Intending to use this as a way to update the app with the appropriate week
    '''
    week_number_dates_dict = {}

    date_prelim_date = datetime.strptime(str_first_prelim_date, "%m/%d/%Y").date()
    for week_number in range(1, 14):
        str_prelim_date = date_prelim_date.strftime("%m/%d/%Y")
        week_number_dates_dict[str_prelim_date] = week_number

        date_prelim_date += timedelta(days=7)

    return week_number_dates_dict


def return_current_standings(week_number):
    """ return current standings given week number and standings through all current weeks available """
    # Create dicionary containing the primary team attributes
    teamId_dict = {
        '2019': [
            [1, "Connor DeLong", "DeLong"],
            [2, "Shawn Fulford", "Fulfi"],
            [3, "Kevin Perelstein", "K-Train"],
            [4, "Mario Bynum", "Mario"],
            [5, "Brendan Elliot", "Brendan"],
            [6, "Josh Nadeau", "Germany"],
            [7, "Keith Kaplan", "Keith"],
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
            [7, "Keith Kaplan", "Keith"],
            [8, "Jonathan Kaunert", "Jon"],
            [9, "Alex Darr", "Darr"],
            [10, "Travis Hohman", "Travis"],
            [11, "Keanu Hines", "Keanu"],
            [12, "Matt Fleisher", "Fleish"]
        ]
    }

    # Dictionary containing the metrics that will be transformed as cumulative totals by team across weeks
    cum_dictionary = {'score': 'cum_score', 'win_ind': 'cum_wins', 'all_play_wins': 'cum_all_play_wins'
        , 'all_play_losses': 'cum_all_play_losses', 'tie_ind': 'cum_ties'
        , 'loss_ind': 'cum_losses', 'total_wins': 'cum_total_wins'}

    rank_metrics_by_week_range = {'1-4': [['cum_total_wins', 'cum_score'], [False, False]]
        , '5-6': [['cum_all_play_wins', 'cum_score'], [False, False]]
        , '7-12': [['cum_total_wins', 'cum_score'], [False, False]]}

    # Create dataframe versions of the 2019 and 2020 team dictionaries
    team_df_2019 = pd.DataFrame(teamId_dict['2019'], columns=['teamId', 'full_name', 'manual_nickname'])
    team_df_2019['seasonId'] = 2019

    team_df_2020 = pd.DataFrame(teamId_dict['2020'], columns=['teamId', 'full_name', 'manual_nickname'])
    team_df_2020['seasonId'] = 2020

    team_df_all_seasons = pd.concat([team_df_2019, team_df_2020])

    # Create several different JSON objects containing different pulls from the ESPN API
    main_data_2019 = pull_data(2019, league_id=48347143)

    matchup_data_2019 = pull_data(2019, league_id=48347143,
                                  dict_params={"view": "mMatchup"})
    matchup_data_2020 = pull_data(2020, league_id=48347143,
                                  dict_params={"view": "mMatchup"})

    # player_info_2020 = pull_data(2019, league_id=48347143,
    #                              dict_params={"view": "kona_player_info"})
    # pro_team_info_2020 = pull_data(2020,
    #                                dict_params={"view": "proTeamSchedules_wl"})

    # Create global variables consisting of the primary datasets to use below
    # Note: There's probably a better way to go about this
    choose_data = matchup_data_2020.copy()
    team_df = team_df_2020.copy()

    # Run through the processing steps to create the final Team/Week level dataframe
    df_matchup_data = create_matchup_df(choose_data)
    df_expanded_matchup = expand_matchup_data(df_matchup_data)
    df_matchup_data_w_wl = add_win_loss_ind(df_expanded_matchup)
    df_matchup_data_w_all_play = add_all_play(df_matchup_data_w_wl)
    df_matchup_data_w_cum = add_cum_metrics(df_matchup_data_w_all_play, cum_dictionary)
    df_matchup_data_w_team = merge_on_team_data(df_matchup_data_w_cum, team_df)
    df_final = add_all_standings(df_matchup_data_w_team, rank_metrics_by_week_range=rank_metrics_by_week_range)

    df_current_standings = df_final[['week_number', 'full_name', 'standings', 'cum_total_wins','score',
           'all_play_wins', 'cum_score', 'cum_all_play_wins',
            'manual_nickname', 'cum_losses', 'cum_ties', 'cum_wins']].loc[df_final['week_number'] == week_number]

    # df_final[['week_number', 'full_name', 'standings', 'score',
    #           'cum_total_wins', 'cum_score', 'cum_all_play_wins', 'manual_nickname']]

    return (df_final, df_current_standings)


week_number = 7

pd.options.display.max_columns = None
pd.options.display.width = None

df_current_standings = return_current_standings(week_number)[1]

df_final = return_current_standings(week_number)[0]

print(df_current_standings)

remaining_teams, losing_team = survivor_challenge(df_final, week_number)
print(losing_team)
print(remaining_teams)

print(df_final.columns)

file_dir = '/home/cdelong/python_projects/ff_web_app/\
delt_ff_standings/weekly_standings_csvs/Delt_2020_Week' + str(week_number) + '_Standings.csv'

# Creates a csv of the current standings
# df_current_standings.to_csv(file_dir)
