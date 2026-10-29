-- 1. Locality-wise Average Congestion, Speed, and AQI Ranking
SELECT 
    locality,
    ROUND(AVG(congestion_pct), 2) AS avg_congestion_pct,
    ROUND(AVG(avg_speed_kmph), 2) AS avg_speed_kmph,
    ROUND(AVG(aqi), 1) AS avg_aqi,
    ROUND(AVG(pm25), 2) AS avg_pm25,
    COUNT(*) AS total_observations
FROM traffic_aqi_logs
GROUP BY locality
ORDER BY avg_congestion_pct DESC;

-- 2. Time-of-Day Congestion and Pollution Patterns
SELECT 
    time_of_day,
    ROUND(AVG(traffic_volume), 0) AS avg_traffic_volume,
    ROUND(AVG(congestion_pct), 2) AS avg_congestion_pct,
    ROUND(AVG(aqi), 1) AS avg_aqi,
    ROUND(AVG(no2), 2) AS avg_no2_level
FROM traffic_aqi_logs
GROUP BY time_of_day
ORDER BY avg_congestion_pct DESC;

-- 3. Monthly Trend Analysis Across 2025
SELECT 
    month,
    ROUND(AVG(congestion_pct), 2) AS monthly_avg_congestion,
    ROUND(AVG(aqi), 1) AS monthly_avg_aqi,
    ROUND(MAX(aqi), 1) AS peak_aqi
FROM traffic_aqi_logs
GROUP BY month
ORDER BY month ASC;

-- 4. Weekday vs Weekend Comparison
SELECT 
    CASE WHEN is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    ROUND(AVG(congestion_pct), 2) AS avg_congestion_pct,
    ROUND(AVG(avg_speed_kmph), 2) AS avg_speed_kmph,
    ROUND(AVG(aqi), 1) AS avg_aqi
FROM traffic_aqi_logs
GROUP BY is_weekend;

-- 5. High-Risk Pollution & Gridlock Hotspots (Congestion > 80% AND AQI > 150)
SELECT 
    locality,
    COUNT(*) AS severe_incident_count,
    ROUND(AVG(congestion_pct), 1) AS avg_hotspot_congestion,
    ROUND(AVG(aqi), 1) AS avg_hotspot_aqi
FROM traffic_aqi_logs
WHERE congestion_pct > 80 AND aqi > 150
GROUP BY locality
ORDER BY severe_incident_count DESC;