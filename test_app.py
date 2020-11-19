
# https://dash.plotly.com/layout

# https://opensource.com/article/18/1/step-step-guide-git
from create_ff_standings import *
from get_week_number import *
import dash
import dash_table
import dash_html_components as html
import dash_bootstrap_components as dbc

def get_current_standings(week_number):
    ''' Create table used in the dashboard '''
    df_final = create_final_standings()

    df_current_standings = df_final[['week_number', 'full_name', 'standings',
            'cum_total_wins','score','all_play_wins', 'cum_score', 'cum_all_play_wins',
            'manual_nickname', 'cum_losses', 'cum_ties', 'cum_wins']].loc[df_final['week_number'] == week_number]

    dict_columns_to_rename = {'standings': 'Rank', 'manual_nickname': 'Team',
                              'cum_wins': 'Wins', 'cum_losses': 'Losses', 'cum_ties': 'Ties',
                              'cum_score': 'Points Scored',
                              'cum_all_play_wins': 'All Play Wins'}

    keep_vars = ['Rank', 'Team', 'Wins', 'Losses', 'Ties', 'Points Scored', 'All Play Wins']

    df_current_standings.rename(columns=dict_columns_to_rename, inplace=True)

    # df_current_standings['Wins'] = df_current_standings['Wins'].astype('int')
    # df_current_standings['All Play Wins'] = df_current_standings['All Play Wins'].astype('int')

    df_current_standings = df_current_standings[keep_vars]

    df_current_standings['W-L-T'] = df_current_standings['Wins'].astype(str) \
                                    + "-" + df_current_standings['Losses'].astype(str) \
                                    + "-" + df_current_standings['Ties'].astype(str)

    df_current_standings['Points Scored'] = df_current_standings['Points Scored'].round(decimals=2)

    df_current_standings = df_current_standings[['Rank', 'Team', 'W-L-T', 'Points Scored', 'All Play Wins']]

    return df_current_standings

# get the latest week number and limit it to the last week of the regular season
for_week_number = get_current_week_number()
if for_week_number > 13:
    for_week_number = 13

df_current_standings = get_current_standings(for_week_number)


# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = [dbc.themes.SANDSTONE]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

table = dbc.Table.from_dataframe(df_current_standings,
style = {
'textAlign': 'center'
, 'padding': '3px'
, 'font_size': '20px'
# , 'font_family': 'Arial'
, 'maxWidth': '65%'
, 'marginLeft': 'auto', 'marginRight': 'auto'
},
striped=False,
bordered=False,
hover=False,
responsive=True
)



app.layout = table

if __name__ == '__main__':
    app.run_server(debug=True)

