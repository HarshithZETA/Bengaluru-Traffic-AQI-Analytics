import streamlit as st
import pandas as pd
from importlib import import_module
import sqlite3
import os

try:
    px = import_module("plotly.express")
except ModuleNotFoundError:
    px = None

from src.data_generator import generate_raw_data
from src.data_cleaning import clean_dataset
from src.db_manager import init_database, run_sql_query, DB_PATH, CSV_PATH

st.set_page_config(
    page_title="Bengaluru Traffic & AQI Analytics 2025",
    page_icon="🚦",
    layout="wide"
)

if px is None:
    st.error("Plotly is required for the dashboard charts. Install it with: pip install plotly")
    st.stop()

# Auto-initialize pipeline if running for the first time
if not os.path.exists(DB_PATH):
    with st.spinner("Initializing dataset, cleaning pipeline, and SQL database..."):
        generate_raw_data()
        clean_dataset()
        init_database()

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_PATH)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.title("🎛️ Dashboard Filters")
selected_localities = st.sidebar.multiselect(
    "Select Localities",
    options=sorted(df["locality"].unique()),
    default=sorted(df["locality"].unique())
)

selected_months = st.sidebar.multiselect(
    "Select Months (2025)",
    options=sorted(df["month"].unique()),
    default=sorted(df["month"].unique())
)

selected_weather = st.sidebar.multiselect(
    "Weather Condition",
    options=sorted(df["weather_condition"].unique()),
    default=sorted(df["weather_condition"].unique())
)

filtered_df = df[
    (df["locality"].isin(selected_localities)) &
    (df["month"].isin(selected_months)) &
    (df["weather_condition"].isin(selected_weather))
]

# --- HEADER ---
st.title("🚦 Bengaluru Traffic & Air Quality Analytics Dashboard (2025)")
st.markdown("Interactive EDA & SQL-backed insights correlating urban traffic congestion with air pollution trends across Bengaluru.")

# --- KPI METRICS ---
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Observations", f"{len(filtered_df):,}")
col2.metric("Avg Congestion", f"{filtered_df['congestion_pct'].mean():.1f}%")
col3.metric("Avg Traffic Speed", f"{filtered_df['avg_speed_kmph'].mean():.1f} km/h")
col4.metric("Avg AQI", f"{filtered_df['aqi'].mean():.0f}")
col5.metric("Avg PM2.5", f"{filtered_df['pm25'].mean():.1f} µg/m³")

st.divider()

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Visual Analytics", "🗄️ SQL EDA Explorer", "📋 Cleaned Dataset & Power BI Export"])

with tab1:
    r1c1, r1c2 = st.columns(2)
    
    with r1c1:
        st.subheader("Locality Congestion vs. AQI Comparison")
        loc_summary = filtered_df.groupby("locality")[["congestion_pct", "aqi", "avg_speed_kmph"]].mean().reset_index()
        loc_summary = loc_summary.sort_values("congestion_pct", ascending=True)
        
        fig_loc = px.bar(
            loc_summary,
            x="congestion_pct",
            y="locality",
            color="aqi",
            orientation="h",
            color_continuous_scale="RdYlGn_r",
            labels={"congestion_pct": "Avg Congestion (%)", "locality": "Locality", "aqi": "Avg AQI"},
            title="Average Traffic Congestion & AQI by Locality"
        )
        st.plotly_chart(fig_loc, use_container_width=True)

    with r1c2:
        st.subheader("Hourly Congestion & Pollution Trend (24-Hour Cycle)")
        hourly = filtered_df.groupby("hour")[["congestion_pct", "aqi", "avg_speed_kmph"]].mean().reset_index()
        
        fig_hr = px.line(
            hourly,
            x="hour",
            y=["congestion_pct", "aqi"],
            markers=True,
            labels={"hour": "Hour of Day (0-23)", "value": "Value", "variable": "Metric"},
        )
        fig_hr.update_traces(name="Congestion (%)", selector={"name": "congestion_pct"})
        fig_hr.update_traces(name="Average AQI", selector={"name": "aqi"}, yaxis="y2")
        fig_hr.update_layout(
            title="Diurnal Pattern: Traffic Congestion vs. Air Quality Index",
            xaxis=dict(title="Hour of Day (0-23)", tickmode="linear"),
            yaxis=dict(title="Congestion (%)"),
            yaxis2=dict(title="AQI", overlaying="y", side="right"),
            legend=dict(orientation="h", y=1.12)
        )
        st.plotly_chart(fig_hr, use_container_width=True)

    r2c1, r2c2 = st.columns(2)

    with r2c1:
        st.subheader("Time of Day Pollution Breakdown (PM2.5, PM10, NO2)")
        tod_df = filtered_df.groupby("time_of_day")[["pm25", "pm10", "no2"]].mean().reset_index()
        fig_tod = px.bar(
            tod_df,
            x="time_of_day",
            y=["pm25", "pm10", "no2"],
            barmode="group",
            title="Pollutant Concentration by Time Slot"
        )
        st.plotly_chart(fig_tod, use_container_width=True)

    with r2c2:
        st.subheader("Traffic Congestion vs. PM2.5 Correlation")
        sample_df = filtered_df.sample(min(1500, len(filtered_df)), random_state=42) if len(filtered_df) > 0 else filtered_df
        fig_corr = px.scatter(
            sample_df,
            x="congestion_pct",
            y="pm25",
            color="time_of_day",
            hover_data=["locality", "avg_speed_kmph", "aqi"],
            title="Impact of Traffic Bottlenecks on PM2.5 Levels",
            labels={"congestion_pct": "Traffic Congestion (%)", "pm25": "PM2.5 (µg/m³)"}
        )
        st.plotly_chart(fig_corr, use_container_width=True)

