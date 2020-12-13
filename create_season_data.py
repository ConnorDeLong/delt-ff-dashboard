import pandas as pd


def create_season_data():
    """ Returns a dataframe containing the primary attributes of the league by season """

    # Create a list containing the payout breakdown and their respective winners.
    # IMPORTANT NOTE: variable names of the payouts and winners must ONLY differ by their prefix
    # Using the "full_name" here for the winner variables
    season_list = [
        [2019, 12, 50, 350, 100, 50, 50, 50,
         'Matt Fleisher', 'Connor DeLong', 'Jonathan Kaunert', 'Connor DeLong', 'Matt Fleisher'],
        [2020, 12, 50, 350, 100, 50, 50, 50,
         None, None, None, 'Connor DeLong', 'Connor DeLong']
    ]

    var_name_list = ['seasonId', 'num_teams', 'stake_per_team', 'pay_struc_first_overall', 'pay_struc_second_overall',
                     'pay_struc_third_overall', 'pay_struc_most_points', 'pay_struc_survivor', 'winner_first_overall',
                     'winner_second_overall', 'winner_third_overall', 'winner_most_points', 'winner_survivor']

    season_df = pd.DataFrame(season_list, columns=var_name_list)

    return season_df

if __name__ == '__main__':
    pd.options.display.max_columns = None
    pd.options.display.width = None

    print(create_season_data())