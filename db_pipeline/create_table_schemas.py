
import psycopg2
from credentials import USER, PASSWORD

CONNECT_PARAMS = {'user': USER, 'password': PASSWORD,
                  'host': '127.0.0.1', 'port': '5432', 'database': 'Delt_FF_DB'}

def create_db_connection(connect_params: dict=None) -> psycopg2.connect:
    if connect_params is None:
        connect_params = CONNECT_PARAMS
    
    conn = psycopg2.connect(user=connect_params['user'],
                            password=connect_params['password'],
                            host=connect_params['host'],
                            port=connect_params['port'],
                            database=connect_params['database']
                            )
    
    return conn


def create_table_weekly_scores(conn: psycopg2.connect, overwrite: bool=False, table_name: str='WEEKLY_SCORES') -> None:
    ''' Creates the columns and relationships of the WEEKLY_SCORES table '''
    
    if overwrite == True:
        drop_table_statement = f'''DROP TABLE IF EXISTS {table_name};'''
    else:
        drop_table_statement = ''
        
    create_table_statment = f'''
        {drop_table_statement}
        
        CREATE TABLE {table_name}
        (
            YEAR SMALLINT
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
            , CUM_ALL_PLAY_WLT_POINTS_PER_WEEK NUMERIC(3, 2)
            , RECORD VARCHAR(10)
            , ALL_PLAY_RECORD VARCHAR(10)
            , STANDINGS SMALLINT
            , HOME_OR_AWAY VARCHAR(10)
            , CONSTRAINT WEEKLY_SCORES_PKEY PRIMARY KEY(YEAR, TEAM_ID, WEEK_NUMBER)
        );
        '''

    cursor = conn.cursor()
    cursor.execute(create_table_statment)
    conn.commit()

    cursor.close()
    
    
def create_table_teams(conn: psycopg2.connect, overwrite: bool=False, table_name: str='TEAMS') -> None:
    ''' Creates the columns and relationships of the TEAMS table '''
    
    if overwrite == True:
        drop_table_statement = f'''DROP TABLE IF EXISTS {table_name};'''
    else:
        drop_table_statement = ''
        
    create_table_statment = f'''
        {drop_table_statement}
        
        CREATE TABLE {table_name}
        (
            TEAM_ID SMALLINT
            , YEAR SMALLINT
            , MANAGER_NAME VARCHAR(50)
            , MANAGER_NICKNAME VARCHAR(50)
            , CONSTRAINT TEAMS_PKEY PRIMARY KEY(YEAR, TEAM_ID)
        );
        '''

    cursor = conn.cursor()
    cursor.execute(create_table_statment)
    conn.commit()

    cursor.close()
    
    
def create_table_weeks(conn: psycopg2.connect, overwrite: bool=False, table_name: str='WEEKS') -> None:
    ''' Creates the columns and relationships of the WEEKS table '''
    
    if overwrite == True:
        drop_table_statement = f'''DROP TABLE IF EXISTS {table_name};'''
    else:
        drop_table_statement = ''
        
    create_table_statment = f'''
        {drop_table_statement}
        
        CREATE TABLE {table_name}
        (
            YEAR SMALLINT
            , WEEK_NUMBER SMALLINT
            , MATCHUP_PERIOD SMALLINT
            , WEEK_TYPE VARCHAR(25)
            , CONSTRAINT WEEKS_PKEY PRIMARY KEY(YEAR, WEEK_NUMBER)
        );
        '''

    cursor = conn.cursor()
    cursor.execute(create_table_statment)
    conn.commit()

    cursor.close()
    
    
def create_table_divisions(conn: psycopg2.connect, overwrite: bool=False, table_name: str='DIVISIONS') -> None:
    ''' Creates the columns and relationships of the DIVISIONS table '''
    
    if overwrite == True:
        drop_table_statement = f'''DROP TABLE IF EXISTS {table_name};'''
    else:
        drop_table_statement = ''
        
    create_table_statment = f'''
        {drop_table_statement}
        
        CREATE TABLE {table_name}
        (
            YEAR SMALLINT
            , DIVISION_ID SMALLINT            
            , DIVISION_NAME VARCHAR(50)
            , SIZE SMALLINT
            , CONSTRAINT DIVISIONS_PKEY PRIMARY KEY(YEAR, DIVISION_ID)
        );
        '''

    cursor = conn.cursor()
    cursor.execute(create_table_statment)
    conn.commit()

    cursor.close()
    
    
def create_table_settings(conn: psycopg2.connect, overwrite: bool=False, table_name: str='SETTINGS') -> None:
    ''' Creates the columns and relationships of the SETTINGS table '''
    
    if overwrite == True:
        drop_table_statement = f'''DROP TABLE IF EXISTS {table_name};'''
    else:
        drop_table_statement = ''
        
    create_table_statment = f'''
        {drop_table_statement}
        
        CREATE TABLE {table_name}
        (
            YEAR SMALLINT
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
            , CONSTRAINT SETTINGS_PKEY PRIMARY KEY(YEAR)
        );
        '''

    cursor = conn.cursor()
    cursor.execute(create_table_statment)
    conn.commit()

    cursor.close()


if __name__ == '__main__':
    
    CONNECT_PARAMS = {'user': 'postgres', 'password': 'pencil11',
                      'host': '127.0.0.1', 'port': '5432', 'database': 'Delt_FF_DB'}
    
    conn = create_db_connection(connect_params=CONNECT_PARAMS)
    
    create_table_weekly_scores(conn, overwrite=True)
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




