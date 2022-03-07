
import psycopg2

from helpers import create_db_connection
from configs import connection_params


def create_table_scores(conn: psycopg2.connect, overwrite: bool=False) -> None:
    ''' Creates the columns and relationships of the WEEKLY_SCORES table '''
    
    table_name = 'SCORES'
    
    if overwrite == True:
        drop_table_statement = f'''DROP TABLE IF EXISTS {table_name};'''
    else:
        drop_table_statement = ''
        
    create_table_statment = f'''
        {drop_table_statement}
        
        CREATE TABLE {table_name}
        (
            LEAGUE_ID BIGINT
            , SEASON_ID SMALLINT
            , WEEK_NUMBER BIGINT
            , TEAM_ID SMALLINT
            , TEAM_ID_OPP SMALLINT
            , SCORE NUMERIC(5, 2)
            , SCORE_OPP NUMERIC(5, 2)
            , WLT_POINTS NUMERIC(2, 1)
            , WIN_IND SMALLINT
            , LOSS_IND SMALLINT
            , TIE_IND SMALLINT
            , ALL_PLAY_WLT_POINTS NUMERIC(3, 1)
            , ALL_PLAY_WINS SMALLINT
            , ALL_PLAY_LOSSES SMALLINT
            , ALL_PLAY_TIES SMALLINT
            , CUM_SCORE NUMERIC(6, 2)
            , CUM_SCORE_OPP NUMERIC(6, 2)
            , CUM_WLT_POINTS NUMERIC(3, 1)
            , CUM_WINS SMALLINT
            , CUM_LOSSES SMALLINT
            , CUM_TIES SMALLINT
            , CUM_ALL_PLAY_WLT_POINTS NUMERIC(4, 1)
            , CUM_ALL_PLAY_WINS SMALLINT
            , CUM_ALL_PLAY_LOSSES SMALLINT
            , CUM_ALL_PLAY_TIES SMALLINT
            , CUM_SCORE_PER_WEEK NUMERIC(5, 2)
            , CUM_SCORE_OPP_PER_WEEK NUMERIC(5, 2)
            , CUM_ALL_PLAY_WLT_POINTS_PER_WEEK NUMERIC(3, 1)
            , RECORD VARCHAR(10)
            , ALL_PLAY_RECORD VARCHAR(10)
            , STANDINGS SMALLINT
            , HOME_OR_AWAY VARCHAR(10)
            
            , CONSTRAINT WEEKLY_SCORES_PKEY PRIMARY KEY(LEAGUE_ID, SEASON_ID, WEEK_NUMBER, TEAM_ID)
        );
        '''

    cursor = conn.cursor()
    cursor.execute(create_table_statment)
    conn.commit()

    cursor.close()
    
    
def create_table_teams(conn: psycopg2.connect, overwrite: bool=False) -> None:
    ''' Creates the columns and relationships of the TEAMS table '''
    
    table_name = 'TEAMS'
    
    if overwrite == True:
        drop_table_statement = f'''DROP TABLE IF EXISTS {table_name};'''
    else:
        drop_table_statement = ''
        
    create_table_statment = f'''
        {drop_table_statement}
        
        CREATE TABLE {table_name}
        (
            LEAGUE_ID BIGINT
            , SEASON_ID SMALLINT
            , TEAM_ID SMALLINT
            , MANAGER_ID VARCHAR(50)
            , TEAM_NAME VARCHAR(50)
            , MANAGER_NAME VARCHAR(50)
            , ESPN_NAME VARCHAR(50)

            , CONSTRAINT TEAMS_PKEY PRIMARY KEY(LEAGUE_ID, SEASON_ID, TEAM_ID)
        );
        '''

    cursor = conn.cursor()
    cursor.execute(create_table_statment)
    conn.commit()

    cursor.close()
    
    
