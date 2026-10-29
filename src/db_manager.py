import sqlite3
import pandas as pd
import os

DB_PATH = "data/bengaluru_analytics.db"
CSV_PATH = "data/processed/bengaluru_traffic_aqi_cleaned.csv"
SQL_FILE = "sql/eda_queries.sql"

def init_database():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"Cleaned CSV not found at {CSV_PATH}. Run data_cleaning.py first.")
        
    df = pd.read_csv(CSV_PATH)
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("traffic_aqi_logs", conn, if_exists="replace", index=False)
    conn.close()
    print(f"[SUCCESS] Loaded {len(df)} records into SQLite database: {DB_PATH}")

def run_sql_query(query: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result

if __name__ == "__main__":
    init_database()
    
    # Run and display sample SQL EDA output in terminal
    with open(SQL_FILE, "r") as f:
        queries = [q.strip() for q in f.read().split(";") if q.strip()]
        
    print("\n--- RUNNING SQL EDA QUERIES ---")
    for idx, q in enumerate(queries, 1):
        print(f"\nQuery #{idx} Result:")
        print(run_sql_query(q).to_string(index=False))