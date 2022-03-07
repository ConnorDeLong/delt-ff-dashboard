import psycopg2
import pandas as pd
from configs import connection_params


def create_db_connection(connect_params: dict=None) -> psycopg2.connect:
    if connect_params is None:
        connect_params = connection_params(connect_type='heroku')
    
    conn = psycopg2.connect(user=connect_params['user'],
                            password=connect_params['password'],
                            host=connect_params['host'],
                            port=connect_params['port'],
                            database=connect_params['database']
                            )
    
    return conn


def table_columns(conn: psycopg2.connect, table: str) -> tuple:
    """ Pulls all columns in a table """
    
    table = table.lower()
    query = f'''
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'public'
            AND TABLE_NAME = '{table}'
    '''
    
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        
        cols = cursor.fetchall()
        cols = [col[0] for col in cols]
        
        cursor.close()
        
        return cols
        
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        
        return 1


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
