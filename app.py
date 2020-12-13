# https://dash.plotly.com/layout

# https://opensource.com/article/18/1/step-step-guide-git
import create_ff_standings
import get_week_number
import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

for_rank_metrics_by_week_range = {'1-4': [['cum_total_wins', 'cum_score'], [False, False]],
                                  '5-6': [['cum_all_play_wins', 'cum_score'], [False, False]],
                                  '7-12': [['cum_total_wins', 'cum_score'], [False, False]]}

df_standings = create_ff_standings.create_final_standings(rank_metrics_by_week_range=for_rank_metrics_by_week_range)

# add string versions of the score metrics so that they can be formatted correctly
df_standings['cum_score_str'] = df_standings['cum_score'].map('{:,.2f}'.format)
df_standings['cum_score_opp_str'] = df_standings['cum_score_opp'].map('{:,.2f}'.format)
df_standings['cum_score_per_week_str'] = df_standings['cum_score_per_week'].map('{:,.2f}'.format)
df_standings['cum_score_opp_per_week_str'] = df_standings['cum_score_opp_per_week'].map('{:,.2f}'.format)
df_standings['cum_all_play_wins_per_week_str'] = df_standings['cum_all_play_wins_per_week'].map('{:,.1f}'.format)

# Used to create names for the table displayed in the app
dict_columns_w_table_names = {'standings': 'Rank', 'manual_nickname': 'Team', 'cum_score_str': 'Points Scored',
                              'cum_wlt': 'W-L-T', 'cum_all_play_wlt_int': 'All Play W-L-T',
                              'cum_score_per_week_str': 'Points Scored/Week',
                              'cum_all_play_wins_per_week_str': 'All Play Wins/Week',
                              'cum_score_opp_str': 'Points Against',
                              'cum_score_opp_per_week_str': 'Points Against/Week'}

# The standings table contains several metrics that are formatted as strings (e.g. W-L-T). In order to properly
# sort these, this dictionary contains a mapping between the variables used in the standings table (key)
# and the associated variables to sort with (value) IF NEEDED.
# Note that the key uses the original dataframe names and NOT the table's names
dict_sort_table_variables = {'cum_wlt': 'cum_wins', 'cum_all_play_wlt_int': 'cum_all_play_wins',
                             'cum_score_str': 'cum_score', 'cum_score_opp_str': 'cum_score_opp',
                             'cum_score_per_week_str': 'cum_score_per_week',
                             'cum_score_opp_per_week_str': 'cum_score_opp_per_week'}

def create_df_for_standings_table(df_final, week_number, new_col_names=dict_columns_w_table_names, sort_dict=None):
    """ Create dataframe used in the dashboard """
    if sort_dict is None:
        sort_dict = {'sort_values': ['standings'], 'sort_asc': ['True']}

    df_current_standings = df_final.loc[df_final['week_number'] == week_number]

    df_current_standings = df_current_standings.sort_values(sort_dict['sort_values'],
                                                            ascending=sort_dict['sort_asc'], inplace=False)

    final_keep_vars = ['standings', 'manual_nickname', 'cum_wlt', 'cum_score_str', 'cum_score_opp_str',
                       'cum_all_play_wlt_int', 'cum_score_per_week_str', 'cum_score_opp_per_week_str',
                       'cum_all_play_wins_per_week_str']
    df_current_standings = df_current_standings[final_keep_vars]

    df_current_standings.rename(columns=new_col_names, inplace=True)

    return df_current_standings


# ensures the table only displays regular season standings
current_week_number = get_week_number.get_current_week_number()
if current_week_number > 13:
    current_week_number = 13

df_for_standings_table = create_df_for_standings_table(df_standings, current_week_number)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# external_stylesheets = [dbc.themes.FLATLY]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# this is necessary for the Dash app to run in Heroku
server = app.server

standings_table_dropdown = dcc.Dropdown(
    id='standings-table-dd',
    options=[{'label': f"Week {week_number}", 'value': week_number}
             for week_number in range(1, current_week_number + 1)],
    value=current_week_number,
    clearable=False,
    style={
        # 'width': '30%',
        #    'margin-left': '-75px',
        #    'margin-right': '0px',
        #    'font_family': 'Arial',
        #    'display': 'inline-block',
        #    'verticalAlign': 'middle',
        #    'text-align': 'center',

        'width': '90px',
        'font_family': 'Arial',
        'display': 'inline-block',
        'verticalAlign': 'middle',
        'text-align': 'center',
           }
)

