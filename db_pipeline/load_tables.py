"""
Loads data into the tables that need updated once a season
"""

import psycopg2
import pandas as pd

from pull_data import ApiData
from helpers import create_db_connection, upsert_rows, table_columns


def load_table(conn: psycopg2.connect, df: pd.DataFrame, table: str, pkeys: list) -> None:
    df = df.copy()
    df.sort_values(by=pkeys, inplace=True)
    
    # df could contain columns that aren't in the DB
    cols = table_columns(conn, table)
    df = df[cols]
    
    upsert_rows(conn, df, table, pkeys)
    

if __name__ == '__main__':
    
    from configs import connection_params, LEAGUE_ID, SEASON_ID
    
    connect_params = connection_params(connect_type='heroku')
    conn = create_db_connection(connect_params=connect_params)
    season_ids = [2019, 2020, 2021]
    
    scores_keys = ['league_id', 'season_id', 'week_number', 'team_id']
    teams_keys = ['league_id', 'season_id', 'team_id']
    weeks_keys = ['league_id', 'season_id', 'week_number']
    divisions_keys = ['league_id', 'season_id', 'division_id']
    settings_keys = ['league_id', 'season_id']
    
    ####################################################
    ################## UPSERT TABLES ###################
    ####################################################
    
    for season_id in season_ids:
        espn_data = ApiData(season_id, league_id=LEAGUE_ID)
        espn_data.pull_all_data()
        
        load_table(conn, espn_data.scores, 'scores', scores_keys)
        load_table(conn, espn_data.teams, 'teams', teams_keys)
        load_table(conn, espn_data.weeks, 'weeks', weeks_keys)
        load_table(conn, espn_data.divisions, 'divisions', divisions_keys)
        load_table(conn, espn_data.settings, 'settings', settings_keys)
        
    conn.close()
    
    
    # espn_data = ApiData(SEASON_ID, league_id=LEAGUE_ID)
    # espn_data.pull_all_data()
    
    # load_table(conn, espn_data.scores, 'scores', scores_keys)
    # load_table(conn, espn_data.teams, 'teams', teams_keys)
    # load_table(conn, espn_data.weeks, 'weeks', weeks_keys)
    # load_table(conn, espn_data.divisions, 'divisions', divisions_keys)
    # load_table(conn, espn_data.settings, 'settings', settings_keys)
