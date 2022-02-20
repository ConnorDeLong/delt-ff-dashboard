"""
Loads data into the tables that need updated once a season
"""

import psycopg2
import pandas as pd
import pull_data
from credentials import USER, PASSWORD


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


def drop_rows(conn: psycopg2.connect, table: str, where_condition: str) -> None:
    ''' Drops rows from a table based on a set of conditions '''

    query  = f'''
        DELETE FROM {table}
        WHERE {where_condition}
    '''
    
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    cursor.close()


def insert_rows(conn: psycopg2.connect, df: pd.DataFrame, table: str) -> None:
    ''' Inserts the df values into the DB table '''
    # Create a list of tupples from the dataframe values
    tuples = [tuple(x) for x in df.to_numpy()]
    tuples_str = ', '.join(map(str, tuples))
    
    # Comma-separated dataframe columns
    cols = ','.join(list(df.columns))
    
    # SQL quert to execute
    query  = "INSERT INTO %s(%s) VALUES %s" % (table, cols, tuples_str)
    
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    cursor.close()
    
    
def _create_update_set_statement(cols: list) -> str:
    ''' 
    Creates the "do update set" statement used for upsert.
    '''
    base_str ='DO UPDATE SET '
    for i, col in enumerate(cols):
        seperator = ', '
        if i == 0:
            seperator = ''
            
        set_col = seperator + col + ' = EXCLUDED.' + col
    
        base_str = base_str + set_col
        
    return base_str


def upsert_rows(conn: psycopg2.connect, df: pd.DataFrame, table: str, pkeys: list) -> None:
    """
    Using cursor.mogrify() to build the bulk insert query
    then cursor.execute() to execute the query
    """
    # Create a list of tupples from the dataframe values
    tuples = [tuple(x) for x in df.to_numpy()]
    tuples_str = ', '.join(map(str, tuples))
    
    # Comma-separated dataframe columns
    cols = ','.join(list(df.columns))
    
    insert_statement = "INSERT INTO %s(%s) VALUES %s" % (table, cols, tuples_str)
    on_conflict_statement = 'ON CONFLICT (' + ', '.join(map(str, pkeys)) + ')'
    do_update_statement = _create_update_set_statement(list(df.columns))
    
    # SQL quert to execute
    query  = insert_statement + ' ' + on_conflict_statement + ' ' + do_update_statement
    
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    cursor.close()


def load_teams(conn: psycopg2.connect, years: list, table: str='TEAMS', pkeys: list=['year', 'team_id']) -> None:
    ''' Loads the TEAMS table '''
    df_team = pull_data.create_team_data()
    
    filter_years = df_team['year'].isin(years)
    df_team = df_team[filter_years]
    
    rename_cols = {'teamId': 'team_id', 'full_name': 'manager_name', 'manual_nickname': 'manager_nickname'}
    df_team.rename(columns=rename_cols, inplace=True)
    
    upsert_rows(conn, df_team, table, pkeys)


if __name__ == '__main__':
    
    from create_table_schemas import create_table_teams
    
    CONNECT_PARAMS = {'user': USER, 'password': PASSWORD,
                      'host': '127.0.0.1', 'port': '5432', 'database': 'Delt_FF_DB'}
    
    conn = create_db_connection()
    
    ####################################################
    ################## UPSERT TABLES ###################
    ####################################################
    load_teams(conn, [2019, 2020, 2021])
   

