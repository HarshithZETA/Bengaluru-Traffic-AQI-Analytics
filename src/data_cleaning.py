import pandas as pd
import numpy as np
import os

def clean_dataset(
    input_path="data/raw/bengaluru_traffic_aqi_raw.csv",
    output_path="data/processed/bengaluru_traffic_aqi_cleaned.csv"
):
    print("[INFO] Starting data cleaning pipeline...")
    df = pd.read_csv(input_path)
    initial_rows = len(df)
    
    # 1. Standardize String Formats (Locality names)
    df["locality"] = df["locality"].astype(str).str.strip().str.title()
    
    # 2. Fix Inconsistent Date Formats
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="mixed", dayfirst=True, errors="coerce")
    df = df.dropna(subset=["timestamp"])
    
    # 3. Handle Outliers (Domain & IQR capping)
    # Fix negative or impossible speeds
    df.loc[(df["avg_speed_kmph"] < 2) | (df["avg_speed_kmph"] > 100), "avg_speed_kmph"] = np.nan
    
    # Cap AQI outliers (> 500 is severe ceiling for standard scale) using IQR method
    Q1 = df["aqi"].quantile(0.25)
    Q3 = df["aqi"].quantile(0.75)
    IQR = Q3 - Q1
    upper_bound = min(500.0, Q3 + 1.5 * IQR)
    df.loc[df["aqi"] > 500, "aqi"] = np.nan
    
    # 4. Impute Missing Values (Group by locality median for accuracy)
    num_cols = ["avg_speed_kmph", "pm25", "pm10", "no2", "co", "aqi"]
    for col in num_cols:
        df[col] = df.groupby("locality")[col].transform(lambda x: x.fillna(x.median()))
        
    # 5. Feature Engineering (Time of Day, Month, Weekend Flag, AQI Category)
    df["date"] = df["timestamp"].dt.date
    df["month"] = df["timestamp"].dt.strftime("%Y-%m")
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.day_name()
    df["is_weekend"] = df["timestamp"].dt.dayofweek.isin([5, 6]).astype(int)
    
    def get_time_slot(hr):
        if 6 <= hr < 11:
            return "Morning Peak (6AM-11AM)"
        elif 11 <= hr < 16:
            return "Midday (11AM-4PM)"
        elif 16 <= hr < 21:
            return "Evening Peak (4PM-9PM)"
        else:
            return "Night (9PM-6AM)"
            
    df["time_of_day"] = df["hour"].apply(get_time_slot)
    
    def get_aqi_category(aqi):
        if aqi <= 50: return "Good"
        elif aqi <= 100: return "Satisfactory"
        elif aqi <= 200: return "Moderate"
        elif aqi <= 300: return "Poor"
        else: return "Very Poor / Severe"
        
    df["aqi_category"] = df["aqi"].apply(get_aqi_category)
    
    # Sort chronologically
    df = df.sort_values("timestamp").reset_index(drop=True)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[SUCCESS] Cleaned dataset saved to: {output_path} ({len(df)}/{initial_rows} valid rows)")

if __name__ == "__main__":
    clean_dataset()