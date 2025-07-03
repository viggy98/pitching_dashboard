# Pitching dashboard
Pybaseball pitching dashboard via streamlit

View the dashboard here: https://pybaseball-pitching.streamlit.app/

The dashboard pulls in all statcast pitching data as of the day prior. First type in any pitcher (some suggestions include Clayton Kershaw, Max Scherzer, Jacob deGrom) and either hit most recent game to pull up data on their recent game or input a start and date range to select all pitches between those two dates.

On the legend of the strike zone chart, you can select the pitch to filter only for those types of pitches. 

# Statistics:
### WHIP/9:
Walks and hits per 9 innings. Gives an extrapolated performance on how well a batter is able to perform against a pitcher (or how poorly a pitcher is performing) over a 9 inning game. The higher the WHIP/9, the worse the performance. Useful to normalize pitcher performance as different pitchers will pitch a different number of innings on a given day. MLB AVG WHIP/9: 11.7
### K/9: 
Strikeouts per 9 innings. Gives an extrapolated performance on effective a pitchers performance is over a full game based on their days performance. Useful to normalize pitcher performance as different pitchers will pitch a different number of innings on a given day. MLB Avg KO/9: 8
