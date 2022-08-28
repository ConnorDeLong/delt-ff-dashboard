
import pandas as pd
import numpy as np
from create_team_data import create_initial_team_data

df_teams = create_initial_team_data()
df_teams = df_teams.loc[df_teams['seasonId'] == 2022].reset_index()

np.random.seed(20220828)

rand = np.random.rand(10)

df_rand = pd.DataFrame(rand, columns=['rand'])

df_teams = df_teams.join(df_rand)
df_teams = df_teams.sort_values(by='rand').reset_index()

df_teams['order'] = df_teams.index + 1

print(df_teams[['full_name', 'order']])