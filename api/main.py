# ============================================================
# Pearls AQI Predictor — FastAPI
# Sukkur, Sindh, Pakistan
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import requests
import joblib
import certifi
import os
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")

load_dotenv("../.env")

API_KEY     = os.getenv("OPENWEATHER_API_KEY")
LAT         = os.getenv("LAT")
LON         = os.getenv("LON")
CITY        = os.getenv("CITY")
MONGODB_URI = os.getenv("MONGODB_URI")

# ============================================================
# FASTAPI APP
# ============================================================
app = FastAPI(
    title="Pearls AQI Predictor API",
    description="Real-time AQI prediction API for Sukkur, Sindh, Pakistan",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ============================================================
# LOAD MODELS
# ============================================================
ridge  = joblib.load("../models/ridge.pkl")
lasso  = joblib.load("../models/lasso.pkl")
gb     = joblib.load("../models/gradient_boosting.pkl")
scaler = joblib.load("../models/scaler.pkl")
le     = joblib.load("../models/label_encoder.pkl")

feature_cols = [
    "hour", "day", "month",
    "temperature", "humidity", "wind_speed",
    "pm2_5", "pm10", "no2", "co", "o3",
    "aqi_lag_1", "aqi_lag_3", "aqi_lag_24",
    "aqi_rolling_mean_24", "aqi_change_rate",
    "time_of_day", "is_weekend", "season"
]

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def aqi_label(aqi):
    aqi = float(aqi)
    if aqi <= 20:    return "Good"
    elif aqi <= 40:  return "Fair"
    elif aqi <= 60:  return "Moderate"
    elif aqi <= 80:  return "Poor"
    elif aqi <= 100: return "Very Poor"
    else:            return "Extremely Poor"

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

def get_mongo_client():
    return MongoClient(MONGODB_URI, tls=True, tlsCAFile=certifi.where())

def get_model(model_name):
    return {"ridge": ridge, "lasso": lasso, "gradient_boosting": gb}.get(model_name, ridge)

# ============================================================
# ROUTES
# ============================================================

# root
@app.get("/")
def root():
    return {
        "project": "Pearls AQI Predictor",
        "city":    CITY,
        "version": "1.0.0",
        "docs":    "/docs",
        "endpoints": [
            "/current",
            "/forecast",
            "/forecast/{model_name}",
            "/historical",
            "/health"
        ]
    }

# health check
@app.get("/health")
def health():
    return {
        "status":    "ok",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# current AQI
@app.get("/current")
def get_current():
    weather = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?q={CITY},PK&appid={API_KEY}&units=metric"
    ).json()
    poll = requests.get(
        f"http://api.openweathermap.org/data/2.5/air_pollution?lat={LAT}&lon={LON}&appid={API_KEY}"
    ).json()

    aqi  = float(poll["list"][0]["main"]["aqi"])
    comp = poll["list"][0]["components"]

    return {
        "city":        CITY,
        "timestamp":   datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "aqi":         aqi,
        "category":    aqi_label(aqi),
        "temperature": weather["main"]["temp"],
        "humidity":    weather["main"]["humidity"],
        "wind_speed":  weather["wind"]["speed"],
        "pollutants": {
            "pm2_5": comp["pm2_5"],
            "pm10":  comp["pm10"],
            "no2":   comp["no2"],
            "co":    comp["co"],
            "o3":    comp["o3"]
        }
    }

# 3-day forecast with default Ridge model
@app.get("/forecast")
def get_forecast():
    return get_forecast_by_model("ridge")

# 3-day forecast with selected model
@app.get("/forecast/{model_name}")
def get_forecast_by_model(model_name: str):
    model = get_model(model_name)

    # load historical
    client  = get_mongo_client()
    db      = client["pearls_aqi"]
    data    = list(db["aqi_engineered"].find({}, {"_id": 0, "aqi": 1, "timestamp": 1}))
    client.close()

    hist_df     = pd.DataFrame(data).sort_values("timestamp").reset_index(drop=True)
    aqi_history = hist_df["aqi"].tolist()

    # fetch forecast weather
    forecast_url  = f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"
    forecast_data = requests.get(forecast_url).json()

    # fetch current pollution
    poll = requests.get(
        f"http://api.openweathermap.org/data/2.5/air_pollution?lat={LAT}&lon={LON}&appid={API_KEY}"
    ).json()
    comp = poll["list"][0]["components"]

    now              = datetime.now(timezone.utc)
    season_map       = {"winter": 0, "spring": 1, "summer": 2, "autumn": 3}
    tod_classes      = list(le.classes_)
    hourly_forecasts = []

    for item in forecast_data["list"]:
        dt = datetime.fromtimestamp(item["dt"], tz=timezone.utc)
        if dt <= now: continue
        if dt > now + timedelta(hours=72): break

        aqi_lag_1           = float(aqi_history[-1])
        aqi_lag_3           = float(aqi_history[-3])  if len(aqi_history) >= 3  else aqi_lag_1
        aqi_lag_24          = float(aqi_history[-24]) if len(aqi_history) >= 24 else aqi_lag_1
        aqi_rolling_mean_24 = float(np.mean(aqi_history[-24:]))
        aqi_change_rate     = float(aqi_history[-1] - aqi_history[-2]) if len(aqi_history) >= 2 else 0.0

        tod     = get_time_of_day(dt.hour)
        tod_enc = tod_classes.index(tod) if tod in tod_classes else 0
        sea_enc = season_map.get(get_season(dt.month), 0)

        features = pd.DataFrame([{
            "hour":                dt.hour,
            "day":                 dt.day,
            "month":               dt.month,
            "temperature":         item["main"]["temp"],
            "humidity":            item["main"]["humidity"],
            "wind_speed":          item["wind"]["speed"],
            "pm2_5":               comp["pm2_5"],
            "pm10":                comp["pm10"],
            "no2":                 comp["no2"],
            "co":                  comp["co"],
            "o3":                  comp["o3"],
            "aqi_lag_1":           aqi_lag_1,
            "aqi_lag_3":           aqi_lag_3,
            "aqi_lag_24":          aqi_lag_24,
            "aqi_rolling_mean_24": aqi_rolling_mean_24,
            "aqi_change_rate":     aqi_change_rate,
            "time_of_day":         tod_enc,
            "is_weekend":          1 if dt.weekday() in [5, 6] else 0,
            "season":              sea_enc
        }])

        if model_name == "gradient_boosting":
            scaled = features[feature_cols]
        else:
            scaled = scaler.transform(features[feature_cols])

        pred_aqi = float(max(0, model.predict(scaled)[0]))
        hourly_forecasts.append({
            "timestamp":     dt.strftime("%Y-%m-%d %H:%M:%S"),
            "date":          dt.strftime("%Y-%m-%d"),
            "hour":          dt.hour,
            "predicted_aqi": round(pred_aqi, 1),
            "category":      aqi_label(pred_aqi),
            "temperature":   item["main"]["temp"],
            "humidity":      item["main"]["humidity"],
            "wind_speed":    item["wind"]["speed"]
        })
        aqi_history.append(pred_aqi)

    df_fc = pd.DataFrame(hourly_forecasts)
    daily = df_fc.groupby("date").agg(
        predicted_aqi=("predicted_aqi", "mean"),
        temperature=("temperature",     "mean"),
        humidity=("humidity",           "mean"),
        wind_speed=("wind_speed",       "mean")
    ).reset_index().head(3)
    daily["predicted_aqi"] = daily["predicted_aqi"].round(1)
    daily["category"]      = daily["predicted_aqi"].apply(aqi_label)

    return {
        "city":       CITY,
        "model_used": model_name,
        "generated":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "daily_forecast": daily.to_dict("records"),
        "hourly_forecast": hourly_forecasts
    }

# historical data
@app.get("/historical")
def get_historical(limit: int = 100):
    client = get_mongo_client()
    db     = client["pearls_aqi"]
    data   = list(db["aqi_engineered"].find(
        {}, {"_id": 0, "timestamp": 1, "aqi": 1, "temperature": 1, "humidity": 1, "pm10": 1, "pm2_5": 1}
    ).sort("timestamp", -1).limit(limit))
    client.close()
    return {
        "city":    CITY,
        "records": len(data),
        "data":    data
    }

# model info
@app.get("/models")
def get_models():
    return {
        "available_models": [
            {"name": "ridge",             "r2": 1.0000, "rmse": 0.0662, "status": "primary"},
            {"name": "lasso",             "r2": 0.9999, "rmse": 0.1469, "status": "secondary"},
            {"name": "gradient_boosting", "r2": 0.9995, "rmse": 0.2710, "status": "secondary"},
        ]
    }