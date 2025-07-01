import pandas as pd
import numpy as np
from pybaseball import statcast, statcast_batter, statcast_pitcher, playerid_lookup, player_search_list, playerid_reverse_lookup
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from datetime import date, datetime
import datetime as dt
import plotly.express as px

def strike_charter(pitch_df, start_date = None, end_date = None, last_game_date=None):
    if start_date is None:
        
        
        fig = px.scatter(
                pitch_df,
                x="plate_x", y="plate_z",
                color="pitch_name",
                hover_data=["pitch_name", "release_speed", "events", "pitch_name","description"],
                title=f"Pitch Locations on {last_game_date}",
                    
                labels={"plate_x": "Horizontal (ft)", "plate_z": "Vertical (ft)"}
            )
            # add dashed strike zone
        fig.update_traces(
            customdata=pitch_df[["pitch_name", "release_speed", "description","events"]],
            hovertemplate=(
                "<b>Pitch:</b> %{customdata[0]}<br>"
                "<b>Speed:</b> %{customdata[1]}<br>"
                "<b>Description:</b> %{customdata[2]}<br>"
                "<b>Result:</b> %{customdata[3]}<extra></extra>"
                
            )
        )
    
        # add dashed strike zone rectangle & push legend to right
        fig.update_layout(
            shapes=[{
                "type": "rect",
                "x0": -0.83, "x1": 0.83,
                "y0": 1.5, "y1": 3.25,
                "line": {"color": "red", "width": 2, "dash": "dash"}
            }],
            width = 600,
            height = 800,
            xaxis={"range": [-2, 2]},
            yaxis={"range": [0, 5]},
            legend={"x": 1.05, "y": 1},
            margin={"r": 200}  # make room for legend
        )
        return fig
    else:
        
        fig = px.scatter(
                pitch_df,
                x="plate_x", y="plate_z",
                color="pitch_name",
                hover_data=["pitch_name", "release_speed", "events", "pitch_name","description"],
                title=f"Pitch Locations {start_date} ➞ {end_date}",
                    
                labels={"plate_x": "Horizontal (ft)", "plate_z": "Vertical (ft)"}
            )
            # add dashed strike zone
        fig.update_traces(
            customdata=pitch_df[["pitch_name", "release_speed", "description","events"]],
            hovertemplate=(
                "<b>Pitch:</b> %{customdata[0]}<br>"
                "<b>Speed:</b> %{customdata[1]} mph<br>"
                "<b>Description:</b> %{customdata[2]} <br>"
                "<b>Result:</b> %{customdata[3]}<extra></extra>"
                
            )
        )
    
        # add dashed strike zone rectangle & push legend to right
        fig.update_layout(
            shapes=[{
                "type": "rect",
                "x0": -0.83, "x1": 0.83,
                "y0": 1.5, "y1": 3.25,
                "line": {"color": "red", "width": 2, "dash": "dash"}
            }],
            width = 600,
            height = 800,
            xaxis={"range": [-2, 2]},
            yaxis={"range": [0, 5]},
            legend={"x": 1.05, "y": 1},
            margin={"r": 200}  # make room for legend
        )
        return fig

        

def name_splitter(user_entry):
    x = user_entry.split()
    last_name = x[1]
    first_name = x[0]
    return first_name, last_name

def batter_no(df):
    df['batter_no'] = df['inning'] * 3 + df['outs_when_up'] - 3
    df['batter_no'] = np.where((df['inning'] == 1) & (df['outs_when_up'] == 0), 1, df['batter_no'])
    df['batter_no'] = np.where((df['inning'] == 1) & (df['outs_when_up'] == 1), 2, df['batter_no'])
    return df

def whip9(df):
    df['game_date'] = pd.to_datetime(df['game_date'], format = '%Y-%m-%d')
    finalDf = pd.DataFrame(columns = ['game_date','hits','total_batters','per9','whip9'])
    for element in df['game_date'].unique():
        tempDf = df.loc[(df['game_date'] == element)]
        tempDf2 = tempDf.loc[(tempDf['events'].isin(["single","double","triple","home_run","walk"]))]
        hits = tempDf2.events.isin(
            ["single","double","triple","home_run","walk"]).shape[0]
        tempDf['batter_no'] = tempDf['inning'] * 3 + tempDf['outs_when_up'] - 3
        tempDf['batter_no'] = np.where((tempDf['inning'] == 1) & (tempDf['outs_when_up'] == 0), 1, tempDf['batter_no'])
        tempDf['batter_no'] = np.where((tempDf['inning'] == 1) & (tempDf['outs_when_up'] == 1), 2, tempDf['batter_no'])
        tot_batters = (tempDf['batter_no'].max() - tempDf['batter_no'].min()) + 1
        per9 = 27 / tot_batters
        whip9 = hits * per9
        perGame = [element, hits, tot_batters, per9, whip9]
        finalDf.loc[len(finalDf)] = perGame
    finalDf['whip9'] = round(finalDf['whip9'],2)
    return finalDf
    
def k9(df):
    df['game_date'] = pd.to_datetime(df['game_date'], format = '%Y-%m-%d')
    finalDf = pd.DataFrame(columns = ['game_date','ko','total_batters','per9','ko9'])
    for element in df['game_date'].unique():
        tempDf = df.loc[(df['game_date'] == element)]
        tempDf2 = tempDf.loc[(tempDf['events'].isin(["strikeout"]))]
        ko = tempDf2.events.isin(["strikeout"]).shape[0]
        tempDf['batter_no'] = tempDf['inning'] * 3 + tempDf['outs_when_up'] - 3
        tempDf['batter_no'] = np.where((tempDf['inning'] == 1) & (tempDf['outs_when_up'] == 0), 1, tempDf['batter_no'])
        tempDf['batter_no'] = np.where((tempDf['inning'] == 1) & (tempDf['outs_when_up'] == 1), 2, tempDf['batter_no'])
        tot_batters = (tempDf['batter_no'].max() - tempDf['batter_no'].min()) + 1
        per9 = 27 / tot_batters
        ko9 = ko * per9
        perGame = [element, ko, tot_batters, per9, ko9]
        finalDf.loc[len(finalDf)] = perGame
    finalDf['ko9'] = round(finalDf['ko9'],2)
    return finalDf

def agg_whip_9(df):
    return float(df['whip9'].mean())
def agg_ko_9(df):
    return float(df['ko9'].mean())