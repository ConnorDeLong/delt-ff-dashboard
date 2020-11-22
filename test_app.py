import create_ff_standings
import get_week_number
import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

# pull the entire processed Week/Team level dataframe
df_standings = create_ff_standings.create_final_standings()

print(df_standings['cum_score'])