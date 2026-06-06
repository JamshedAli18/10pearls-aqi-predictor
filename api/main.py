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
base       = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(base, "..", "models")

gb     = joblib.load(os.path.join(models_dir, "gradient_boosting.pkl"))
rf     = joblib.load(os.path.join(models_dir, "random_forest.pkl"))
ridge  = joblib.load(os.path.join(models_dir, "ridge.pkl"))
scaler = joblib.load(os.path.join(models_dir, "scaler.pkl"))
le     = joblib.load(os.path.join(models_dir, "label_encoder.pkl"))

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
    return {
        "gradient_boosting": gb,
        "random_forest":     rf,
        "ridge":             ridge
    }.get(model_name, gb)

def scale_features(model_name, features):
    if model_name in ["gradient_boosting", "random_forest"]:
        return features[feature_cols]
    return scaler.transform(features[feature_cols])

# ============================================================
# ROUTES
# ============================================================

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
            "/models",
            "/health"
        ]
    }

@app.get("/health")
def health():
    return {
        "status":    "ok",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/current")
def get_current():
    weather = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?q={CITY},PK&appid={API_KEY}&units=metric"
    ).json()

    # current AQI from Open-Meteo European scale
    today  = datetime.now().strftime("%Y-%m-%d")
    aq_url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality?"
        f"latitude={LAT}&longitude={LON}"
        f"&hourly=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone,european_aqi"
        f"&start_date={today}&end_date={today}"
    )
    aq_data = requests.get(aq_url).json()
    hour    = min(datetime.now().hour, len(aq_data["hourly"]["european_aqi"]) - 1)

    aqi   = aq_data["hourly"]["european_aqi"][hour]
    pm2_5 = aq_data["hourly"]["pm2_5"][hour]
    pm10  = aq_data["hourly"]["pm10"][hour]
    no2   = aq_data["hourly"]["nitrogen_dioxide"][hour]
    co    = aq_data["hourly"]["carbon_monoxide"][hour]
    o3    = aq_data["hourly"]["ozone"][hour]

    return {
        "city":        CITY,
        "timestamp":   datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "aqi":         float(aqi) if aqi is not None else 0.0,
        "category":    aqi_label(float(aqi) if aqi is not None else 0.0),
        "temperature": weather["main"]["temp"],
        "humidity":    weather["main"]["humidity"],
        "wind_speed":  weather["wind"]["speed"],
        "pollutants": {
            "pm2_5": float(pm2_5) if pm2_5 is not None else 0.0,
            "pm10":  float(pm10)  if pm10  is not None else 0.0,
            "no2":   float(no2)   if no2   is not None else 0.0,
            "co":    float(co)    if co    is not None else 0.0,
            "o3":    float(o3)    if o3    is not None else 0.0,
        }
    }

@app.get("/forecast")
def get_forecast():
    return get_forecast_by_model("gradient_boosting")

@app.get("/forecast/{model_name}")
def get_forecast_by_model(model_name: str):
    model = get_model(model_name)

    client      = get_mongo_client()
    db          = client["pearls_aqi"]
    data        = list(db["aqi_engineered"].find(
        {}, {"_id": 0, "aqi": 1, "timestamp": 1}
    ).sort("timestamp", 1))
    client.close()

    hist_df     = pd.DataFrame(data)
    aqi_history = hist_df["aqi"].tolist()

    forecast_url  = f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"
    forecast_data = requests.get(forecast_url).json()

    today  = datetime.now().strftime("%Y-%m-%d")
    aq_url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality?"
        f"latitude={LAT}&longitude={LON}"
        f"&hourly=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone,european_aqi"
        f"&start_date={today}&end_date={today}"
    )
    aq_data = requests.get(aq_url).json()
    hour    = min(datetime.now().hour, len(aq_data["hourly"]["european_aqi"]) - 1)

    pollution = {
        "pm2_5": float(aq_data["hourly"]["pm2_5"][hour] or 0),
        "pm10":  float(aq_data["hourly"]["pm10"][hour]  or 0),
        "no2":   float(aq_data["hourly"]["nitrogen_dioxide"][hour] or 0),
        "co":    float(aq_data["hourly"]["carbon_monoxide"][hour]  or 0),
        "o3":    float(aq_data["hourly"]["ozone"][hour] or 0),
    }

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
            "pm2_5":               pollution["pm2_5"],
            "pm10":                pollution["pm10"],
            "no2":                 pollution["no2"],
            "co":                  pollution["co"],
            "o3":                  pollution["o3"],
            "aqi_lag_1":           aqi_lag_1,
            "aqi_lag_3":           aqi_lag_3,
            "aqi_lag_24":          aqi_lag_24,
            "aqi_rolling_mean_24": aqi_rolling_mean_24,
            "aqi_change_rate":     aqi_change_rate,
            "time_of_day":         tod_enc,
            "is_weekend":          1 if dt.weekday() in [5, 6] else 0,
            "season":              sea_enc
        }])

        scaled   = scale_features(model_name, features)
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
        "city":            CITY,
        "model_used":      model_name,
        "generated":       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "daily_forecast":  daily.to_dict("records"),
        "hourly_forecast": hourly_forecasts
    }

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

@app.get("/models")
def get_models():
    return {
        "available_models": [
            {"name": "gradient_boosting", "r2": 0.9917, "rmse": 1.2187, "status": "primary"},
            {"name": "random_forest",     "r2": 0.9846, "rmse": 1.6580, "status": "secondary"},
            {"name": "ridge",             "r2": 0.8862, "rmse": 4.5046, "status": "secondary"},
        ]
    }