import fastf1
import numpy as np
import matplotlib as mpl
import pandas as pd
import altair as alt
from sklearn.cluster import KMeans
from yellowbrick.cluster import KElbowVisualizer
from sklearn import preprocessing
from sklearn.preprocessing import OneHotEncoder


def change_initial_position(df):
    df["Index"] = df.index
    first_corner = df[df["str_cor"] == 1].groupby(["str_cor"])["Index"].min().sum()
    df["Index"] = np.where(
        df["Index"] < first_corner, df["Index"] + df["Index"].max(), df["Index"]
    )
    df = df.sort_values(by=["Index"]).reset_index(drop=True)
    del df["Index"]
    return df


def pick_fastest_driver_of_session(laps):
    drivers = pd.unique(laps["Driver"])
    counter = 1
    for drv in drivers:
        if counter == 1:
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
    compound = laps.pick_driver(best_driver).pick_fastest()["Compound"]
    return fastestlap, best_driver, compound


def print_the_best_driver(session, fastestlap, best_driver):
    print(
        session.weekend.name
        + " fastest lap is "
        + best_driver
        + " with time "
        + str(fastestlap)
    )


def load_best_lap(laps, best_driver):
    df = laps.pick_driver(best_driver).pick_fastest().telemetry
    df = pd.DataFrame(df)
    df = df[df["Source"] == "car"].reset_index(drop=True)
    print(df.columns)
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

    return df


def flags_strcor_based_on_normal_speed(df):
    df["normalizedspeed"] = df["Speed"].rolling(window=4, min_periods=1).mean()
    df["str_cor"] = np.where(
        (df["normalizedspeed"].shift(1) - df["normalizedspeed"]) > 3, 1, 0
    )
    df["str_cor"] = np.where(
        (df["str_cor"] == 1)
        & (df["str_cor"].shift(1) != 1)
        & (df["str_cor"].shift(-1) != 1),
        0,
        (df["str_cor"]),
    )
    return df


def order_data(df):
    # Create Order of data
    df["No"] = df.index
    return df


def counter_strcor(df):
    df["counter_straights"] = np.nan
    df["counter_corners"] = np.nan
    for index, rows in df.iterrows():
        if df.loc[index, "No"] == 0:
            if df.loc[index, "str_cor"] == 0:
                df.at[index, "counter_straights"] = 1
                df.at[index, "counter_corners"] = 0
            elif df.loc[index, "str_cor"] == 1:
                df.at[index, "counter_straights"] = 0
                df.at[index, "counter_corners"] = 1
        elif df.loc[index, "str_cor"] == previous_str_cor:
            df.at[index, "counter_straights"] = previous_counter_straights
            df.at[index, "counter_corners"] = previous_counter_corners
        elif df.loc[index, "str_cor"] == 1:
            df.at[index, "counter_straights"] = previous_counter_straights
            df.at[index, "counter_corners"] = previous_counter_corners + 1
        elif df.loc[index, "str_cor"] == 0:
            df.at[index, "counter_straights"] = previous_counter_straights + 1
            df.at[index, "counter_corners"] = previous_counter_corners
        previous_str_cor = df.loc[index, "str_cor"]
        previous_counter_straights = df.loc[index, "counter_straights"]
        previous_counter_corners = df.loc[index, "counter_corners"]
    return df


def track_vizualization(session, df):
    chart = (
        alt.Chart(df)
        .mark_circle()
        .encode(
            alt.X("X", scale=alt.Scale(zero=False), axis=None),
            alt.Y("Y", scale=alt.Scale(zero=False), axis=None),
            order="No",
            color=alt.Color(
                "str_cor",
                scale=alt.Scale(domain=[0, 1], range=["#028A0F", "#B90E0A"]),
                legend=None,
            ),
        )
        .configure_axis(grid=False)
        .configure_view(strokeWidth=0)
        .properties(title=session.weekend.name)
        .configure_title(fontSize=20, anchor="middle", color="#404040")
    )
    chart.display()


def corner_counter_speeds(df):
    corner_analysis = (
        df.groupby("counter_corners")
        .min("Speed")
        .reset_index()[["counter_corners", "Speed"]]
    )

    corner_analysis["grp_corner"] = np.where(
        corner_analysis["Speed"] <= 50,
        "50",
        np.where(
            corner_analysis["Speed"] <= 100,
            "100",
            np.where(
                corner_analysis["Speed"] <= 150,
                "150",
                np.where(
                    corner_analysis["Speed"] <= 200,
                    "200",
                    np.where(
                        corner_analysis["Speed"] <= 250,
                        "250",
                        np.where(
                            corner_analysis["Speed"] <= 300,
                            "300",
                            np.where(corner_analysis["Speed"] <= 350, 350, "error"),
                        ),
                    ),
                ),
            ),
        ),
    )

    corner_analysis = pd.pivot_table(
        corner_analysis, columns="grp_corner", values="counter_corners", aggfunc="count"
    ).reset_index()
    corner_analysis = corner_analysis[[x for x in corner_analysis.columns if "0" in x]]

    corner_analysis_columns = ["cor_" + x for x in corner_analysis.columns if "0" in x]
    corner_analysis.columns = corner_analysis_columns
    return corner_analysis


