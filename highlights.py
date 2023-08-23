import pandas as pd
import json

#TO-DO 
def get_players_events(match_dataframe, refactored_data):
    events_array = []
    # player Name
    # event Type: highlight/lowlight
    # event Detail: ACE master
    events_array = get_aces_highlight(match_dataframe)
    events_array = events_array+get_most_killer_highlight(match_dataframe)
    events_array = events_array+get_most_efficient_killer(match_dataframe)
    events_array = events_array+get_most_clutchs(match_dataframe)
    events_array = events_array+get_ninja_defuse(match_dataframe)
    events_array = events_array+get_one_tap_king(match_dataframe)
    events_array = events_array+get_headshot_master(match_dataframe)
    #events_array.append()
    #events_array.append(get_most_efficient_killer(match_dataframe))
    #events_array.append(get_most_clutchs(match_dataframe))
    #get_mvp_star(match_dataframe, refactored_data)

    #for event in events_array:
        #print(event[0]+" - "+event[1]+" - "+event[2])
    return events_array

def get_aces_highlight(match_dataframe):
    aces_highlights = []
    for index, row in match_dataframe.loc[match_dataframe['wasAce'] > 0].iterrows():
        aces_highlights.append([
            row['playerName'],
            "highlight",
            str(row['wasAce']) + "x ACE round killed every single enemy"
            ])
    return aces_highlights

def get_most_killer_highlight(match_dataframe):
    most_killers_highlight = []
    match_dataframe = match_dataframe.groupby(['playerName'], as_index=False)['kills'].sum()
    for index, row in match_dataframe[match_dataframe.kills == match_dataframe.kills.max()].iterrows():
        most_killers_highlight.append([
            row['playerName'],
            'highlight',
            'Player with most kills putting '+str(row['kills'])+' enemies down'
        ])
    return most_killers_highlight

def get_most_efficient_killer(match_dataframe):
    most_eficient_players = []
    print(match_dataframe)
    match_dataframe = match_dataframe.groupby(['playerName'], as_index=False)['KD_Ratio'].sum()
    for index, row in match_dataframe[match_dataframe['KD_Ratio'] == match_dataframe['KD_Ratio'].max()].iterrows():
        most_eficient_players.append([
            row['playerName'],
            'highlight',
            'The efficient killer with higher KD ratio of '+str(round(row['KD_Ratio'],2))
        ])
    return most_eficient_players

def get_most_clutchs(match_dataframe):
    most_clutchs = []
    match_dataframe = match_dataframe.groupby(['playerName'], as_index=False)['clutch'].sum()
    for index, row in match_dataframe[match_dataframe['clutch'] == match_dataframe['clutch'].max()].iterrows():
        if row['clutch'] > 0:
            most_clutchs.append([
                row['playerName'],
                'highlight',
                str(row['clutch']) + 'x rounds wons by its clutch'
            ])
    return most_clutchs

def get_ninja_defuse(match_dataframe):
    ninja_defuse_list = []
    match_dataframe = match_dataframe.groupby(['playerName'], as_index=False)['wasNinja'].sum()
    for index, row in match_dataframe[match_dataframe['wasNinja'] == match_dataframe['wasNinja'].max()].iterrows():
        if row['wasNinja'] > 0:
            ninja_defuse_list.append([
                row['playerName'],
                'highlight',
                str(row['wasNinja']) + 'x defused the bomb with more enemies alive (ninja)'
            ])
    return ninja_defuse_list

def get_one_tap_king(match_dataframe):
    one_tap_list = []
    match_dataframe = match_dataframe.groupby(['playerName'], as_index=False)['onetaps'].sum()
    for index, row in match_dataframe[match_dataframe['onetaps'] == match_dataframe['onetaps'].max()].iterrows():
        if row['onetaps'] > 0:
            one_tap_list.append([
                row['playerName'],
                'highlight',
                'One-tap king with '+str(row['onetaps'])+' kills'
            ])
    return one_tap_list

def get_headshot_master(match_dataframe):
    headshot_master_link = []
    match_dataframe = match_dataframe.groupby(['playerName'], as_index=False)['headshots'].sum()
    for index, row in match_dataframe[match_dataframe['headshots'] == match_dataframe['headshots'].max()].iterrows():
        if row['headshots'] > 0:
            headshot_master_link.append([
                row['playerName'],
                'highlight',
                'Aim with higher accuracy of the match with '+str(row['headshots'])+' headshot kills'
            ])
    return headshot_master_link

def get_mvp_star(match_dataframe, refactored_data):
    mvp_star_list = []
    print(match_dataframe)
    match_dataframe['Score'] = (
        match_dataframe.kills_norm + 
        match_dataframe.khs_norm +
        match_dataframe.ace_norm
        )
    return 0 