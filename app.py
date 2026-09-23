import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
from scipy import stats as scipy_stats

st.set_page_config(page_title="Fitness Track Insights Dashboard", page_icon="🏃", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #0f2027; background-image: linear-gradient(135deg, #0f2027, #203a43, #2c5364); }
h1, h2, h3, p, label, .stMarkdown, .stCaption { color: #f0f0f0 !important; }
[data-testid="stSidebar"] { background-color: #16222a; }
.kpi-card {
    background-color: #ffffff;
    border: 4px solid #003366;
    border-radius: 12px;
    padding: 14px;
    text-align: center;
    height: 120px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}
.kpi-label {
    color: #000000;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 6px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    line-height: 1.2;
}
.kpi-value { color: #000000; font-size: 26px; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

def kpi_card(label, value):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# ===== HEADER / LOGO =====
c1, c2 = st.columns([1, 6])
with c1:
    st.markdown("<h1 style='font-size:60px; margin:0;'>🏃‍♀️💪</h1>", unsafe_allow_html=True)
with c2:
    st.title("Fitness Track Insights Dashboard")
    st.caption("Smart device usage insights for Bellabeat's marketing strategy")

@st.cache_data
def load_data():
    df = pd.read_csv("fitbit_data/daily_merged_final.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    df["Weekday"] = df["Date"].dt.day_name()
    df["TotalActiveMinutes"] = df["VeryActiveMinutes"] + df["FairlyActiveMinutes"] + df["LightlyActiveMinutes"]
    df["SleepHours"] = (df["TotalMinutesAsleep"] / 60).round(2)

    def level(steps):
        if steps < 5000: return "Sedentary"
        elif steps < 7500: return "Lightly Active"
        elif steps < 10000: return "Fairly Active"
        else: return "Very Active"
    df["ActivityLevel"] = df["TotalSteps"].apply(level)
    return df

df = load_data()

# ===== SIDEBAR FILTERS (4) =====
st.sidebar.header("🔍 Filters")

user_ids = ["All"] + sorted(df["Id"].astype(str).unique().tolist())
selected_user = st.sidebar.selectbox("1. User ID", user_ids)

weekday_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
selected_days = st.sidebar.multiselect("2. Weekday", weekday_order, default=weekday_order)

min_date, max_date = df["Date"].min(), df["Date"].max()
date_range = st.sidebar.date_input("3. Date range", (min_date, max_date), min_value=min_date, max_value=max_date)

activity_levels = ["All"] + sorted(df["ActivityLevel"].unique().tolist())
selected_level = st.sidebar.selectbox("4. Activity Level", activity_levels)

# ===== APPLY FILTERS =====
filtered = df.copy()
if selected_user != "All":
    filtered = filtered[filtered["Id"].astype(str) == selected_user]
filtered = filtered[filtered["Weekday"].isin(selected_days)]
if len(date_range) == 2:
    filtered = filtered[(filtered["Date"] >= pd.to_datetime(date_range[0])) & (filtered["Date"] <= pd.to_datetime(date_range[1]))]
if selected_level != "All":
    filtered = filtered[filtered["ActivityLevel"] == selected_level]

st.write(f"Showing **{len(filtered)}** records after filters")

# ===== 5 KPI CARDS (custom HTML) =====
st.header("📊 Key Metrics")
k1, k2, k3, k4, k5 = st.columns(5)
with k1: kpi_card("🚶 Avg Steps", int(filtered["TotalSteps"].mean()) if len(filtered) else 0)
with k2: kpi_card("🔥 Avg Calories", int(filtered["Calories"].mean()) if len(filtered) else 0)
with k3: kpi_card("🪑 Avg Sedentary Min", int(filtered["SedentaryMinutes"].mean()) if len(filtered) else 0)
with k4: kpi_card("😴 Avg Sleep (hrs)", round(filtered["SleepHours"].mean(), 1) if len(filtered) else 0)
with k5: kpi_card("⚡ Avg Active Min", int(filtered["TotalActiveMinutes"].mean()) if len(filtered) else 0)

st.header("📋 Data Preview")
st.dataframe(filtered.head(20))

# ===== DATA CLEANING INSIGHTS =====
st.markdown("---")
st.header("🧹 Key Insights from Data Cleaning")
st.markdown("""
- **Duplicate rows removed** during merge to prevent double-counting of records.
- **Date columns standardized** to a single `datetime` format across daily, sleep, and weight files.
- **Missing weight and sleep data**: not every user logged weight or sleep daily, so these columns contain blanks (NaN) rather than being dropped, to preserve the full activity record.
- **Full-day sedentary values (1440 minutes)** were flagged as likely days the tracker was not worn, rather than true inactivity.
- **Wide-format files skipped** (e.g. `minuteStepsWide`) since they duplicated data already present in the Narrow-format files.
- **Activity Level column engineered** from `TotalSteps` using CDC-style thresholds (Sedentary / Lightly / Fairly / Very Active) for easier segmentation.
""")

# ===== 6 CHARTS (varied types) =====
st.header("📅 1. Average Steps by Weekday")
steps_by_day = filtered.groupby("Weekday")["TotalSteps"].mean().reindex(weekday_order)
fig1, ax1 = plt.subplots()
ax1.plot(steps_by_day.index, steps_by_day.values, marker="o", color="mediumseagreen", linewidth=2)
ax1.fill_between(steps_by_day.index, steps_by_day.values, color="mediumseagreen", alpha=0.2)
ax1.set_ylabel("Avg Steps")
st.pyplot(fig1)

st.header("🪑 2. Sedentary Minutes by Weekday")
sed_by_day = filtered.groupby("Weekday")["SedentaryMinutes"].mean().reindex(weekday_order)
fig2, ax2 = plt.subplots()
ax2.barh(sed_by_day.index, sed_by_day.values, color="orange")
ax2.set_xlabel("Avg Sedentary Minutes")
st.pyplot(fig2)

st.header("🔥 3. Average Calories by Weekday")
cal_by_day = filtered.groupby("Weekday")["Calories"].mean().reindex(weekday_order)
fig3, ax3 = plt.subplots()
ax3.stem(cal_by_day.index, cal_by_day.values, linefmt="crimson", markerfmt="o", basefmt=" ")
ax3.set_ylabel("Avg Calories")
st.pyplot(fig3)

st.header("😴 4. Sleep vs Sedentary Minutes (Density)")
sleep_df = filtered.dropna(subset=["TotalMinutesAsleep"])
fig4, ax4 = plt.subplots()
hb = ax4.hexbin(sleep_df["SedentaryMinutes"], sleep_df["TotalMinutesAsleep"], gridsize=25, cmap="magma")
ax4.set_xlabel("Sedentary Minutes")
ax4.set_ylabel("Total Minutes Asleep")
fig4.colorbar(hb, ax=ax4, label="Record count")
st.pyplot(fig4)

st.header("🏷️ 5. Activity Level Breakdown")
level_counts = filtered["ActivityLevel"].value_counts()
fig5, ax5 = plt.subplots()
ax5.pie(level_counts.values, labels=level_counts.index, autopct="%1.0f%%")
st.pyplot(fig5)

st.header("😴 6. Average Sleep Hours by Weekday")
fig6, ax6 = plt.subplots()
box_data = [filtered[filtered["Weekday"] == d]["SleepHours"].dropna() for d in weekday_order]
ax6.boxplot(box_data, tick_labels=weekday_order)
ax6.set_ylabel("Sleep Hours")
st.pyplot(fig6)

# ===== SELF CHECK: RADAR CHART + PERCENTILE =====
st.markdown("---")
st.header("✅ Check Your Own Activity Level")
st.write("Enter your daily numbers to see how you compare to the Fitbit users in this dataset.")

c1, c2, c3 = st.columns(3)
user_steps = c1.number_input("Your daily steps", min_value=0, value=5000)
user_cal = c2.number_input("Your daily calories burned", min_value=0, value=2000)
user_sleep = c3.number_input("Your minutes asleep", min_value=0, value=420)

if st.button("Check My Stats"):
    # ---- Percentiles for the 3 user-entered metrics ----
    steps_pct = scipy_stats.percentileofscore(df["TotalSteps"].dropna(), user_steps)
    cal_pct = scipy_stats.percentileofscore(df["Calories"].dropna(), user_cal)
    sleep_pct = scipy_stats.percentileofscore(df["TotalMinutesAsleep"].dropna(), user_sleep)

    st.subheader("📊 Your Percentile Ranking")
    p1, p2, p3 = st.columns(3)
    p1.metric("Steps", f"{steps_pct:.0f}th percentile")
    p2.metric("Calories Burned", f"{cal_pct:.0f}th percentile")
    p3.metric("Sleep", f"{sleep_pct:.0f}th percentile")

    if steps_pct >= 75:
        st.success(f"🏆 Your steps beat {steps_pct:.0f}% of days in this dataset!")
    elif steps_pct >= 50:
        st.info(f"👍 Your steps beat {steps_pct:.0f}% of days in this dataset.")
    else:
        st.warning(f"⚠️ Your steps beat only {steps_pct:.0f}% of days — room to grow.")

    if sleep_pct >= 50:
        st.success(f"😴 Your sleep beats {sleep_pct:.0f}% of days — solid rest!")
    else:
        st.warning(f"😴 Your sleep beats only {sleep_pct:.0f}% of days — aim for more.")

    # ---- Radar chart: user vs dataset average ----
    st.subheader("🕸️ You vs. The Average")

    categories = ["Steps", "Calories", "Active Min", "Sleep (min)", "Low Sedentary"]

    avg_active = df["TotalActiveMinutes"].mean()
    avg_sedentary = df["SedentaryMinutes"].mean()
    max_sedentary = df["SedentaryMinutes"].max()

    def norm(value, max_value):
        return min(100, (value / max_value) * 100) if max_value else 0

    max_steps = df["TotalSteps"].max()
    max_cal = df["Calories"].max()
    max_active = df["TotalActiveMinutes"].max()
    max_sleep = df["TotalMinutesAsleep"].max()

    low_sed_score = 100 - norm(avg_sedentary, max_sedentary)

    user_values = [
        norm(user_steps, max_steps),
        norm(user_cal, max_cal),
        norm(avg_active, max_active),
        norm(user_sleep, max_sleep),
        low_sed_score,
    ]
    avg_values = [
        norm(df["TotalSteps"].mean(), max_steps),
        norm(df["Calories"].mean(), max_cal),
        norm(avg_active, max_active),
        norm(df["TotalMinutesAsleep"].mean(), max_sleep),
        low_sed_score,
    ]

    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    user_values += user_values[:1]
    avg_values += avg_values[:1]
    angles += angles[:1]

    fig_radar, ax_radar = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax_radar.plot(angles, user_values, color="crimson", linewidth=2, label="You")
    ax_radar.fill(angles, user_values, color="crimson", alpha=0.25)
    ax_radar.plot(angles, avg_values, color="mediumseagreen", linewidth=2, label="Dataset Avg")
    ax_radar.fill(angles, avg_values, color="mediumseagreen", alpha=0.15)
    ax_radar.set_xticks(angles[:-1])
    ax_radar.set_xticklabels(categories, fontsize=9)
    ax_radar.set_yticklabels([])
    ax_radar.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    st.pyplot(fig_radar)

# ===== SQL ANALYSIS =====
st.markdown("---")
st.header("🗄️ SQL Analysis")
conn = sqlite3.connect(":memory:")
df.to_sql("daily", conn, index=False, if_exists="replace")

query = st.text_area("Write a SQL query on the 'daily' table:",
    "SELECT Id, ROUND(AVG(TotalSteps),0) as avg_steps FROM daily GROUP BY Id ORDER BY avg_steps DESC")

if st.button("Run Query"):
    try:
        result = pd.read_sql(query, conn)
        st.dataframe(result)
    except Exception as e:
        st.error(f"Query error: {e}")
