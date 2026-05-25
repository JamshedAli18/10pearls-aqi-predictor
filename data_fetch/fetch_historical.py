import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv("../.env")

LAT = float(os.getenv("LAT"))
LON = float(os.getenv("LON"))
CITY = os.getenv("CITY")
MONGODB_URI = os.getenv("MONGODB_URI")

def fetch_air_quality():
    end_date   = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

    url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality?"
        f"latitude={LAT}&longitude={LON}"
        f"&hourly=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone,european_aqi"
        f"&start_date={start_date}&end_date={end_date}"
    )

    response = requests.get(url)
    data = response.json()

    records = []
    for i, time in enumerate(data["hourly"]["time"]):
        dt = datetime.strptime(time, "%Y-%m-%dT%H:%M")
        records.append({
            "timestamp": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "date":      dt.strftime("%Y-%m-%d"),
            "hour":      dt.hour,
            "day":       dt.day,
            "month":     dt.month,
            "city":      CITY,
            "aqi":       data["hourly"]["european_aqi"][i],
            "pm2_5":     data["hourly"]["pm2_5"][i],
            "pm10":      data["hourly"]["pm10"][i],
            "no2":       data["hourly"]["nitrogen_dioxide"][i],
            "co":        data["hourly"]["carbon_monoxide"][i],
            "o3":        data["hourly"]["ozone"][i],
        })

    return records

def fetch_weather():
    end_date   = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={LAT}&longitude={LON}"
        f"&start_date={start_date}&end_date={end_date}"
        f"&hourly=temperature_2m,relativehumidity_2m,windspeed_10m"
    )

    response = requests.get(url)
    data = response.json()

    records = {}
    for i, time in enumerate(data["hourly"]["time"]):
        dt  = datetime.strptime(time, "%Y-%m-%dT%H:%M")
        key = dt.strftime("%Y-%m-%d %H:%M:%S")
        records[key] = {
            "temperature": data["hourly"]["temperature_2m"][i],
            "humidity":    data["hourly"]["relativehumidity_2m"][i],
            "wind_speed":  data["hourly"]["windspeed_10m"][i],
        }

    return records

def save_to_mongodb(records):
    client = MongoClient(MONGODB_URI)
    db     = client["pearls_aqi"]
    col    = db["aqi_features"]

    # clear old data
    col.drop()

    # insert all
    col.insert_many(records)
    print(f"Saved {len(records)} records to MongoDB ✅")
    client.close()

if __name__ == "__main__":
    print("Fetching air quality data...")
    aq_records = fetch_air_quality()
    print(f"Got {len(aq_records)} air quality records")

    print("Fetching weather data...")
    weather_records = fetch_weather()
    print(f"Got {len(weather_records)} weather records")

    print("Merging...")
    merged = []
    for record in aq_records:
        key = record["timestamp"]
        if key in weather_records:
            record.update(weather_records[key])
            merged.append(record)

    print(f"Merged: {len(merged)} records")
    print("\n--- Sample Record ---")
    for k, v in merged[0].items():
        print(f"  {k}: {v}")

    print("\nSaving to MongoDB...")
    save_to_mongodb(merged)