standings_table = dash_table.DataTable(
    id='standings-table',
    columns=[{"name": i, "id": i} for i in df_for_standings_table.columns],
    data=df_for_standings_table.to_dict('records'),
    style_table={'maxWidth': '1000px',
                 # 'maxWidth': '75%',
                 'marginLeft': 'auto',
                 'marginRight': 'auto'
                 },
    style_cell={'textAlign': 'center',
                'padding': '7px',
                'font_size': '16px',
                'font_family': 'Arial'
                },
    style_header={'backgroundColor': 'purple',
                  'fontWeight': 'bold',
                  'color': 'gold',
                  'font_size': '18px',
                  'height': 'auto',
                  'whiteSpace': 'normal'
                  },
    style_cell_conditional=[
        {'if': {'column_id': 'Rank'},
         'width': '10%'},
        {'if': {'column_id': 'Team'},
         'width': '13%'},
        {'if': {'column_id': 'W-L-T'},
         'width': '11%'},
        {'if': {'column_id': 'Points Scored'},
         'width': '11%'},
        {'if': {'column_id': 'Points Against'},
         'width': '11%'},
        {'if': {'column_id': 'All Play W-L-T'},
         'width': '11%'},
        {'if': {'column_id': 'Points Scored/Week'},
         'width': '11%'},
        {'if': {'column_id': 'Points Against/Week'},
         'width': '11%'},
        {'if': {'column_id': 'All Play Wins/Week'},
         'width': '11%'},
    ],
    sort_action='custom',
    sort_mode='multi',
    sort_by=[]
)

app.layout = html.Div(children=[
    html.H4("Delt Fantasy Football Standings",
            style={'textAlign': 'center',
                   'font_family': 'Arial',
                   'padding': '0px',
                   }
            ),

    html.Div([html.H6("Choose Week: ",
                      style={'display': 'inline-block',
                             # 'marginLeft': 'auto', 'marginRight': 'auto',
                             'verticalAlign': 'middle'
                             }
                      ),
              standings_table_dropdown
              ],
             style={'textAlign': 'center',
                    'verticalAlign': 'middle'
                    # 'margin-right': '0px',
                    # 'margin-left': '150px'

                    # 'margin-right': 'auto',
                    # 'margin-left': 'auto'
                    # 'display': 'inline-block',
                    # 'horizonatlAlign': 'middle',
                    # 'width': '100%'
                    }
             ),

    standings_table,
])

@app.callback(Output('standings-table', 'data'),
              [Input('standings-table', 'sort_by'),
               Input('standings-table-dd', 'value')])
def sort_table_standings(sort_by, week_number, dict_sort_table_variables=dict_sort_table_variables):
    # note that the sort_by property is a list of dictionaries with the following form:
    # {'column_id': <column_name>, 'direction': <'ascending' or 'descending'>}

    # create a list of the table's sort variables
    initial_sort_values = [col['column_id'] for col in sort_by]

    # break out the table name dictionary into lists containing the keys and values
    keys_columns_w_table_names = list(dict_columns_w_table_names.keys())
    values_columns_w_table_names = list(dict_columns_w_table_names.values())

    # create a list containing the original dataframe names of the sort variables
    converted_sort_values = []
    for initial_sort_value in initial_sort_values:
        converted_sort_value = keys_columns_w_table_names[values_columns_w_table_names.index(initial_sort_value)]
        converted_sort_values.append(converted_sort_value)

    # create lists of the current sort values and their associated directions
    sort_asc = [col['direction'] == 'asc'for col in sort_by]
    sort_values = [dict_sort_table_variables[converted_sort_value] if converted_sort_value
                   in list(dict_sort_table_variables) else converted_sort_value
                   for converted_sort_value in converted_sort_values]

    sort_dict = {'sort_values': sort_values, 'sort_asc': sort_asc}

    # create the standings table data sorted by the table's sort variables
    if len(sort_values):
        dff_for_standings_table = create_df_for_standings_table(df_standings, week_number, sort_dict=sort_dict)
    else:
        dff_for_standings_table = create_df_for_standings_table(df_standings, week_number)

    return dff_for_standings_table.to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True)
