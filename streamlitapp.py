import pandas as pd
import numpy as np
from pybaseball import statcast, statcast_batter, statcast_pitcher, playerid_lookup, player_search_list, playerid_reverse_lookup
from helper import strike_charter, name_splitter, batter_no, whip9, k9, agg_whip_9, agg_ko_9
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from datetime import date, datetime
import datetime as dt
import plotly.express as px
        

st.title("Strike Zone Visualization")
st.sidebar.header("Pitcher Search")



pitcher_name = st.sidebar.text_input("Player Name")
start_date = st.sidebar.text_input("Start Date")
end_date = st.sidebar.text_input("End Date")

most_recent = st.sidebar.button("Most Recent Game")
date_range = st.sidebar.button("Date Range")

if not most_recent and not date_range:
    st.info("Please pick a pitcher and date range, then click a date option.")
    st.stop()

first_name, last_name = name_splitter(pitcher_name)

if most_recent:
    with st.spinner("Looking up pitcher ID and Statcast data..."):
        try:
            lookup_df = playerid_lookup(last_name, first_name)
            if lookup_df.empty:
                st.error("Pitcher not found")
            else:
                
                saver = statcast_pitcher(start_dt = '1900-01-01',  end_dt = datetime.today().strftime('%Y-%m-%d'), player_id = lookup_df['key_mlbam'].iloc[0])
                saver['game_date'] = pd.to_datetime(saver['game_date'], format = '%Y-%m-%d')
                if len(saver.index) == 0:
                    st.error("Pitcher not found")
                else:
                    saver = saver.loc[saver['game_date'].dt.year == max(saver['game_date'].dt.year)]
                    saver['events'] = np.where(saver['events'].isnull(),"mid at-bat", saver['events'])
                    saver2 = saver.loc[saver['game_date'] == max(saver['game_date'])]
                    last_game_date = saver2.game_date.iloc[0].strftime('%Y-%m-%d')
                    num_pitches = len(saver2.index)
                    whip_last = whip9(saver2)
                    
                    ko_last = k9(saver2)
                    
                    num_strikes = saver2.loc[saver2['type'] == 'S'].shape[0]
                    strk_pct = (num_strikes / num_pitches) * 100 
                    num_balls = saver2.loc[saver2['type'] == 'B'].shape[0]
                    ball_pct = (num_balls / num_pitches) * 100
                    in_play = saver2.loc[saver2['type'] == 'X'].shape[0]
                    in_play_pct = (in_play / num_pitches) * 100

                    
                    st.success(f"✅ Last pitched on: **{last_game_date}**")
                    st.metric(label = "Total Pitches Thrown", value=num_pitches)
                    st.metric(label=f"WHIP/9 on {last_game_date}", value=round(agg_whip_9(whip9(saver2)), 2))
                    st.metric(label=f"KO/9 on {last_game_date}", value=round(agg_ko_9(k9(saver2)), 2))
                    st.markdown(f"**{strk_pct:.1f}%** of pitches are strikes ({num_strikes}/{num_pitches})")
                    st.markdown(f"**{ball_pct:.1f}%** of pitches are balls ({num_balls}/{num_pitches})")
                    st.markdown(f"**{in_play_pct:.1f}%** of pitches are in play ({in_play}/{num_pitches})")
                    saver2['description'] = saver2['description'].astype(str).str.strip().str.lower()
                    saver2['description'] = np.where(saver2['description'].str.contains('foul'), 'foul', saver2['description'])
                    saver2['description'] = np.where(saver2['description'].str.contains('ball'), 'ball', saver2['description'])
                    
                    pitch_df = saver2[['plate_x','plate_z','pitch_name','description','release_speed','events']].dropna()
                    fig = strike_charter(pitch_df = pitch_df, last_game_date = last_game_date)
                    st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
       
            st.error(f"Something went wrong: {e}")
    with st.spinner("Performance today relative to rest of season..."):
        try:
            whip = whip9(saver)
            fig = px.line(
            whip,
            x="game_date",
            y="whip9",
            markers=True,
            title="WHIP/9 (Walks and hits per 9 )",
            labels={"whip9": "WHIP/9", "game_date": "Game Date"}
        )
            fig.add_shape(
                type="line",  # Specify the shape type as 'line'
                y0=11.7,
                y1=11.7,
                x0=whip.game_date.min(),
                x1=whip.game_date.max(),    
                showlegend = True,
                name = 'MLB Average WHIP/9',
                line=dict(    # Define line properties
                    color="red",
                    width=2,
                    dash="dash"  # Optional: 'solid', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot'
                )
            )
            fig.update_layout(
                
            yaxis=dict(range=[0, max(whip['whip9'].max() + 5, 40)]),
                
            height=500,
                legend={"x": 1.05, "y": 1},
            margin={"r": 50}  # make room for legend
                    )
        
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Something went wrong: {e}")
    with st.spinner("Performance today relative to rest of season..."):
        try:
            strk_9 = k9(saver)
            fig = px.line(
            strk_9,
            x="game_date",
            y="ko9",
            markers=True,
            title="KO/9 (Strike Outs per 9 innings)",
            labels={"ko9": "KO/9", "game_date": "Game Date"}
        )
            fig.add_shape(
                type="line",  # Specify the shape type as 'line'
                y0=8,
                y1=8,
                x0=strk_9.game_date.min(),
                x1=strk_9.game_date.max(),    
                showlegend = True,
                name = 'MLB Average KO/9',
                line=dict(    # Define line properties
                    color="red",
                    width=2,
                    dash="dash"  # Optional: 'solid', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot'
                )
            )
            fig.update_layout(
                
            yaxis=dict(range=[0, max(strk_9['ko9'].max()+2, 20)]),
                
            height=500,
                legend={"x": 1.05, "y": 1},
            margin={"r": 50}  # make room for legend
                    )
        
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Something went wrong: {e}")

