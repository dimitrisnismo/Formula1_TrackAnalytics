# find straights and corners in data
df["STR_COR_P1"] = np.where(
    df["Y"] - df["Y"].shift(-1) == 0,
    0,
    (df["X"] - df["X"].shift(-1)) / (df["Y"] - df["Y"].shift(-1)),
)
df["STR_COR_P2"] = np.where(
    (df["Y"].shift(1) - df["Y"]) == 0,
    0,
    (df["X"].shift(1) - df["X"]) / (df["Y"].shift(1) - df["Y"]),
)

df["STR_COR"] = abs(df["STR_COR_P1"] - df["STR_COR_P2"]).fillna(0)
df["STR_COR"] =np.where(df["STR_COR"]>0.2,1,0 )


