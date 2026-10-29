import pandas as pd
import numpy as np
import os

def generate_raw_data(output_path="data/raw/bengaluru_traffic_aqi_raw.csv"):
    np.random.seed(42)
    
    localities = [
        "Silk Board", "Whitefield", "Koramangala", "Indiranagar", 
        "Electronic City", "Hebbal", "Marathahalli", "Jayanagar", 
        "MG Road", "Yeshwanthpur"
    ]
    
    # Generate 6 months of hourly data in 2025
    date_rng = pd.date_range(start="2025-01-01", end="2025-06-30 23:00:00", freq="h")
    
    records = []
    # Sample ~12,000 records across localities and timestamps
    n_samples = 12000
    sampled_dates = np.random.choice(date_rng, n_samples)
    
    for dt in sampled_dates:
        ts = pd.Timestamp(dt)
        loc = np.random.choice(localities)
        hour = ts.hour
        is_weekend = ts.dayofweek >= 5
        
        # Traffic logic: Peak hours (8-11 AM, 5-9 PM) on weekdays
        if not is_weekend and (8 <= hour <= 11 or 17 <= hour <= 21):
            congestion = np.random.normal(78, 12)
            speed = np.random.normal(14, 4)
            volume = np.random.normal(4200, 700)
        elif 0 <= hour <= 5:
            congestion = np.random.normal(18, 6)
            speed = np.random.normal(48, 7)
            volume = np.random.normal(450, 150)
        else:
            congestion = np.random.normal(48, 14)
            speed = np.random.normal(26, 6)
            volume = np.random.normal(2100, 500)
            
        # Locality multipliers (Silk Board, Hebbal, Marathahalli are heavier)
        if loc in ["Silk Board", "Marathahalli", "Hebbal", "Whitefield"]:
            congestion *= 1.15
            speed *= 0.82
        elif loc in ["Jayanagar", "Indiranagar"]:
            congestion *= 0.88
            speed *= 1.12
            
        congestion = np.clip(congestion, 5, 100)
        speed = np.clip(speed, 5, 75)
        volume = max(50, int(volume))
        
        # Air Quality logic (correlated with traffic congestion + base urban levels)
        pm25 = (congestion * 0.95) + np.random.normal(25, 10)
        pm10 = (pm25 * 1.65) + np.random.normal(20, 12)
        no2 = (congestion * 0.55) + np.random.normal(12, 5)
        co = (congestion * 0.025) + np.random.normal(0.5, 0.2)
        aqi = max(pm25 * 1.45, pm10 * 0.85) + np.random.normal(0, 8)
        
        weather = np.random.choice(["Clear", "Cloudy", "Rain", "Haze"], p=[0.5, 0.3, 0.12, 0.08])
        
        records.append({
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "locality": loc,
            "traffic_volume": volume,
            "avg_speed_kmph": round(speed, 2),
            "congestion_pct": round(congestion, 2),
            "pm25": round(max(10, pm25), 2),
            "pm10": round(max(20, pm10), 2),
            "no2": round(max(5, no2), 2),
            "co": round(max(0.1, co), 2),
            "aqi": round(max(25, aqi), 0),
            "weather_condition": weather
        })
        
    df = pd.DataFrame(records)
    
    # --- INJECT REALISTIC RAW DATA ISSUES FOR CLEANING ---
    # 1. Missing values (NaNs)
    for col in ["avg_speed_kmph", "pm25", "pm10", "aqi"]:
        mask = np.random.rand(len(df)) < 0.04
        df.loc[mask, col] = np.nan
        
    # 2. Outliers (Sensor spikes / negative glitches)
    outlier_idx = np.random.choice(df.index, size=60, replace=False)
    df.loc[outlier_idx[:30], "aqi"] = np.random.uniform(950, 2500, size=30)
    df.loc[outlier_idx[30:], "avg_speed_kmph"] = -15.0
    
    # 3. Inconsistent string & date formatting
    messy_idx = np.random.choice(df.index, size=300, replace=False)
    df.loc[messy_idx[:150], "locality"] = df.loc[messy_idx[:150], "locality"].str.lower() + "  "
    df.loc[messy_idx[150:], "timestamp"] = pd.to_datetime(df.loc[messy_idx[150:], "timestamp"]).dt.strftime("%d/%m/%Y %H:%M")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[SUCCESS] Generated raw dataset with {len(df)} rows at: {output_path}")

if __name__ == "__main__":
    generate_raw_data()