import streamlit as st
from functions import *

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    data = json.load(uploaded_file)
    refactored_data = refactor_match_data(data)
    df = prepare_dataframe(refactored_data)
    
    df = df.groupby(['matchID','playerName', 'side'], as_index=False)[['kills','wasKilled', 'wasAce', 'wasNinja', 'headshots','onetaps', 'clutch', 'noscopes', 'lookingaway', 'trade_kills', 'activity']].sum()

    df['KD_Ratio'] = df['kills'] / df['wasKilled']
    df['KHS_Ratio'] = df['headshots'] / df['kills']
    df['ONE_Ratio'] = df['onetaps'] / df['kills']

    df['kills_norm'] = (df['KD_Ratio'] - df['KD_Ratio'].min()) / (df['KD_Ratio'].max() - df['KD_Ratio'].min())
    df['khs_norm'] = (df['KHS_Ratio'] - df['KHS_Ratio'].min()) / (df['KHS_Ratio'].max() - df['KHS_Ratio'].min())
    df['onetaps_norm'] = (df['ONE_Ratio'] - df['ONE_Ratio'].min()) / (df['ONE_Ratio'].max() - df['ONE_Ratio'].min())
    df['ninja_norm'] = (df['wasNinja'] - df['wasNinja'].min()) / (df['wasNinja'].max() - df['wasNinja'].min())
    df['ace_norm'] = (df['wasAce'] - df['wasAce'].min()) / (df['wasAce'].max() - df['wasAce'].min())
    df['noscope_norm'] = (df['noscopes'] - df['noscopes'].min()) / (df['noscopes'].max() - df['noscopes'].min())

    st.bar_chart(df.sort_values('KD_Ratio'), x="playerName", y=["KD_Ratio"])
    st.dataframe(df.sort_values('KD_Ratio'))