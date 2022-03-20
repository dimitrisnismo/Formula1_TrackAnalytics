from operator import index
import fastf1
import numpy as np
import matplotlib as mpl
import pandas as pd
import altair as alt
from sklearn.cluster import KMeans
from sklearn.preprocessing import OneHotEncoder
from yellowbrick.cluster import KElbowVisualizer
from sklearn import preprocessing
from core import *

pd.set_option("precision", 2)
fastf1.Cache.enable_cache("C:\\Cachef1")  # replace with your cache directory


df = pd.DataFrame()
tracks_points = pd.DataFrame()
for i in range(1, 23):
    # Loading Data for each race
    session = fastf1.get_session(2021, i, "Q")
    laps = session.load_laps(with_telemetry=True)
    # Retrieving the best lap
    fastestlap, best_driver, compound = pick_fastest_driver_of_session(laps)
    # Excluding sessions in wet conditions
    if (compound == "WET") | (compound == "INTERMEDIATE"):
        pass
    else:
        print_the_best_driver(session, fastestlap, best_driver)
        # Retrieving Telemetry data only for the fastest driver
        track_df = dataframe_creation(laps, best_driver)
        # Visualize track
        track_vizualization(session, track_df)
        # Creating the Dimensions that we need to use
        track_df_new = retreive_kpis(session, fastestlap, track_df)
        track_df["grandprix"] = session.weekend.name
        # Creating a dataframe with all races
        tracks_points = pd.concat([tracks_points, track_df])
        # Creating a dataframe with the dimensions that we need for K-Means
        df = pd.concat([df, track_df_new])


### Working on k means
df, kmeans_df = Preparing_df_for_kmeans(df)
kmeans_df = onehotencoder_method(kmeans_df)
kmeans_df = minmaxscaler_method(kmeans_df)

# Finding number of cluster
visualizer = KElbowVisualizer(
    KMeans(),
    k=(2, 18),
    metric="distortion",
    timings=True,
    locate_elbow=True,
)
visualizer.fit(kmeans_df)
visualizer.show()

# Applying K-Means
clusters = visualizer.elbow_value_
kmeans = KMeans(clusters)
kmeans.fit(kmeans_df)
identified_clusters = kmeans.fit_predict(kmeans_df)
data_with_clusters = df.copy()
data_with_clusters.columns = df.columns
data_with_clusters["Cluster"] = identified_clusters
data_with_clusters["grandprix"] = df["grandprix"]
Cluster_centers = data_with_clusters.groupby("Cluster").mean()

# number of tracks per cluster
clusters_counter = (
    data_with_clusters[["Cluster", "grandprix"]]
    .groupby("Cluster")
    .count()
    .reset_index()
)
clusters_counter["Cluster"] = clusters_counter["Cluster"].astype("category")
(
    alt.Chart(clusters_counter)
    .mark_bar()
    .encode(
        alt.X("Cluster", scale=alt.Scale(zero=False)),
        alt.Y("grandprix", axis=None),
        text="grandprix",
    )
    # .configure_axis(grid=False)
    .configure_view(strokeWidth=0)
    .properties(title="Grand Prix per Cluster")
    .configure_title(fontSize=20, anchor="middle", color="#404040")
)


###Appear track by Color
tracks_points = pd.merge(
    tracks_points, data_with_clusters[["grandprix", "Cluster"]], how="inner"
)


for track in tracks_points.grandprix.unique():
    temp_track_data = tracks_points[tracks_points["grandprix"] == track]
    track_vizualization_byCluster(temp_track_data, track)
