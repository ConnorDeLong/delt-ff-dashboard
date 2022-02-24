import requests
import pandas as pd
import numpy as np

import standings


class ApiData():
    
    def __init__(self, season_id: int, standings_metrics: dict=None, league_id: int=48347143) -> None:
        self.season_id = season_id
        self.league_id = league_id
        
        if standings_metrics is None:
            self.standings_metrics = {'1-4': [['cum_total_wins', 'cum_score'], [False, False]],
                                 '5-6': [['cum_all_play_wins', 'cum_score'], [False, False]],
                                 '7-12': [['cum_total_wins', 'cum_score'], [False, False]]}
        else:
            self.standings_metrics = standings_metrics
            
        self.standings = None
        self.settings = None
        self.divisions = None
        self.teams = None
        self.weeks = None
        
        self._raw_matchup = None      
        self._raw_settings = None
        self._raw_teams = None

    def pull_api_data(self, params: (dict, tuple)=None) -> dict:
        """ Returns a JSON object containing the data pulled APIs url. """
    
        if params == None:
            params = []
            
        season_id = self.season_id
        league_id = self.league_id
    
        if season_id < 2020:
            url = "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/" + \
                  str(league_id) + "?seasonId=" + str(season_id)
        else:
            url = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/" + \
                  str(season_id) + "/segments/0/leagues/" + str(league_id)
    
        # Passing the dict_params directly to the request_params of the requests.get method was
        # resulting in certain pulls retrieving unspecified data.
        # So, I'm directly applying those parameters to the URL string to prevent this
        # Note: This was likely happening due to duplicate keys being used (e.g. "view") in the dict
    
        if type(params) is tuple:
            params = self._convert_tuple_to_list(params)
    
        if type(params) is dict:
            params = self._convert_dict_to_list(params)
    
        for full_param in params:
            param = str(full_param[0])
            param_value = str(full_param[1])
    
            if url.find("?") == -1:
                url = url + "?" + param + "=" + param_value
            else:
                url = url + "&" + param + "=" + param_value
    
        r = requests.get(url)
    
        if r.status_code == 200:
            pass
        else:
            if r.status_code == 429:
                print("429 error")
    
            return None
    
            # 2020 url returns JSON object while prior season_ids return it in a list
        if season_id < 2020:
            d = r.json()[0]
        else:
            d = r.json()
    
        r.close()
    
        return d
    
    def pull_all_data(self, clear_json: bool=True) -> None:
        """ 
        Updates the attribute associated with every "pull_" method.
        """

        pull_methods = [attr for attr in dir(self) if attr.startswith('pull')]
        for pull_method in pull_methods:
            attr = pull_method[5:]
            
            # Prevents "pull_" methods without an attr from running
            if attr in(dir(self)):
                getattr(self, pull_method)(return_df=False)
                
        if clear_json:
            self.clear_json_attrs()

        return None
    
    def pull_standings(self, return_df: bool=True) -> [pd.DataFrame, None]:
        """ 
        Returns a dataframe containing the Team/Week level standings through
        the current week.
        """
        
        if self._raw_matchup is None:
            self._raw_matchup = self._pull_raw_matchup()
            
        playoff_week_start = self._playoff_week_start()
        
        df = standings.pull_standings(self._raw_matchup, playoff_week_start, 
                                      rank_metrics_by_week_range=self.standings_metrics)
        df['season_id'] = self.season_id
        df['league_id'] = self.league_id
        
        self.standings = df
        
        if return_df == True:
            return df
        else:
            return None

    def pull_settings(self, return_df: bool=True) -> [pd.DataFrame, None]:
        """ Returns dataframe containing all relevant data for the settings of a league/year. """
        
        if self._raw_settings is None:
            self._raw_settings = self._pull_raw_settings()

        schedule_settings = self._raw_settings['settings']['scheduleSettings']
        scoring_settings = self._raw_settings['settings']['scoringSettings']
        status_settings = self._raw_settings['status']
        
        playoffSeedingRule = schedule_settings['playoffSeedingRule']
        playoffSeedingRuleBy = schedule_settings['playoffSeedingRuleBy']
    
        num_playoff_teams = schedule_settings['playoffTeamCount']
    
        firstScoringPeriod = status_settings['firstScoringPeriod']
        finalScoringPeriod = status_settings['finalScoringPeriod']
        matchup_period_count = schedule_settings['matchupPeriodCount']
        
        # This ensures the playoff_week_start var references the week number (i.e. scoring period)
        playoff_week_start = self._playoff_week_start()
        
        scoring_type = scoring_settings['scoringType']
        
        reg_season_matchup_tiebreaker = scoring_settings['matchupTieRule']
        playoff_matchup_tiebreaker = scoring_settings['playoffMatchupTieRule']
        
        home_team_bonus = scoring_settings['homeTeamBonus']
    
        settings_list = [[playoffSeedingRule, playoffSeedingRuleBy, num_playoff_teams,
                        firstScoringPeriod, finalScoringPeriod, matchup_period_count, 
                        playoff_week_start, scoring_type, reg_season_matchup_tiebreaker, 
                        playoff_matchup_tiebreaker, home_team_bonus]]
        
        columns = ['playoff_seeding_rule', 'playoff_seeding_rule_by', 'num_playoff_teams',
                   'first_scoring_period', 'final_scoring_period', 'matchup_period_count', 
                   'playoff_week_start', 'scoring_type', 'reg_season_matchup_tiebreaker', 
                   'playoff_matchup_tiebreaker', 'home_team_bonus']
        
        df = pd.DataFrame(settings_list, columns=columns)
        df['league_id'] = self.league_id
        df['season_id'] = self.season_id
        
        self.settings = df
        
        if return_df == True:
            return df
        else:
            return None

    def pull_divisions(self, return_df: bool=True) -> [pd.DataFrame, None]:
        """ Return dataframe containing the name and size of each division. """
        
        if self._raw_settings is None:
            self._raw_settings = self._pull_raw_settings()
        
        divisions_list = self._raw_settings['settings']['scheduleSettings']['divisions']
    
        divisions = []
        for division in divisions_list:
            division_name = division['name']
            division_size = division['size']
            divisionId = division['id']
    
            divisions.append([division_name, division_size, divisionId])
            
        columns = ['division_name', 'size', 'division_id']
        df = pd.DataFrame(divisions, columns=columns)
        
        df['league_id'] = self.league_id
        df['season_id'] = self.season_id
    
        self.divisions = df
    
        if return_df == True:
            return df
        else:
            return None
        
    def pull_teams(self, return_df: bool=True) -> [pd.DataFrame, None]:
        """ 
        Retruns dataframe containing Team attributes.
        Note that a team can be owned by multiple members - This will member
        attributes for the first one associated with the team.
        """
        if self._raw_teams is None:
            self._raw_teams = self._pull_raw_teams()
            
        teams = []
        for team in self._raw_teams['teams']:
            team_id = team['id']
            manager_id = team['owners'][0]
            team_name = team['location'] + ' ' + team['nickname']
            
            teams.append([team_id, manager_id, team_name])
            
        df = pd.DataFrame(teams, columns=['team_id', 'manager_id', 'team_name'])
        
        member_df = self.pull_members()
        df = pd.merge(df, member_df, on='manager_id', how='left')
        
        df['season_id'] = self.season_id
        df['league_id'] = self.league_id
        
        self.teams = df
        
        if return_df == True:
            return df
        else:
            return None
    
    def pull_members(self) -> pd.DataFrame:
        """ 
        Returns dataframe containing Member attributes.
        Note: Not going to include this as an attribute yet since it 
        will be included the teams df.        
        """
        
        if self._raw_teams is None:
            self._raw_teams = self._pull_raw_teams()
            
        members = []
        for member in self._raw_teams['members']:
            manager_id = member['id']
            espn_name = member['displayName']
            manager_name = member['firstName'] + ' ' + member['lastName']
            
            members.append([manager_id, espn_name, manager_name])
            
        cols = ['manager_id', 'espn_name', 'manager_name']
        df = pd.DataFrame(members, columns=cols)
        
        return df

    def pull_weeks(self, return_df: bool=True) -> [pd.DataFrame, None]:
        """ Returns dataframe containing the scoring period mapped to matchup period. """
        
        if self._raw_settings is None:
            self._raw_settings = self._pull_raw_settings()
            
        schedule_settings = self._raw_settings['settings']['scheduleSettings']
            
        num_matchups = schedule_settings['matchupPeriodCount']
        
        reg_season_matchups_pds = self._raw_settings['settings']['scheduleSettings']['matchupPeriods']
        
        scoring_pd_list = []
        for matchup_pd, scoring_pds in reg_season_matchups_pds.items():
            
            matchup_pd = int(matchup_pd)   
            for scoring_pd in scoring_pds:
                scoring_pd = int(scoring_pd)
    
                scoring_pd_list.append([scoring_pd, matchup_pd])
                
        columns = ['week_number', 'matchup_period']
        df = pd.DataFrame(scoring_pd_list, columns=columns)
        
        week_type_conditions = [
            (df['matchup_period'] <= num_matchups),
            (df['matchup_period'] > num_matchups)
        ]
        df['regular_season_ind'] = np.select(week_type_conditions, [1, 0])
        
        df['season_id'] = self.season_id
        df['league_id'] = self.league_id
        
        self.weeks = df
        
        if return_df == True:
            return df
        else:
            return None

        return df
    
    def clear_json_attrs(self):
        ''' 
        Clears all the atttributes that hold the json data pulled from the API. 
        '''
        attrs = [attr for attr in dir(self) if attr.startswith('_raw_')]
        for attr in attrs:
            self.__dict__[attr] = None
    
    def _pull_raw_matchup(self) -> list:
        params = [["view", "mMatchup"], ["view", "mMatchupScore"]]
        return self.pull_api_data(params=params)
    
    def _pull_raw_settings(self) -> list:
        return self.pull_api_data(params=(("view", "mSettings")))
    
    def _pull_raw_teams(self) -> list:
        params = [['view', 'mTeams'], ['view', 'mTeam']]
        return self.pull_api_data(params=params)
    
    def _playoff_week_start(self) -> int:
        lookup = self.pull_weeks()
        playoff_periods = lookup['week_number'].loc[lookup['regular_season_ind'] == 0]
        playoff_week_start = playoff_periods.tolist()[0]
        
        return playoff_week_start
    
    def _convert_tuple_to_list(self, tuple_var: tuple) -> list:
        """
        Converts tuple to a list.
        Note: This isn't really necessary, but accounts for 1D tuple cases so i'm using it.
        """
    
        list_var = []
    
        # Need to process 1D and 2D tuples differently
        if type(tuple_var[0]) is tuple:
            for value in tuple_var:
                dict_key = value[0]
                dict_value = value[1]
    
                list_var.append([dict_key, dict_value])
        else:
            dict_key = tuple_var[0]
            dict_value = tuple_var[1]
    
            list_var.append([dict_key, dict_value])
    
        return list_var

    def _convert_dict_to_list(dict_var: dict) -> list:
        """ Converts dictionary to a 2D list. """
    
        list_var = []
        for param, param_value in dict_var.items():
            list_var.append([param, param_value])
    
        return list_var


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    
    espn_data = ApiData(2021, league_id=48347143)
    espn_data.pull_all_data()
    
    print(espn_data.standings)
    print(espn_data.settings)
    print(espn_data.teams)
    print(espn_data.weeks)
    print(espn_data.divisions)
    
    # print(espn_data.pull_standings())
    # print(espn_data.pull_settings())
    # print(espn_data.pull_divisions())
    # print(espn_data.pull_teams())
    # print(espn_data.pull_teams())
    
    # print(espn_data.pull_weeks())
    
    # params = [['view', 'mTeams'], ['view', 'mTeam']]
    # raw_teams = espn_data.pull_api_data(params=params)
    # print(raw_teams['teams'])
    
    # for team in raw_teams['teams']:
    #     print(team['owners'][0])
    

    # lookup = espn_data.pull_weeks()
    
    # check = lookup{}
    
    # print(lookup['week_number'].loc[lookup['matchup_period'] == 14].tolist())
    
    # settings_df = espn_data.pull_settings(return_df=True)
    # print(settings_df) 
    # print(espn_data._raw_settings['settings']['scheduleSettings'])
    
    # check = espn_data._raw_settings['settings']['scheduleSettings']['matchupPeriodCount']
    # print(check)
    
    # matchup_period_count = settings_df['matchup_period_count'].values.tolist()
    # print(matchup_period_count)
    
    # print(settings_df)
    
    # check = settings.pull_settings(settings_dict, 48347143, 2021)
    # check = settings.pull_divisions(settings_dict, 48347143, 2021)
    # print(check)
    
    