def create_table_weeks(conn: psycopg2.connect, overwrite: bool=False) -> None:
    ''' Creates the columns and relationships of the WEEKS table '''
    
    table_name = 'WEEKS'
    
    if overwrite == True:
        drop_table_statement = f'''DROP TABLE IF EXISTS {table_name};'''
    else:
        drop_table_statement = ''
        
    create_table_statment = f'''
        {drop_table_statement}
        
        CREATE TABLE {table_name}
        (
            LEAGUE_ID BIGINT
            , SEASON_ID SMALLINT
            , WEEK_NUMBER SMALLINT
            , MATCHUP_PERIOD SMALLINT
            , REG_SEASON_FLAG SMALLINT

            , CONSTRAINT WEEKS_PKEY PRIMARY KEY(LEAGUE_ID, SEASON_ID, WEEK_NUMBER)
        );
        '''

    cursor = conn.cursor()
    cursor.execute(create_table_statment)
    conn.commit()

    cursor.close()
    
    
def create_table_divisions(conn: psycopg2.connect, overwrite: bool=False) -> None:
    ''' Creates the columns and relationships of the DIVISIONS table '''
    
    table_name = 'DIVISIONS'
    
    if overwrite == True:
        drop_table_statement = f'''DROP TABLE IF EXISTS {table_name};'''
    else:
        drop_table_statement = ''
        
    create_table_statment = f'''
        {drop_table_statement}
        
        CREATE TABLE {table_name}
        (
            LEAGUE_ID BIGINT
            , SEASON_ID SMALLINT
            , DIVISION_NAME VARCHAR(50)
            , SIZE SMALLINT
            , DIVISION_ID SMALLINT

            , CONSTRAINT DIVISIONS_PKEY PRIMARY KEY(LEAGUE_ID, SEASON_ID, DIVISION_ID)
        );
        '''

    cursor = conn.cursor()
    cursor.execute(create_table_statment)
    conn.commit()

    cursor.close()
    
    
def create_table_settings(conn: psycopg2.connect, overwrite: bool=False) -> None:
    ''' Creates the columns and relationships of the SETTINGS table '''
    
    table_name = 'SETTINGS'
    
    if overwrite == True:
        drop_table_statement = f'''DROP TABLE IF EXISTS {table_name};'''
    else:
        drop_table_statement = ''
        
    create_table_statment = f'''
        {drop_table_statement}
        
        CREATE TABLE {table_name}
        (
            LEAGUE_ID BIGINT
            , SEASON_ID SMALLINT
            , PLAYOFF_SEEDING_RULE VARCHAR(100)
            , PLAYOFF_SEEDING_RULE_BY SMALLINT
            , NUM_PLAYOFF_TEAMS SMALLINT
            , FIRST_SCORING_PERIOD SMALLINT
            , FINAL_SCORING_PERIOD SMALLINT
            , PLAYOFF_WEEK_START SMALLINT
            , SCORING_TYPE VARCHAR(50)
            , REG_SEASON_MATCHUP_TIEBREAKER VARCHAR(50)
            , PLAYOFF_MATCHUP_TIEBREAKER VARCHAR(50)
            , HOME_TEAM_BONUS SMALLINT

            , CONSTRAINT SETTINGS_PKEY PRIMARY KEY(LEAGUE_ID, SEASON_ID)
        );
        '''

    cursor = conn.cursor()
    cursor.execute(create_table_statment)
    conn.commit()

    cursor.close()


if __name__ == '__main__':
    
    connect_params = connection_params(connect_type='heroku')
    conn = create_db_connection(connect_params=connect_params)
    
    create_table_scores(conn, overwrite=True)
    create_table_teams(conn, overwrite=True)
    create_table_weeks(conn, overwrite=True)
    create_table_divisions(conn, overwrite=True)
    create_table_settings(conn, overwrite=True)
    
    conn.close()


    ####################################################
    ################## SCRATCH #########################
    ####################################################
    # select_statement = '''
    # SELECT *
    # FROM SEASONS;
    # '''
    
    # conn = create_db_connection(connect_params=CONNECT_PARAMS)
    
    # cursor = conn.cursor()
    # cursor.execute(select_statement)
    
    # check = cursor.fetchall()
    # print(check)
    
    # cursor.close()
    # conn.close()




