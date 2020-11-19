# https://dash.plotly.com/layout

# https://opensource.com/article/18/1/step-step-guide-git
import create_ff_standings
import get_week_number
import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

def create_df_for_standings_table(week_number):
    """ Create table used in the dashboard """
    df_final = create_ff_standings.create_final_standings()

    # pull the standings for the current week
    df_current_standings = df_final[['week_number', 'full_name', 'standings',
            'cum_total_wins','score','all_play_wins', 'cum_score', 'cum_all_play_wins',
            'manual_nickname', 'cum_losses', 'cum_ties', 'cum_wins']].loc[df_final['week_number'] == week_number]

    # create dictionary to map the original variable names to the new ones
    dict_columns_to_rename = {'standings': 'Rank', 'manual_nickname': 'Team',
                              'cum_wins': 'Wins', 'cum_losses': 'Losses', 'cum_ties': 'Ties',
                              'cum_score': 'Points Scored',
                              'cum_all_play_wins': 'All Play Wins'}

    keep_vars = ['Rank', 'Team', 'Wins', 'Losses', 'Ties', 'Points Scored', 'All Play Wins']

    df_current_standings.rename(columns=dict_columns_to_rename, inplace=True)

    # create initial subset of data containing only the relevant variables
    df_current_standings = df_current_standings[keep_vars]

    df_current_standings['W-L-T'] = df_current_standings['Wins'].astype(str) \
                                    + "-" + df_current_standings['Losses'].astype(str) \
                                    + "-" + df_current_standings['Ties'].astype(str)

    df_current_standings['Points Scored'] = df_current_standings['Points Scored'].round(decimals=2)

    df_current_standings = df_current_standings[['Rank', 'Team', 'W-L-T', 'Points Scored', 'All Play Wins']]

    return df_current_standings


# get the latest week number and limit it to the last week of the regular season
current_week_number = get_week_number.get_current_week_number()
if current_week_number > 13:
    current_week_number = 13

# create the df used for the "standings-table"
df_for_standings_table = create_df_for_standings_table(current_week_number)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# external_stylesheets = [dbc.themes.FLATLY]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

# create the drop-down used to adjust the standings table
standings_table_dropdown = dcc.Dropdown(
    id='standings-table-dd',
    options=[{'label': f"Week {week_number}", 'value': week_number}
             for week_number in range(1, current_week_number + 1)],
    value=current_week_number,
    clearable=False,
    style={'width': '30%',
           'margin-left': '-75px',
           'margin-right': '0px',
           'font_family': 'Arial',
           'display': 'inline-block',
           'verticalAlign': 'middle',
           'text-align': 'center'
           }
)

# create table containing the standings
standings_table = dash_table.DataTable(
    id='standings-table',
    columns=[{"name": i, "id": i} for i in df_for_standings_table.columns],
    data=df_for_standings_table.to_dict('records'),
    style_table={'maxWidth': '75%',
                 'marginLeft': 'auto',
                 'marginRight': 'auto'
                 },
    style_cell={'textAlign': 'center',
                'padding': '7px',
                'font_size': '16px',
                'font_family': 'Arial'
                },
    style_header={'backgroundColor': 'grey',
                  'fontWeight': 'bold',
                  'color': 'white',
                  'font_size': '18px'
                  },
    sort_action='native',
    sort_mode='multi',
    sort_by=[]
)

app.layout = html.Div(children=[
    html.H4("Delt Fantasy Football Standings",
            style={'textAlign': 'center',
                   'font_family': 'Arial',
                   'padding': '0px'
                   }
            ),

    html.Div([html.H6("Choose Week: ",
                      style={'marginLeft': 'auto', 'marginRight': 'auto',
                             'display': 'inline-block',
                             'verticalAlign': 'middle'
                             }
                      ),
              standings_table_dropdown
              ],
             style={'textAlign': 'center',
                    'margin-right': '0px',
                    'margin-left': '150px'
                    }
             ),

    standings_table,
])

@app.callback(Output('standings-table', 'data'),
              [Input('standings-table-dd', 'value')])
def update_standings_table(week_number):
    dff_for_standings_table = create_df_for_standings_table(week_number)

    return dff_for_standings_table.to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True)
