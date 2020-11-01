# https://dash.plotly.com/layout

# https://opensource.com/article/18/1/step-step-guide-git
from create_ff_standings import *
from get_week_number import *
import dash
import dash_table

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

if __name__ == '__main__':
    # for_week_number = get_current_week_number()
    for_week_number = 7

    df_current_standings = get_current_standings(for_week_number)

    app = dash.Dash(__name__)

    server = app.server

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

    app.run_server(debug=True)

