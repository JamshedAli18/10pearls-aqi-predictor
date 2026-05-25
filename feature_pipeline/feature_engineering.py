import pandas as pd
import numpy as np
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv("../.env")

MONGODB_URI = os.getenv("MONGODB_URI")

def load_from_mongodb():
    client = MongoClient(MONGODB_URI)
    db     = client["pearls_aqi"]
    col    = db["aqi_features"]
    data   = list(col.find({}, {"_id": 0}))
    client.close()
    return pd.DataFrame(data)

def engineer_features(df):
    # sort by timestamp
    df = df.sort_values("timestamp").reset_index(drop=True)

    # lag features
    df["aqi_lag_1"]           = df["aqi"].shift(1)
    df["aqi_lag_3"]           = df["aqi"].shift(3)
    df["aqi_lag_24"]          = df["aqi"].shift(24)

    # rolling average
    df["aqi_rolling_mean_24"] = df["aqi"].shift(1).rolling(window=24).mean()

    # change rate
    df["aqi_change_rate"]     = df["aqi"].diff()

    # time of day
    def get_time_of_day(hour):
        if 5 <= hour < 12:   return "morning"
        elif 12 <= hour < 17: return "afternoon"
        elif 17 <= hour < 21: return "evening"
        else:                 return "night"

    df["time_of_day"] = df["hour"].apply(get_time_of_day)

    # weekend flag
    df["timestamp"]   = pd.to_datetime(df["timestamp"])
    df["is_weekend"]  = df["timestamp"].dt.dayofweek.isin([5, 6]).astype(int)

    # season
    def get_season(month):
        if month in [12, 1, 2]: return "winter"
        elif month in [3, 4, 5]: return "spring"
        elif month in [6, 7, 8]: return "summer"
        else:                    return "autumn"

    df["season"] = df["month"].apply(get_season)

    # drop NaN rows from lag features
    df = df.dropna().reset_index(drop=True)

    return df

def save_engineered_to_mongodb(df):
    client = MongoClient(MONGODB_URI)
    db     = client["pearls_aqi"]
    col    = db["aqi_engineered"]

    # clear old
    col.drop()

    # convert to dict and insert
    records = df.to_dict("records")
    col.insert_many(records)
    print(f"Saved {len(records)} engineered records to MongoDB ✅")
    client.close()

if __name__ == "__main__":
    print("Loading data from MongoDB...")
    df = load_from_mongodb()
    print(f"Loaded: {df.shape}")

    print("Engineering features...")
    df = engineer_features(df)
    print(f"After engineering: {df.shape}")

    print("\n--- Columns ---")
    print(df.columns.tolist())

    print("\n--- Sample Row ---")
    print(df.iloc[0].to_dict())

    print("\nSaving engineered data...")
    save_engineered_to_mongodb(df)