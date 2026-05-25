# ============================================================
# Run Feature Pipeline
# Called by GitHub Actions every hour
# Fetches current data and pushes to MongoDB
# ============================================================

import os
import sys
import pandas as pd
import numpy as np
import requests
import certifi
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

API_KEY     = os.getenv("OPENWEATHER_API_KEY")
LAT         = float(os.getenv("LAT"))
LON         = float(os.getenv("LON"))
CITY        = os.getenv("CITY")
MONGODB_URI = os.getenv("MONGODB_URI")

def get_time_of_day(hour):
    if 5 <= hour < 12:    return "morning"
    elif 12 <= hour < 17: return "afternoon"
    elif 17 <= hour < 21: return "evening"
    else:                 return "night"

def get_season(month):
    if month in [12, 1, 2]:  return "winter"
    elif month in [3, 4, 5]: return "spring"
    elif month in [6, 7, 8]: return "summer"
    else:                    return "autumn"

def fetch_current():
    weather = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?q={CITY},PK&appid={API_KEY}&units=metric"
    ).json()
    poll = requests.get(
        f"http://api.openweathermap.org/data/2.5/air_pollution?lat={LAT}&lon={LON}&appid={API_KEY}"
    ).json()

    now = datetime.now(timezone.utc)
    return {
        "timestamp":   now.strftime("%Y-%m-%d %H:%M:%S"),
        "date":        now.strftime("%Y-%m-%d"),
        "hour":        int(now.hour),
        "day":         int(now.day),
        "month":       int(now.month),
        "city":        CITY,
        "temperature": float(weather["main"]["temp"]),
        "humidity":    int(weather["main"]["humidity"]),
        "wind_speed":  float(weather["wind"]["speed"]),
        "aqi":         float(poll["list"][0]["main"]["aqi"]),
        "pm2_5":       float(poll["list"][0]["components"]["pm2_5"]),
        "pm10":        float(poll["list"][0]["components"]["pm10"]),
        "no2":         float(poll["list"][0]["components"]["no2"]),
        "co":          float(poll["list"][0]["components"]["co"]),
        "o3":          float(poll["list"][0]["components"]["o3"]),
    }

def get_lag_features(col, record):
    client = MongoClient(MONGODB_URI, tls=True, tlsCAFile=certifi.where())
    db     = client["pearls_aqi"]
    recent = list(db["aqi_features"].find(
        {}, {"_id": 0, "aqi": 1}
    ).sort("timestamp", -1).limit(24))
    client.close()

    aqi_history = [r["aqi"] for r in reversed(recent)]
    current_aqi = record["aqi"]

    if len(aqi_history) >= 1:
        record["aqi_lag_1"]           = float(aqi_history[-1])
        record["aqi_lag_3"]           = float(aqi_history[-3])  if len(aqi_history) >= 3  else current_aqi
        record["aqi_lag_24"]          = float(aqi_history[-24]) if len(aqi_history) >= 24 else current_aqi
        record["aqi_rolling_mean_24"] = float(np.mean(aqi_history[-24:]))
        record["aqi_change_rate"]     = float(aqi_history[-1] - aqi_history[-2]) if len(aqi_history) >= 2 else 0.0
    else:
        record["aqi_lag_1"]           = current_aqi
        record["aqi_lag_3"]           = current_aqi
        record["aqi_lag_24"]          = current_aqi
        record["aqi_rolling_mean_24"] = current_aqi
        record["aqi_change_rate"]     = 0.0

    record["time_of_day"] = get_time_of_day(record["hour"])
    record["is_weekend"]  = int(datetime.now().weekday() in [5, 6])
    record["season"]      = get_season(record["month"])
    return record

def push_to_mongodb(record):
    client = MongoClient(MONGODB_URI, tls=True, tlsCAFile=certifi.where())
    db     = client["pearls_aqi"]

    # push to raw features
    db["aqi_features"].insert_one({k: v for k, v in record.items() if k != "_id"})

    # push to engineered features
    db["aqi_engineered"].insert_one({k: v for k, v in record.items() if k != "_id"})

    client.close()
    print(f"Pushed record for {record['timestamp']} ✅")

if __name__ == "__main__":
    print("Fetching current data...")
    record = fetch_current()
    print(f"Fetched: AQI={record['aqi']}, Temp={record['temperature']}")

    print("Computing lag features...")
    record = get_lag_features(None, record)

    print("Pushing to MongoDB...")
    push_to_mongodb(record)
    print("Feature pipeline complete ✅")