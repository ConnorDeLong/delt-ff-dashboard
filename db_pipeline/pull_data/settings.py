"""
Provides classes and functions to pull Settings related data for a
Season/League/Team
"""

import pandas as pd
import numpy as np


def pull_settings_data(raw_settings_data, league_id, season_id):
    """ Returns dataframe containing all relevant data for the settings of a league/year """
    
    schedule_settings = raw_settings_data['settings']['scheduleSettings']
    scoring_settings = raw_settings_data['settings']['scoringSettings']
    status_settings = raw_settings_data['status']
    
    playoffSeedingRule = schedule_settings['playoffSeedingRule']
    playoffSeedingRuleBy = schedule_settings['playoffSeedingRuleBy']

    num_playoff_teams = schedule_settings['playoffTeamCount']

    firstScoringPeriod = status_settings['firstScoringPeriod']
    finalScoringPeriod = status_settings['finalScoringPeriod']
    playoff_week_start = schedule_settings['matchupPeriodCount'] + 1
    
    scoring_type = scoring_settings['scoringType']
    
    reg_season_matchup_tiebreaker = scoring_settings['matchupTieRule']
    playoff_matchup_tiebreaker = scoring_settings['playoffMatchupTieRule']
    
    home_team_bonus = scoring_settings['homeTeamBonus']

    settings_list = [[playoffSeedingRule, playoffSeedingRuleBy, num_playoff_teams,
                    firstScoringPeriod, finalScoringPeriod, playoff_week_start, scoring_type, 
                    reg_season_matchup_tiebreaker, playoff_matchup_tiebreaker, home_team_bonus]]
    
    columns = ['playoff_seeding_rule', 'playoff_seeding_rule_by', 'num_playoff_teams',
               'first_scoring_period', 'final_scoring_period', 'playoff_week_start', 'scoring_type', 
               'reg_season_matchup_tiebreaker', 'playoff_matchup_tiebreaker', 
               'home_team_bonus']
    
    df = pd.DataFrame(settings_list, columns=columns)
    df['league_id'] = league_id
    df['season_id'] = season_id
        
    return df


def pull_divisions(raw_settings_data, league_id, season_id):
    """ Return dataframe containing the name and size of each division """
    
    divisions_list = raw_settings_data['settings']['scheduleSettings']['divisions']

    divisions = []
    for division in divisions_list:
        division_name = division['name']
        division_size = division['size']
        divisionId = division['id']

        divisions.append([division_name, division_size, divisionId])
        
    columns = ['division_name', 'size', 'division_id']
    df = pd.DataFrame(divisions, columns=columns)
    
    df['league_id'] = league_id
    df['season_id'] = season_id

    return df


def create_scoring_period_lookup(raw_settings_data, num_reg_season_matchups):
    """ Returns dataframe containing the scoring period mapped to matchup period """
    
    reg_season_matchups_pds = raw_settings_data['settings']['scheduleSettings']['matchupPeriods']
    
    scoring_pd_list = []
    for matchup_pd, scoring_pds in reg_season_matchups_pds.items():
        
        matchup_pd = int(matchup_pd)   
        for scoring_pd in scoring_pds:
            
            scoring_pd = int(scoring_pd)

            scoring_pd_list.append([scoring_pd, matchup_pd])
            
    columns = ['scoringPeriodId', 'macthupPeriodId']
    df = pd.DataFrame(scoring_pd_list, columns=columns)
    
    week_type_conditions = [
        (df['macthupPeriodId'] <= num_reg_season_matchups),
        (df['macthupPeriodId'] > num_reg_season_matchups)
    ]

    df['regular_season_ind'] = np.select(week_type_conditions, [1, 0])
            
    return df
    

if __name__ == '__main__':
    
    pd.set_option('display.max_columns', 50)
    
    settings = settingsData(2021, 48347143)
    
    df_settings = pull_settings_data(settings)
    df_divisions = pull_divisions_data(settings)

    print(df_settings)
    # print('\n', '\n')
    print(df_divisions)
    
    
    # raw_settings_data = pull_data(season_id, league_id, params=(("view", "mSettings")))
