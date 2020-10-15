# https://dash.plotly.com/layout

import dash
import dash_table
import pandas as pd

def get_standings(week_number):
    # file_dir = '/home/cdelong/python_projects/ff_web_app/delt_ff_standings/weekly_standings_csvs/Delt_2020_Week2_Standings.csv'
    file_dir = '/home/cdelong/python_projects/ff_web_app/delt_ff_standings/weekly_standings_csvs/Delt_2020_Week' + str(week_number) + '_Standings.csv'

    pd.options.display.max_columns = None
    pd.options.display.width = None

    df_current_standings = pd.read_csv(file_dir)
    # df_current_standings = df_current_standings[['week_number', 'full_name', 'standings',
    #                                              'cum_total_wins', 'score', 'all_play_wins', 'cum_score',
    #                                              'cum_all_play_wins', 'manual_nickname']]

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

    df_current_standings = df_current_standings[['Rank', 'Team', 'W-L-T', 'Points Scored', 'All Play Wins']]

    return df_current_standings

df_current_standings = get_standings(4)

# Points against? need to add cum of score_opp
# print(df_current_standings)

app = dash.Dash(__name__)

app.layout = dash_table.DataTable(
    id='table'
    , columns=[{"name": i, "id": i} for i in df_current_standings.columns]
    , data=df_current_standings.to_dict('records')
    , style_cell={'textAlign': 'center', 'padding': '5px'}
    , style_header={
        'backgroundColor': 'grey'
        , 'fontWeight': 'bold'
    }
    # , style_cell_conditional=[
    #     {
    #         'if': {'column_id': 'Rank'},
    #         'textAlign': 'center'
    #     }
    # ]
    # , style_as_list_view=True
)

if __name__ == '__main__':
    app.run_server(debug=True)