with tab2:
    st.subheader("🗄️ Interactive SQL EDA Query Runner (SQLite Backend)")
    st.markdown("Run pre-configured analytical SQL queries or write your own custom SQL against the `traffic_aqi_logs` table.")
    
    preset_queries = {
        "1. Locality Congestion & AQI Ranking": """SELECT locality, ROUND(AVG(congestion_pct), 2) AS avg_congestion_pct, ROUND(AVG(avg_speed_kmph), 2) AS avg_speed_kmph, ROUND(AVG(aqi), 1) AS avg_aqi, COUNT(*) AS records FROM traffic_aqi_logs GROUP BY locality ORDER BY avg_congestion_pct DESC;""",
        "2. Time of Day Congestion & NO2 Trends": """SELECT time_of_day, ROUND(AVG(traffic_volume), 0) AS avg_volume, ROUND(AVG(congestion_pct), 2) AS avg_congestion_pct, ROUND(AVG(aqi), 1) AS avg_aqi, ROUND(AVG(no2), 2) AS avg_no2 FROM traffic_aqi_logs GROUP BY time_of_day ORDER BY avg_congestion_pct DESC;""",
        "3. Severe Gridlock & Pollution Hotspots (Congestion > 80% & AQI > 150)": """SELECT locality, COUNT(*) AS severe_incidents, ROUND(AVG(congestion_pct), 1) AS avg_congestion, ROUND(AVG(aqi), 1) AS avg_aqi FROM traffic_aqi_logs WHERE congestion_pct > 80 AND aqi > 150 GROUP BY locality ORDER BY severe_incidents DESC;""",
        "4. Weekday vs Weekend Traffic & AQI Impact": """SELECT CASE WHEN is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS day_type, ROUND(AVG(congestion_pct), 2) AS avg_congestion, ROUND(AVG(avg_speed_kmph), 2) AS avg_speed_kmph, ROUND(AVG(aqi), 1) AS avg_aqi FROM traffic_aqi_logs GROUP BY is_weekend;"""
    }
    
    selected_q = st.selectbox("Select an Analytical SQL Query:", list(preset_queries.keys()))
    sql_input = st.text_area("SQL Query:", value=preset_queries[selected_q], height=100)
    
    if st.button("Execute SQL Query"):
        try:
            res_df = run_sql_query(sql_input)
            st.dataframe(res_df, use_container_width=True)
        except Exception as e:
            st.error(f"SQL Error: {e}")

with tab3:
    st.subheader("📥 Download Cleaned Data for Power BI")
    st.markdown("Import `data/processed/bengaluru_traffic_aqi_cleaned.csv` directly into **Power BI Desktop** (`Get Data -> Text/CSV`) to build supplementary DAX measures.")
    
    csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Filtered Cleaned CSV",
        data=csv_bytes,
        file_name="bengaluru_traffic_aqi_cleaned.csv",
        mime="text/csv"
    )
    st.dataframe(filtered_df.head(100), use_container_width=True)