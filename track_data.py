from operator import index
import fastf1
import numpy as np
import matplotlib as mpl
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
import altair as alt
from altair_saver import save

fastf1.Cache.enable_cache("C:\\Cachef1")  # replace with your cache directory

##############################################################################
# First, we define some variables that allow us to conveniently control what
# we want to plot.
year = 2021
wknd = 2
ses = "Q"
driver = "VER"
colormap = mpl.cm.plasma


##############################################################################
# Next, we load the session and select the desired data.
# i = 1
# while i <= 2:
# i = i + 1
for i in range(1,20):
    session = fastf1.get_session(2021, i, "Q")
    laps = session.load_laps(with_telemetry=True)
    drivers = pd.unique(laps["Driver"])
    list_fastest_laps = list()
    counter = 1
    for drv in drivers:
        if counter == 1:
            current_fastest_driver = laps.pick_driver(drv).pick_fastest()
            fastestlap = laps.pick_driver(drv).pick_fastest()["LapTime"]
            best_driver = laps.pick_driver(drv).pick_fastest()["Driver"]
        else:
            try:
                if laps.pick_driver(drv).pick_fastest()["LapTime"] <= fastestlap:
                    fastestlap = laps.pick_driver(drv).pick_fastest()["LapTime"]
                    best_driver = laps.pick_driver(drv).pick_fastest()["Driver"]
                else:
                    pass
            except:
                pass
        counter = counter + 1
    print(session.weekend.name +" fastest lap is "+best_driver +" with time "+ str(fastestlap))
fastest_lap_data = laps.pick_driver(best_driver).pick_fastest()


# lap = laps.pick_driver("HAM").pick_fastest()
# lap.telemetry.to_excel('test.xlsx')

df = fastest_lap_data.telemetry
df = pd.DataFrame(df)
df = df[df["Source"] == "car"].reset_index(drop=True)
df = df[
    [
        "Date",
        "RPM",
        "Speed",
        "nGear",
        "Throttle",
        "Brake",
        "DRS",
        "Distance",
        "X",
        "Y",
        "Z",
    ]
]

df["normalizedspeed"] = df["Speed"].rolling(window=4, min_periods=1).mean()
df["STR_COR_basedonSpeed"] = np.where(
    (df["normalizedspeed"].shift(1) - df["normalizedspeed"]) > 3, 1, 0
)

# Change the order of data in order to identify the big straight
df["Index"] = df.index
first_corner = (
    df[df["STR_COR_basedonSpeed"] == 1]
    .groupby(["STR_COR_basedonSpeed"])["Index"]
    .min()
    .sum()
)
df["Index"] = np.where(
    df["Index"] < first_corner, df["Index"] + df["Index"].max(), df["Index"]
)
df = df.sort_values(by=["Index"]).reset_index(drop=True)
del df["Index"]
df["No"] = df.index
##########
df["counter_straights"] = np.nan
df["counter_corners"] = np.nan

for index, rows in df.iterrows():
    if df.loc[index, "No"] == 0:
        if df.loc[index, "STR_COR_basedonSpeed"] == 0:
            df.at[index, "counter_straights"] = 1
            df.at[index, "counter_corners"] = 0
            x = 1
        elif df.loc[index, "STR_COR_basedonSpeed"] == 1:
            df.at[index, "counter_straights"] = 0
            df.at[index, "counter_corners"] = 1
            x = 2
    elif df.loc[index, "STR_COR_basedonSpeed"] == previous_STR_COR_basedonSpeed:
        df.at[index, "counter_straights"] = previous_counter_straights
        df.at[index, "counter_corners"] = previous_counter_corners
        x = 3
    elif df.loc[index, "STR_COR_basedonSpeed"] == 1:
        df.at[index, "counter_straights"] = previous_counter_straights
        df.at[index, "counter_corners"] = previous_counter_corners + 1
        x = 4
    elif df.loc[index, "STR_COR_basedonSpeed"] == 0:
        df.at[index, "counter_straights"] = previous_counter_straights + 1
        df.at[index, "counter_corners"] = previous_counter_corners
        x = 5
    previous_STR_COR_basedonSpeed = df.loc[index, "STR_COR_basedonSpeed"]
    previous_counter_straights = df.loc[index, "counter_straights"]
    previous_counter_corners = df.loc[index, "counter_corners"]
    df.at[index, "check"] = x

df["_Full_Throttle"] = np.where(df["Throttle"] >= 100, 1, 0)

corners = "STR_COR_basedonSpeed"

lap_new = df

import altair as alt
from vega_datasets import data

domain = [0, 1]
Colours = ["#028A0F", "#B90E0A"]

chart = (
    alt.Chart(df)
    .mark_circle()
    .encode(
        alt.X("X", scale=alt.Scale(zero=False), axis=None),
        alt.Y("Y", scale=alt.Scale(zero=False), axis=None),
        order="No",
        color=alt.Color(
            "STR_COR_basedonSpeed",
            scale=alt.Scale(domain=domain, range=Colours),
            legend=None,
        ),
    )
    .configure_axis(grid=False)
    .configure_view(strokeWidth=0)
    .properties(title=weekend.name)
    .configure_title(fontSize=20, anchor="middle", color="#404040")
)
chart.display()
