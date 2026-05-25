# ============================================================
# Run Training Pipeline
# Called by GitHub Actions every day
# Retrains Ridge model with latest data from MongoDB
# ============================================================

import os
import sys
import pandas as pd
import numpy as np
import certifi
import joblib
from pymongo import MongoClient
from sklearn.linear_model import Ridge
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

feature_cols = [
    "hour", "day", "month",
    "temperature", "humidity", "wind_speed",
    "pm2_5", "pm10", "no2", "co", "o3",
    "aqi_lag_1", "aqi_lag_3", "aqi_lag_24",
    "aqi_rolling_mean_24", "aqi_change_rate",
    "time_of_day", "is_weekend", "season"
]

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

def engineer(df):
    df = df.sort_values("timestamp").reset_index(drop=True)
    df["aqi"]                     = df["aqi"].astype(float)
    df["aqi_lag_1"]               = df["aqi"].shift(1)
    df["aqi_lag_3"]               = df["aqi"].shift(3)
    df["aqi_lag_24"]              = df["aqi"].shift(24)
    df["aqi_rolling_mean_24"]     = df["aqi"].shift(1).rolling(24).mean()
    df["aqi_change_rate"]         = df["aqi"].diff()
    df["timestamp"]               = pd.to_datetime(df["timestamp"])
    df["hour"]                    = df["timestamp"].dt.hour
    df["day"]                     = df["timestamp"].dt.day
    df["month"]                   = df["timestamp"].dt.month
    df["time_of_day"]             = df["hour"].apply(get_time_of_day)
    df["is_weekend"]              = df["timestamp"].dt.dayofweek.isin([5,6]).astype(int)
    df["season"]                  = df["month"].apply(get_season)
    return df.dropna().reset_index(drop=True)

if __name__ == "__main__":
    print("Connecting to MongoDB...")
    client = MongoClient(MONGODB_URI, tls=True, tlsCAFile=certifi.where())
    db     = client["pearls_aqi"]

    print("Fetching features...")
    data = list(db["aqi_features"].find({}, {"_id": 0}))
    client.close()
    print(f"Fetched {len(data)} records")

    df = pd.DataFrame(data)
    df = engineer(df)
    print(f"After engineering: {df.shape}")

    # prepare
    le     = LabelEncoder()
    scaler = StandardScaler()
    df["time_of_day"] = le.fit_transform(df["time_of_day"])
    df["season"]      = pd.factorize(df["season"])[0]
    X        = df[feature_cols]
    y        = df["aqi"]
    X_scaled = scaler.fit_transform(X)

    # train
    print("Training Ridge model...")
    model = Ridge(alpha=1.0)
    model.fit(X_scaled, y)

    preds = model.predict(X_scaled)
    r2    = r2_score(y, preds)
    rmse  = np.sqrt(mean_squared_error(y, preds))
    mae   = mean_absolute_error(y, preds)
    print(f"R²: {r2:.4f} | RMSE: {rmse:.4f} | MAE: {mae:.4f}")

    # save models
    os.makedirs("models", exist_ok=True)
    joblib.dump(model,  "models/ridge.pkl")
    joblib.dump(scaler, "models/scaler.pkl")
    joblib.dump(le,     "models/label_encoder.pkl")
    print("Models saved ✅")

    # save metrics to MongoDB
    client = MongoClient(MONGODB_URI, tls=True, tlsCAFile=certifi.where())
    db     = client["pearls_aqi"]
    db["model_metadata"].insert_one({
        "model":      "Ridge",
        "r2":         round(r2, 4),
        "rmse":       round(rmse, 4),
        "mae":        round(mae, 4),
        "trained_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "records":    len(df)
    })
    client.close()
    print("Metrics saved to MongoDB ✅")
    print("Training pipeline complete ✅")