import pandas as pd

df = pd.read_csv("daily_merged_final.csv")
print("Before:", df.shape)

df["Date"] = pd.to_datetime(df["Date"])
df["Weekday"] = df["Date"].dt.day_name()

df = df.drop(columns=["StepTotal", "TrackerDistance", "LogId",
                      "IsManualReport", "Fat"], errors="ignore")

print("Duplicate rows:", df.duplicated().sum())
df = df.drop_duplicates(subset=["Id", "Date"])

df["TotalSleepRecords"] = df["TotalSleepRecords"].fillna(0)
df["NotWorn"] = (df["TotalSteps"] == 0) & (df["SedentaryMinutes"] >= 1440)

df["TotalActiveMinutes"] = (df["VeryActiveMinutes"]
                            + df["FairlyActiveMinutes"]
                            + df["LightlyActiveMinutes"])
df["SleepHours"] = (df["TotalMinutesAsleep"] / 60).round(2)

def level(steps):
    if steps < 5000: return "Sedentary"
    if steps < 7500: return "Lightly Active"
    if steps < 10000: return "Fairly Active"
    return "Very Active"

df["ActivityLevel"] = df["TotalSteps"].apply(level)

print("Nulls:\n", df.isna().sum())
print("Not-worn days:", df["NotWorn"].sum())

df.to_csv("daily_clean.csv", index=False)
print("After:", df.shape)