import pandas as pd

def create_team_data():
    teamId_dict = {
        '2019': [
            [1, "Connor DeLong", "DeLong"],
            [2, "Shawn Fulford", "Fulfi"],
            [3, "Kevin Perelstein", "K-Train"],
            [4, "Mario Bynum", "Mario"],
            [5, "Brendan Elliot", "Brendan"],
            [6, "Josh Nadeau", "Germany"],
            [7, "Keith Kaplan", "Keith"],
            [8, "Jonathan Kaunert", "Jon"],
            [9, "Brock Corsi", "Brock"],
            [10, "Travis Hohman", "Travis"],
            [11, "Keanu Hines", "Keanu"],
            [12, "Matt Fleisher", "Fleish"]
        ],
        '2020': [
            [1, "Connor DeLong", "DeLong"],
            [2, "Shawn Fulford", "Fulfi"],
            [3, "Kevin Perelstein", "K-Train"],
            [4, "Mario Bynum", "Mario"],
            [5, "Brian Solomon", "Solomon"],
            [6, "Josh Nadeau", "Germany"],
            [7, "Keith Kaplan", "Keith"],
            [8, "Jonathan Kaunert", "Jon"],
            [9, "Alex Darr", "Darr"],
            [10, "Travis Hohman", "Travis"],
            [11, "Keanu Hines", "Keanu"],
            [12, "Matt Fleisher", "Fleish"]
        ]
    }

    # Create dataframe versions of the 2019 and 2020 team dictionaries
    team_df_2019 = pd.DataFrame(teamId_dict['2019'], columns=['teamId', 'full_name', 'manual_nickname'])
    team_df_2019['seasonId'] = 2019

    team_df_2020 = pd.DataFrame(teamId_dict['2020'], columns=['teamId', 'full_name', 'manual_nickname'])
    team_df_2020['seasonId'] = 2020

    team_df_all_seasons = pd.concat([team_df_2019, team_df_2020])

    team_df_all_seasons.reset_index(drop=True, inplace=True)

    return team_df_all_seasons

if __name__ == '__main__':
    all_team_df = create_team_data()
    team_df = all_team_df.loc[all_team_df['seasonId'] == 2020]
    print(team_df)
    print(all_team_df)