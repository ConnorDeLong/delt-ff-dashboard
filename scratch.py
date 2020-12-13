import scipy.stats

# check = scipy.stats.norm(0, [13]).cdf(5)
#
# check2 = 1 - scipy.stats.norm(5, [13]).cdf(0)
#
# print(check)
# print(check2)

from create_ff_standings import *

def create_final_standings(league_id=48347143, year=2020,
                           rank_metrics_by_week_range=None, cum_metrics_dict=None, playoff_week_start=14):
    """ return standings through all current weeks available and current standings"""

    if cum_metrics_dict is None:
        # Dictionary containing the metrics that will be transformed as cumulative totals by team across weeks
        cum_metrics_dict = {'score': 'cum_score', 'win_ind': 'cum_wins', 'all_play_wins': 'cum_all_play_wins',
                            'all_play_losses': 'cum_all_play_losses', 'tie_ind': 'cum_ties', 'loss_ind': 'cum_losses',
                            'total_wins': 'cum_total_wins', 'all_play_wins_int': 'cum_all_play_wins_int',
                            'all_play_losses_int': 'cum_all_play_losses_int',
                            'all_play_ties_int': 'cum_all_play_ties_int', 'score_opp': 'cum_score_opp'}

    if rank_metrics_by_week_range is None:
        # Set the ranking system of the league
        rank_metrics_by_week_range = {'1-12': [['cum_total_wins', 'cum_score'], [False, False]]}

    num_weeks_reg_season = playoff_week_start - 1

    # Create several different JSON objects containing different pulls from the ESPN API
    matchup_data = pull_data(year, league_id=league_id,
                             dict_params={"view": "mMatchup"})

    df_team_all_seasons = create_team_data.create_team_data()
    df_team_current_season = df_team_all_seasons.loc[df_team_all_seasons['seasonId'] == year]

    # Run through the processing steps to create the final Team/Week level dataframe
    df_matchup_data = create_matchup_df(matchup_data, playoff_week_start=playoff_week_start)
    df_expanded_matchup = expand_matchup_data(df_matchup_data)
    df_matchup_data_w_wl = add_win_loss_ind(df_expanded_matchup)
    df_matchup_data_w_all_play = add_all_play(df_matchup_data_w_wl)
    df_matchup_data_w_cum = add_cum_metrics(df_matchup_data_w_all_play, cum_metrics_dict)
    df_matchup_data_w_team = merge_on_team_data(df_matchup_data_w_cum, df_team_current_season)
    df_updated_matchup_data = add_update_additional_metrics(df_matchup_data_w_team)
    df_final = add_all_standings(df_updated_matchup_data, num_weeks_reg_season=num_weeks_reg_season,
                                 rank_metrics_by_week_range=rank_metrics_by_week_range)

    return df_final

check = create_final_standings()

print(check)

# by_group = ['A', 'B', 'C']
# cum_group = ['D', 'E']
#
# by_cum_group = by_group + cum_group
#
# print(by_cum_group)