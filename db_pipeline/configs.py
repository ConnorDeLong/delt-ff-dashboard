import os

from credentials import HEROKU_USER, HEROKU_PASSWORD, LOCAL_USER, LOCAL_PASSWORD


LEAGUE_ID = 48347143
SEASON_ID = 2021

# NOTE: Need to set up some type of script which set this environment variable:
# export DATABASE_URL=$(heroku pg:credentials:url -a delt-ff-db)
def db_credentials() -> [dict, None]:
    credentials = os.environ.get('DATABASE_URL')

    if credentials is not None:
        credentials = credentials.replace('"', '')
        credentials_dict = {}
        for credential in credentials.split():
            break_point = credential.find('=')
            credential_type = credential[:break_point]
            credential_val = credential[break_point + 1:]
            
            credentials_dict[credential_type] = credential_val
            
        return credentials_dict
    else:
        return None
    
    
def connection_params(connect_type: str='heroku') -> dict:
    if connect_type == 'heroku':
        credentials = db_credentials()
        
        if credentials is None:
            port = '5432'
            host = 'ec2-44-194-113-156.compute-1.amazonaws.com'
            db_name = 'd9tktipamnn3o6'
            user = HEROKU_USER
            password = HEROKU_PASSWORD        
        else:
            port = credentials['port']
            host = credentials['host']
            db_name = credentials['dbname']
            user = credentials['user']
            password = credentials['password']

    else:
        port = '5432'
        host = '127.0.0.1'
        db_name = 'Delt_FF_DB'
        user = LOCAL_USER
        password = LOCAL_PASSWORD
        
    connect_params = {'user': user, 'password': password,
              'host': host, 'port': port, 'database': db_name}

    return connect_params