if date_range:
    try:
        if start_date >= end_date:
            st.error("Start date must be **before** end date.")

        with st.spinner("Looking up pitcher ID and Statcast data..."):
            lookup_df = playerid_lookup(last_name, first_name)
            if lookup_df.empty:
                st.error("Pitcher not found")
            else:
                
                saver = statcast_pitcher(start_dt = start_date,  end_dt = end_date, player_id = lookup_df['key_mlbam'].iloc[0])
                saver['game_date'] = pd.to_datetime(saver['game_date'], format = '%Y-%m-%d')
                if len(saver.index) == 0:
                    st.error("Pitcher not found")
                else:
                    
                    last_game_date = max(saver.game_date).strftime(format = '%Y-%m-%d')
                    num_pitches = len(saver.index)
                    whip_last = whip9(saver)
                    
                    ko_last = k9(saver)
                    num_strikes = saver.loc[saver['type'] == 'S'].shape[0]
                    strk_pct = (num_strikes / num_pitches) * 100 
                    num_balls = saver.loc[saver['type'] == 'B'].shape[0]
                    ball_pct = (num_balls / num_pitches) * 100
                    in_play = saver.loc[saver['type'] == 'X'].shape[0]
                    in_play_pct = (in_play / num_pitches) * 100
                    
                    st.success(f"✅ Last pitched on: **{last_game_date}**")
                    st.metric(label = f"Total Pitches between {start_date} and {end_date}:", value=num_pitches)
                    st.metric(label=f"WHIP/9 between {start_date} and {end_date}", value=round(agg_whip_9(whip_last),2))
                    st.metric(label=f"KO/9 between {start_date} and {end_date}", value=round(agg_ko_9(ko_last),2))
                    st.markdown(f"**{strk_pct:.1f}%** of pitches are strikes ({num_strikes}/{num_pitches})")
                    st.markdown(f"**{ball_pct:.1f}%** of pitches are balls ({num_balls}/{num_pitches})")
                    st.markdown(f"**{in_play_pct:.1f}%** of pitches are in play ({in_play}/{num_pitches})")
                    saver['description'] = saver['description'].astype(str).str.strip().str.lower()
                    saver['description'] = np.where(saver['description'].str.contains('foul'), 'foul', saver['description'])
                    saver['description'] = np.where(saver['description'].str.contains('ball'), 'ball', saver['description'])
                    saver['events'] = np.where(saver['events'].isnull(),"mid at-bat", saver['events'])
                    pitch_df = saver[['plate_x','plate_z','pitch_name','description','release_speed','events']]
                    fig = strike_charter(pitch_df = pitch_df, start_date = start_date, end_date = end_date)
                    st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Something went wrong: {e}")

    with st.spinner(f"WHIP/9 between {start_date} and {end_date}:"):

        try:
            whip = whip9(saver)
            fig = px.line(
            whip,
            x="game_date",
            y="whip9",
            markers=True,
            title="WHIP/9 (Walks and hits per 9 )",
            labels={"whip9": "WHIP/9", "game_date": "Game Date"}
        )
            fig.add_shape(
                type="line",  # Specify the shape type as 'line'
                y0=11.7,
                y1=11.7,
                x0=whip.game_date.min(),
                x1=whip.game_date.max(),    
                showlegend = True,
                name = 'MLB Average WHIP/9',
                line=dict(    # Define line properties
                    color="red",
                    width=2,
                    dash="dash"  # Optional: 'solid', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot'
                )
            )
            fig.update_layout(
                
            yaxis=dict(range=[0, max(whip['whip9'].max() + 5, 40)]),
                
            height=500,
                legend={"x": 1.05, "y": 1},
            margin={"r": 50}  # make room for legend
                    )
        
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Something went wrong: {e}")

    with st.spinner("Performance today relative to rest of season..."):
        try:
            strk_9 = k9(saver)
            fig = px.line(
            strk_9,
            x="game_date",
            y="ko9",
            markers=True,
            title="KO/9 (Strike Outs per 9 innings)",
            labels={"ko9": "KO/9", "game_date": "Game Date"}
        )
            fig.add_shape(
                type="line",  # Specify the shape type as 'line'
                y0=8,
                y1=8,
                x0=strk_9.game_date.min(),
                x1=strk_9.game_date.max(),    
                showlegend = True,
                name = 'MLB Average KO/9',
                line=dict(    # Define line properties
                    color="red",
                    width=2,
                    dash="dash"  # Optional: 'solid', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot'
                )
            )
            fig.update_layout(
                
            yaxis=dict(range=[0, max(strk_9['ko9'].max()+2, 20)]),
                
            height=500,
                legend={"x": 1.05, "y": 1},
            margin={"r": 50}  # make room for legend
                    )
        
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Something went wrong: {e}")


    