def straight_counter_speeds(df):
    temp_df = (
        df.groupby("counter_straights")
        .max("Speed")
        .reset_index()[["counter_straights", "Speed"]]
    )

    temp_df["grp_straights"] = np.where(
        temp_df["Speed"] <= 50,
        "50",
        np.where(
            temp_df["Speed"] <= 100,
            "100",
            np.where(
                temp_df["Speed"] <= 150,
                "150",
                np.where(
                    temp_df["Speed"] <= 200,
                    "200",
                    np.where(
                        temp_df["Speed"] <= 250,
                        "250",
                        np.where(
                            temp_df["Speed"] <= 300,
                            "300",
                            np.where(temp_df["Speed"] <= 350, 350, "error"),
                        ),
                    ),
                ),
            ),
        ),
    )

    temp_df = pd.pivot_table(
        temp_df, columns="grp_straights", values="counter_straights", aggfunc="count"
    ).reset_index()
    temp_df = temp_df[[x for x in temp_df.columns if "0" in x]]

    temp_df_columns = ["str_" + x for x in temp_df.columns if "0" in x]
    temp_df.columns = temp_df_columns
    return temp_df


def dataframe_creation(laps, best_driver):
    df = load_best_lap(laps, best_driver)
    df = flags_strcor_based_on_normal_speed(df)
    df = change_initial_position(df)
    df = order_data(df)
    df = counter_strcor(df)
    return df


def retreive_kpis(session, fastestlap, df):
    temporary_df = pd.DataFrame()
    df["_Full_Throttle"] = np.where(df["Throttle"] >= 95, 1, 0)
    distance = df.Distance.max()
    avg_speed = distance / 1000 / float(fastestlap / np.timedelta64(1, "h"))
    max_speed = df.Speed.max()
    perc_full_throttle = df["_Full_Throttle"].sum() / df["_Full_Throttle"].count()
    df_corners = corner_counter_speeds(df)
    df_straights = straight_counter_speeds(df)
    temporary_df = pd.concat([temporary_df, df_corners, df_straights], axis=1)
    temporary_df["perc_full_throttle"] = perc_full_throttle
    temporary_df["distance"] = distance
    temporary_df["max_speed"] = max_speed
    temporary_df["avg_speed"] = avg_speed
    temporary_df["grandprix"] = session.weekend.name
    return temporary_df


def Preparing_df_for_kmeans(df):
    df = df.fillna(0)
    df = df[df["grandprix"] != "Styrian Grand Prix"]
    df = df[
        [
            "grandprix",
            "max_speed",
            "avg_speed",
            "distance",
            "perc_full_throttle",
            "cor_50",
            "cor_100",
            "cor_150",
            "cor_200",
            "cor_250",
            "cor_300",
            "str_150",
            "str_200",
            "str_250",
            "str_300",
            "str_350",
        ]
    ].reset_index(drop=True)
    kmeans_df = df.drop(columns="grandprix")
    columnslist = [
        "cor_50",
        "cor_100",
        "cor_150",
        "cor_200",
        "cor_250",
        "cor_300",
        "str_150",
        "str_200",
        "str_250",
        "str_300",
        "str_350",
    ]

    for col in columnslist:
        kmeans_df[col] = kmeans_df[col].astype("int")
        kmeans_df[col] = kmeans_df[col].astype("category")
    return df, kmeans_df


def onehotencoder_method(kmeans_df):
    onehotcolumns = [
        "cor_50",
        "cor_100",
        "cor_150",
        "cor_200",
        "cor_250",
        "cor_300",
        "str_150",
        "str_200",
        "str_250",
        "str_300",
        "str_350",
    ]
    enc = OneHotEncoder(handle_unknown="ignore")
    kmeans_df = pd.get_dummies(kmeans_df, columns=onehotcolumns)
    return kmeans_df


def minmaxscaler_method(kmeans_df):
    x = kmeans_df.values
    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(x)
    kmeans_df = pd.DataFrame(x_scaled)
    return kmeans_df


def track_vizualization_byCluster(df, track):
    chart = (
        alt.Chart(df)
        .mark_circle()
        .encode(
            alt.X("X", scale=alt.Scale(zero=False), axis=None),
            alt.Y("Y", scale=alt.Scale(zero=False), axis=None),
            order="No",
            color=alt.Color(
                "Cluster",
                scale=alt.Scale(
                    domain=[0, 1, 2, 3, 4, 5,6,7],
                    range=[
                        "#1B1A17",
                        "#F0A500",
                        "#5463FF",
                        "#7C203A",
                        "#468966",
                        "#573391",
                        "#A4D792",
                        "#EB2632",
                    ],
                ),
                legend=None,
            ),
        )
        .configure_axis(grid=False)
        .configure_view(strokeWidth=0)
        .properties(title=track)
        .configure_title(fontSize=20, anchor="middle", color="#404040")
    )
    chart.display()