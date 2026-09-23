import pandas as pd

folders = ["fitbit_data/"]
D = "%m/%d/%Y"
DT = "%m/%d/%Y %I:%M:%S %p"

def load(name):
    dfs = [pd.read_csv(f + name) for f in folders]
    return pd.concat(dfs, ignore_index=True).drop_duplicates()

# ===== DAILY =====
daily = load("dailyActivity_merged.csv")
daily["Date"] = pd.to_datetime(daily["ActivityDate"], format=D).dt.date
daily = daily.drop(columns="ActivityDate")

for name in ["dailyCalories", "dailyIntensities", "dailySteps"]:
    d = load(name + "_merged.csv")
    d["Date"] = pd.to_datetime(d["ActivityDay"], format=D).dt.date
    d = d.drop(columns="ActivityDay")
    daily = daily.merge(d, on=["Id", "Date"], how="left", suffixes=("", "_dup"))
daily = daily[[c for c in daily.columns if not c.endswith("_dup")]]

sleep = load("sleepDay_merged.csv")
sleep["Date"] = pd.to_datetime(sleep["SleepDay"], format=DT).dt.date
sleep = sleep.drop(columns="SleepDay")
daily = daily.merge(sleep, on=["Id", "Date"], how="left")

weight = load("weightLogInfo_merged.csv")
weight["Date"] = pd.to_datetime(weight["Date"], format=DT).dt.date

weight = (
    weight.sort_values(["Id", "Date"])
          .groupby(["Id", "Date"], as_index=False)
          .last()
)

daily = daily.merge(weight, on=["Id", "Date"], how="left")

daily.to_csv("daily_merged_final.csv", index=False)
print(daily.shape)
print(daily.head())