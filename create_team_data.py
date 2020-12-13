import pandas as pd
import numpy as np
import create_season_data

def create_initial_team_data():
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

    team_df_2019 = pd.DataFrame(teamId_dict['2019'], columns=['teamId', 'full_name', 'manual_nickname'])
    team_df_2019['seasonId'] = 2019

    team_df_2020 = pd.DataFrame(teamId_dict['2020'], columns=['teamId', 'full_name', 'manual_nickname'])
    team_df_2020['seasonId'] = 2020

    team_df_all_seasons = pd.concat([team_df_2019, team_df_2020])

    team_df_all_seasons.reset_index(drop=True, inplace=True)

    return team_df_all_seasons


def calculate_payouts(df_team_season, payout_var_prefix='pay_struc'):
    """ Returns a Season/Team level dataframe that includes the payouts awarded """

    df_team_season = df_team_season.copy()

    df_season_cols = list(df_team_season.columns)

    payout_var_prefix_len = len(payout_var_prefix)

    payout_vars = []
    for df_season_col in df_season_cols:
        if df_season_col[:payout_var_prefix_len] == 'pay_struc':
            payout_vars.append(df_season_col[payout_var_prefix_len + 1:])

    amt_won_var_names = []
    for payout_var in payout_vars:
        amt_won_var_name = 'amt_won_' + payout_var
        winner_var_name = 'winner_' + payout_var
        payout_var_name = 'pay_struc_' + payout_var

        df_team_season[amt_won_var_name] = np.where(df_team_season['full_name'] == df_team_season[winner_var_name],
                                                    df_team_season[payout_var_name], 0)

        amt_won_var_names.append(amt_won_var_name)

    df_team_season['amt_won_total'] = df_team_season[amt_won_var_names].sum(axis=1)
    return df_team_season


def temp_create_team_data():
    df_season = create_season_data.create_season_data()

    df_team = create_initial_team_data()

    df_team = pd.merge(df_team, df_season, on=['seasonId'])

    return df_team

def create_team_data():
    return create_initial_team_data()

if __name__ == '__main__':
    pd.options.display.max_columns = None
    pd.options.display.width = None
    # all_team_df = create_team_data()
    # team_df = all_team_df.loc[all_team_df['seasonId'] == 2020]
    # print(team_df)
    # print(all_team_df)
    # test_df = temp_create_team_data()
    # print(list(test_df.columns))
    print(calculate_payouts(temp_create_team_data()))