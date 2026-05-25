# ============================================================
# Run Feature Pipeline
# Called by GitHub Actions every hour
# Fetches current data and pushes to MongoDB
# ============================================================

import os
import requests
import certifi
import numpy as np
from datetime import datetime, timezone, date
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
    # weather from OpenWeather
    weather = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?q={CITY},PK&appid={API_KEY}&units=metric"
    ).json()

    # AQI from Open-Meteo European scale
    today  = date.today().strftime("%Y-%m-%d")
    aq_url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality?"
        f"latitude={LAT}&longitude={LON}"
        f"&hourly=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone,european_aqi"
        f"&start_date={today}&end_date={today}"
    )
    aq_data = requests.get(aq_url).json()

    now   = datetime.now(timezone.utc)
    hour  = now.hour
    index = min(hour, len(aq_data["hourly"]["european_aqi"]) - 1)

    aqi   = aq_data["hourly"]["european_aqi"][index]
    pm2_5 = aq_data["hourly"]["pm2_5"][index]
    pm10  = aq_data["hourly"]["pm10"][index]
    no2   = aq_data["hourly"]["nitrogen_dioxide"][index]
    co    = aq_data["hourly"]["carbon_monoxide"][index]
    o3    = aq_data["hourly"]["ozone"][index]

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
        "aqi":         float(aqi)   if aqi   is not None else 0.0,
        "pm2_5":       float(pm2_5) if pm2_5 is not None else 0.0,
        "pm10":        float(pm10)  if pm10  is not None else 0.0,
        "no2":         float(no2)   if no2   is not None else 0.0,
        "co":          float(co)    if co    is not None else 0.0,
        "o3":          float(o3)    if o3    is not None else 0.0,
    }

def get_lag_features(record):
    client  = MongoClient(MONGODB_URI, tls=True, tlsCAFile=certifi.where())
    db      = client["pearls_aqi"]
    recent  = list(db["aqi_engineered"].find(
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
    db["aqi_features"].insert_one({k: v for k, v in record.items()})
    db["aqi_engineered"].insert_one({k: v for k, v in record.items()})
    client.close()
    print(f"Pushed record for {record['timestamp']} ✅")

if __name__ == "__main__":
    print("Fetching current data...")
    record = fetch_current()
    print(f"Fetched: AQI={record['aqi']}, Temp={record['temperature']}")

    print("Computing lag features...")
    record = get_lag_features(record)

    print("Pushing to MongoDB...")
    push_to_mongodb(record)
    print("Feature pipeline complete ✅")