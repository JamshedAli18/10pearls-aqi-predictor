# ============================================================
# Pearls AQI Predictor — Streamlit Dashboard
# Sukkur, Sindh, Pakistan
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import requests
import joblib
import shap
import os
import certifi
import plotly.graph_objects as go
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
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Pearls AQI Predictor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# STYLES — light mood
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.block-container { padding: 2rem 3rem 3rem 3rem; }
.main { background-color: #f0f4f8; }

.top-header {
    background: linear-gradient(135deg, #e8f4fd 0%, #dbeafe 100%);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid #bfdbfe;
}
.top-left h1 {
    font-size: 2.2rem;
    font-weight: 900;
    color: #1e3a5f;
    margin: 0;
    letter-spacing: -0.5px;
}
.top-left p {
    font-size: 0.85rem;
    font-weight: 300;
    color: #5b7fa6;
    margin: 0.3rem 0 0 0;
}
.top-right { text-align: right; }
.aqi-big {
    font-size: 4.5rem;
    font-weight: 900;
    line-height: 1;
}
.aqi-cat {
    font-size: 1rem;
    font-weight: 600;
    margin-top: 0.2rem;
}
.aqi-meta {
    font-size: 0.8rem;
    font-weight: 300;
    color: #5b7fa6;
    margin-top: 0.4rem;
}
.card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem 1.8rem;
    box-shadow: 0 2px 12px rgba(100,150,200,0.1);
    height: 100%;
    border-top: 4px solid;
}
.card-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #94a3b8;
    margin-bottom: 0.5rem;
}
.card-date {
    font-size: 0.85rem;
    font-weight: 400;
    color: #64748b;
    margin-bottom: 0.5rem;
}
.card-aqi {
    font-size: 3.5rem;
    font-weight: 900;
    line-height: 1;
}
.card-cat {
    font-size: 0.95rem;
    font-weight: 600;
    margin-top: 0.3rem;
}
.card-meta {
    font-size: 0.8rem;
    font-weight: 300;
    color: #94a3b8;
    margin-top: 1rem;
    padding-top: 0.8rem;
    border-top: 1px solid #f1f5f9;
}
.alert-danger {
    background: #fef2f2;
    border: 1.5px solid #fca5a5;
    border-radius: 14px;
    padding: 1.5rem 2rem;
}
.alert-warning {
    background: #fffbeb;
    border: 1.5px solid #fcd34d;
    border-radius: 14px;
    padding: 1.5rem 2rem;
}
.alert-moderate {
    background: #fff7ed;
    border: 1.5px solid #fdba74;
    border-radius: 14px;
    padding: 1.5rem 2rem;
}
.alert-success {
    background: #f0fdf4;
    border: 1.5px solid #86efac;
    border-radius: 14px;
    padding: 1.5rem 2rem;
}
.alert-tag {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
}
.alert-heading {
    font-size: 1.15rem;
    font-weight: 700;
    margin-top: 0.4rem;
    color: #1e3a5f;
}
.alert-body {
    font-size: 0.88rem;
    font-weight: 300;
    color: #475569;
    margin-top: 0.5rem;
    line-height: 1.7;
}
.rec-title {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #64748b;
    margin-top: 1.2rem;
    margin-bottom: 0.4rem;
}
.rec-item {
    font-size: 0.85rem;
    font-weight: 300;
    color: #475569;
    margin-top: 0.3rem;
    padding-left: 0.8rem;
    border-left: 2px solid #cbd5e1;
    margin-bottom: 0.3rem;
}
.section-heading {
    font-size: 1.2rem;
    font-weight: 700;
    color: #1e3a5f;
    margin-bottom: 0.2rem;
    margin-top: 0.5rem;
}
.section-sub {
    font-size: 0.82rem;
    font-weight: 300;
    color: #94a3b8;
    margin-bottom: 1.2rem;
}
.stat-card {
    background: white;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    box-shadow: 0 2px 8px rgba(100,150,200,0.08);
    text-align: center;
    border: 1px solid #e2e8f0;
}
.stat-value {
    font-size: 1.8rem;
    font-weight: 900;
    color: #1e3a5f;
}
.stat-label {
    font-size: 0.75rem;
    font-weight: 400;
    color: #94a3b8;
    margin-top: 0.2rem;
}
.footer-text {
    font-size: 0.75rem;
    font-weight: 300;
    color: #94a3b8;
    text-align: center;
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid #e2e8f0;
}
div[data-testid="stTabs"] button {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 0.85rem;
    letter-spacing: 0.5px;
}
section[data-testid="stSidebar"] {
    background-color: #f8fafc;
    border-right: 1px solid #e2e8f0;
}
</style>
""", unsafe_allow_html=True)

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

def aqi_color(cat):
    return {
        "Good":           "#16a34a",
        "Fair":           "#2563eb",
        "Moderate":       "#d97706",
        "Poor":           "#ea580c",
        "Very Poor":      "#dc2626",
        "Extremely Poor": "#991b1b"
    }.get(cat, "#64748b")

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

def chart_layout(title, xtitle="", ytitle="", height=340):
    return dict(
        title=dict(text=title, font=dict(size=13, family="Inter", color="#1e3a5f")),
        xaxis=dict(title=xtitle, showgrid=False, color="#94a3b8"),
        yaxis=dict(title=ytitle, gridcolor="#f1f5f9", color="#94a3b8"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter", color="#475569"),
        height=height,
        margin=dict(t=50, b=50, l=50, r=20)
    )

feature_cols = [
    "hour", "day", "month",
    "temperature", "humidity", "wind_speed",
    "pm2_5", "pm10", "no2", "co", "o3",
    "aqi_lag_1", "aqi_lag_3", "aqi_lag_24",
    "aqi_rolling_mean_24", "aqi_change_rate",
    "time_of_day", "is_weekend", "season"
]

# ============================================================
# LOAD MODELS
# ============================================================
@st.cache_resource
def load_models():
    ridge  = joblib.load("../models/ridge.pkl")
    lasso  = joblib.load("../models/lasso.pkl")
    gb     = joblib.load("../models/gradient_boosting.pkl")
    scaler = joblib.load("../models/scaler.pkl")
    le     = joblib.load("../models/label_encoder.pkl")
    return ridge, lasso, gb, scaler, le

ridge, lasso, gb, scaler, le = load_models()

# ============================================================
# SIDEBAR — model selector
# ============================================================
st.sidebar.markdown("## Pearls AQI")
st.sidebar.markdown("---")
st.sidebar.markdown("### Prediction Model")
selected_model_name = st.sidebar.selectbox(
    "Select model for forecast:",
    ["Ridge Regression", "Lasso", "Gradient Boosting"],
    index=0
)
model_map = {
    "Ridge Regression":  ridge,
    "Lasso":             lasso,
    "Gradient Boosting": gb
}
selected_model = model_map[selected_model_name]

st.sidebar.markdown("---")
st.sidebar.markdown("### Model Performance")
perf_map = {
    "Ridge Regression":  {"R²": "1.0000", "RMSE": "0.0662"},
    "Lasso":             {"R²": "0.9999", "RMSE": "0.1469"},
    "Gradient Boosting": {"R²": "0.9995", "RMSE": "0.2710"},
}
perf = perf_map[selected_model_name]
st.sidebar.markdown(f"**R² Score:** {perf['R²']}")
st.sidebar.markdown(f"**RMSE:** {perf['RMSE']}")

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.markdown("Data: Open-Meteo + OpenWeather")
st.sidebar.markdown("Database: MongoDB Atlas")
st.sidebar.markdown(f"Location: {os.getenv('CITY')}, Sindh, PK")

# ============================================================
# FETCH DATA
# ============================================================
@st.cache_data(ttl=3600)
def fetch_current_weather():
    url  = f"https://api.openweathermap.org/data/2.5/weather?q={CITY},PK&appid={API_KEY}&units=metric"
    data = requests.get(url).json()
    return {
        "temperature": data["main"]["temp"],
        "humidity":    data["main"]["humidity"],
        "wind_speed":  data["wind"]["speed"],
        "description": data["weather"][0]["description"].title()
    }

@st.cache_data(ttl=3600)
def fetch_current_pollution():
    url  = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={LAT}&lon={LON}&appid={API_KEY}"
    data = requests.get(url).json()
    comp = data["list"][0]["components"]
    return {
        "pm2_5": comp["pm2_5"],
        "pm10":  comp["pm10"],
        "no2":   comp["no2"],
        "co":    comp["co"],
        "o3":    comp["o3"],
    }

@st.cache_data(ttl=3600)
def fetch_weather_forecast():
    url  = f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"
    data = requests.get(url).json()
    records = []
    for item in data["list"]:
        dt = datetime.fromtimestamp(item["dt"], tz=timezone.utc)
        records.append({
            "timestamp":   dt,
            "temperature": item["main"]["temp"],
            "humidity":    item["main"]["humidity"],
            "wind_speed":  item["wind"]["speed"]
        })
    return pd.DataFrame(records)

@st.cache_data(ttl=3600)
def load_historical():
    client = MongoClient(MONGODB_URI, tls=True, tlsCAFile=certifi.where())
    db     = client["pearls_aqi"]
    data   = list(db["aqi_engineered"].find({}, {"_id": 0}))
    client.close()
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

# ============================================================
# RUN FORECAST
# ============================================================
def run_forecast(model):
    hist_df          = load_historical()
    weather_forecast = fetch_weather_forecast()
    pollution        = fetch_current_pollution()

    now              = datetime.now(timezone.utc)
    aqi_history      = hist_df["aqi"].tolist()
    season_map       = {"winter": 0, "spring": 1, "summer": 2, "autumn": 3}
    tod_classes      = list(le.classes_)
    hourly_forecasts = []

    for _, row in weather_forecast.iterrows():
        dt = row["timestamp"]
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
            "temperature":         row["temperature"],
            "humidity":            row["humidity"],
            "wind_speed":          row["wind_speed"],
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

        if selected_model_name == "Gradient Boosting":
            scaled   = features[feature_cols]
        else:
            scaled   = scaler.transform(features[feature_cols])

        pred_aqi = float(max(0, model.predict(scaled)[0]))

        hourly_forecasts.append({
            "timestamp":     dt,
            "date":          dt.strftime("%Y-%m-%d"),
            "hour":          dt.hour,
            "predicted_aqi": round(pred_aqi, 1),
            "temperature":   row["temperature"],
            "humidity":      row["humidity"],
            "wind_speed":    row["wind_speed"]
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
    return df_fc, daily

# ============================================================
# LOAD ALL DATA
# ============================================================
current_weather    = fetch_current_weather()
current_poll       = fetch_current_pollution()
hist_df            = load_historical()
df_forecast, daily = run_forecast(selected_model)

current_aqi = float(hist_df["aqi"].iloc[-1])
current_cat = aqi_label(current_aqi)
current_col = aqi_color(current_cat)

# ============================================================
# HEADER
# ============================================================
st.markdown(f"""
<div class="top-header">
    <div class="top-left">
        <h1>Pearls AQI Predictor</h1>
        <p>
            {CITY}, Sindh, Pakistan &nbsp;|&nbsp;
            {datetime.now().strftime("%A, %d %B %Y")} &nbsp;|&nbsp;
            {current_weather['description']}
        </p>
    </div>
    <div class="top-right">
        <div class="aqi-big" style="color:{current_col}">{current_aqi:.0f}</div>
        <div class="aqi-cat" style="color:{current_col}">{current_cat}</div>
        <div class="aqi-meta">
            {current_weather['temperature']}°C &nbsp;|&nbsp;
            {current_weather['humidity']}% humidity &nbsp;|&nbsp;
            {current_weather['wind_speed']} m/s wind
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "  Forecast  ",
    "  History  ",
    "  Analysis  ",
    "  Alerts  "
])

# ============================================================
# TAB 1 — FORECAST
# ============================================================
with tab1:
    st.markdown('<p class="section-heading">3-Day Air Quality Forecast</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-sub">Predicted AQI for the next 3 days using {selected_model_name} model</p>', unsafe_allow_html=True)

    cols   = st.columns(3)
    labels = ["Tomorrow", "Day 2", "Day 3"]

    for col, label, (_, row) in zip(cols, labels, daily.iterrows()):
        cat   = row["category"]
        color = aqi_color(cat)
        with col:
            st.markdown(f"""
            <div class="card" style="border-top-color:{color}">
                <div class="card-label">{label}</div>
                <div class="card-date">{row['date']}</div>
                <div class="card-aqi" style="color:{color}">{row['predicted_aqi']}</div>
                <div class="card-cat" style="color:{color}">{cat}</div>
                <div class="card-meta">
                    {row['temperature']:.1f}°C &nbsp;|&nbsp;
                    {row['humidity']:.0f}% humidity &nbsp;|&nbsp;
                    {row['wind_speed']:.1f} m/s wind
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=daily["date"],
            y=daily["predicted_aqi"],
            marker_color=[aqi_color(c) for c in daily["category"]],
            text=daily["category"],
            textposition="outside",
            width=0.35
        ))
        fig1.update_layout(**chart_layout("3-Day Average AQI Forecast", "Date", "AQI"))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=list(range(len(df_forecast))),
            y=df_forecast["predicted_aqi"],
            mode="lines+markers",
            marker=dict(size=5, color="#3b82f6"),
            line=dict(color="#3b82f6", width=2),
            fill="tozeroy",
            fillcolor="rgba(59,130,246,0.06)"
        ))
        fig2.update_layout(**chart_layout("Forecast Intervals — Next 72 Hours", "Intervals (3-hourly)", "Predicted AQI"))
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=list(range(len(df_forecast))),
            y=df_forecast["temperature"],
            mode="lines",
            line=dict(color="#f59e0b", width=2),
            fill="tozeroy",
            fillcolor="rgba(245,158,11,0.06)"
        ))
        fig3.update_layout(**chart_layout("Temperature Forecast", "Intervals (3-hourly)", "°C"))
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(
            x=list(range(len(df_forecast))),
            y=df_forecast["humidity"],
            mode="lines",
            line=dict(color="#06b6d4", width=2),
            fill="tozeroy",
            fillcolor="rgba(6,182,212,0.06)"
        ))
        fig4.update_layout(**chart_layout("Humidity Forecast", "Intervals (3-hourly)", "%"))
        st.plotly_chart(fig4, use_container_width=True)

# ============================================================
# TAB 2 — HISTORY
# ============================================================
with tab2:
    st.markdown('<p class="section-heading">Historical Air Quality</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Last 3 months of recorded AQI and pollutant data for Sukkur</p>', unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value" style="color:#2563eb">{hist_df['aqi'].mean():.0f}</div>
            <div class="stat-label">Average AQI</div>
        </div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value" style="color:#dc2626">{hist_df['aqi'].max():.0f}</div>
            <div class="stat-label">Max AQI</div>
        </div>""", unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value" style="color:#16a34a">{hist_df['aqi'].min():.0f}</div>
            <div class="stat-label">Min AQI</div>
        </div>""", unsafe_allow_html=True)
    with s4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value" style="color:#7c3aed">{len(hist_df)}</div>
            <div class="stat-label">Total Records</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col5, col6 = st.columns(2)

    with col5:
        daily_hist = hist_df.groupby("date")["aqi"].mean().reset_index()
        fig5 = go.Figure()
        fig5.add_trace(go.Scatter(
            x=daily_hist["date"],
            y=daily_hist["aqi"],
            mode="lines",
            line=dict(color="#2563eb", width=2),
            fill="tozeroy",
            fillcolor="rgba(37,99,235,0.05)"
        ))
        fig5.update_layout(**chart_layout("Daily Average AQI — Last 3 Months", "Date", "AQI"))
        st.plotly_chart(fig5, use_container_width=True)

    with col6:
        fig6 = go.Figure()
        fig6.add_trace(go.Scatter(
            x=hist_df["timestamp"],
            y=hist_df["temperature"],
            mode="lines",
            line=dict(color="#f59e0b", width=1),
        ))
        fig6.update_layout(**chart_layout("Temperature — Last 3 Months", "Date", "°C"))
        st.plotly_chart(fig6, use_container_width=True)

    col7, col8 = st.columns(2)

    with col7:
        fig7 = go.Figure()
        fig7.add_trace(go.Scatter(
            x=hist_df["timestamp"],
            y=hist_df["pm10"],
            mode="lines",
            line=dict(color="#dc2626", width=1),
            name="PM10"
        ))
        fig7.add_trace(go.Scatter(
            x=hist_df["timestamp"],
            y=hist_df["pm2_5"],
            mode="lines",
            line=dict(color="#f59e0b", width=1),
            name="PM2.5"
        ))
        fig7.update_layout(**chart_layout("PM10 and PM2.5 — Last 3 Months", "Date", "µg/m³"))
        st.plotly_chart(fig7, use_container_width=True)

    with col8:
        monthly = hist_df.groupby("month")["aqi"].mean().reset_index()
        month_names = {2: "Feb", 3: "Mar", 4: "Apr", 5: "May",
                       6: "Jun", 7: "Jul", 8: "Aug", 9: "Sep"}
        monthly["month_name"] = monthly["month"].map(month_names)
        fig8 = go.Figure()
        fig8.add_trace(go.Bar(
            x=monthly["month_name"],
            y=monthly["aqi"],
            marker_color="#3b82f6",
            opacity=0.8
        ))
        fig8.update_layout(**chart_layout("Monthly Average AQI", "Month", "AQI"))
        st.plotly_chart(fig8, use_container_width=True)

# ============================================================
# TAB 3 — ANALYSIS
# ============================================================
with tab3:
    st.markdown('<p class="section-heading">Model Analysis</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">SHAP feature importance and current pollutant levels</p>', unsafe_allow_html=True)

    col9, col10 = st.columns(2)

    with col9:
        @st.cache_data
        def compute_shap():
            df         = load_historical()
            le_enc     = joblib.load("../models/label_encoder.pkl")
            sc         = joblib.load("../models/scaler.pkl")
            rdg        = joblib.load("../models/ridge.pkl")
            season_map = {"winter": 0, "spring": 1, "summer": 2, "autumn": 3}
            df["time_of_day"] = le_enc.transform(df["time_of_day"])
            df["season"]      = df["season"].map(season_map).fillna(0).astype(int)
            X    = df[feature_cols]
            X_sc = sc.transform(X)
            exp  = shap.LinearExplainer(rdg, X_sc)
            sv   = exp.shap_values(X_sc)
            imp  = np.abs(sv).mean(axis=0)
            return imp

        importance  = compute_shap()
        sorted_idx  = np.argsort(importance)[::-1]
        sorted_feat = [feature_cols[i] for i in sorted_idx]
        sorted_imp  = importance[sorted_idx]

        fig9 = go.Figure()
        fig9.add_trace(go.Bar(
            x=sorted_feat,
            y=sorted_imp,
            marker_color="#3b82f6",
            opacity=0.85
        ))
        fig9.update_layout(**chart_layout("SHAP Feature Importance — Ridge Model", "Feature", "Mean |SHAP value|", height=400))
        fig9.update_xaxes(tickangle=45)
        st.plotly_chart(fig9, use_container_width=True)

    with col10:
        pollutants = ["pm2_5", "pm10", "no2", "co", "o3"]
        values     = [current_poll[p] for p in pollutants]
        colors_p   = ["#dc2626", "#f59e0b", "#2563eb", "#16a34a", "#7c3aed"]

        fig10 = go.Figure()
        fig10.add_trace(go.Bar(
            x=pollutants,
            y=values,
            marker_color=colors_p,
            text=[f"{v:.1f}" for v in values],
            textposition="outside"
        ))
        fig10.update_layout(**chart_layout("Current Pollutant Levels", "Pollutant", "Concentration (µg/m³)", height=400))
        st.plotly_chart(fig10, use_container_width=True)

    st.markdown('<p class="section-heading">Model Performance</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Evaluation metrics for all trained models</p>', unsafe_allow_html=True)

    metrics_df = pd.DataFrame([
        {"Model": "Ridge Regression",   "R²": 1.0000, "RMSE": 0.0662, "MAE": 0.0438, "Verdict": "No overfitting", "Status": "Primary"},
        {"Model": "Lasso",              "R²": 0.9999, "RMSE": 0.1469, "MAE": 0.1097, "Verdict": "No overfitting", "Status": "Secondary"},
        {"Model": "Gradient Boosting",  "R²": 0.9995, "RMSE": 0.2710, "MAE": 0.1148, "Verdict": "No overfitting", "Status": "Secondary"},
        {"Model": "Random Forest",      "R²": 0.9972, "RMSE": 0.6600, "MAE": 0.2758, "Verdict": "No overfitting", "Status": "Trained"},
        {"Model": "ElasticNet",         "R²": 0.9960, "RMSE": 0.7914, "MAE": 0.5632, "Verdict": "No overfitting", "Status": "Trained"},
        {"Model": "LSTM",               "R²": -19.10, "RMSE": 61.966, "MAE": 52.577, "Verdict": "Overfitting",    "Status": "Experimental"},
    ])
    st.dataframe(metrics_df, use_container_width=True, hide_index=True)

# ============================================================
# TAB 4 — ALERTS
# ============================================================
with tab4:
    st.markdown('<p class="section-heading">Health Alerts</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Air quality advisories based on 3-day forecast for Sukkur</p>', unsafe_allow_html=True)

    max_aqi = daily["predicted_aqi"].max()
    max_cat = aqi_label(max_aqi)

    if max_aqi > 100:
        st.markdown(f"""
        <div class="alert-danger">
            <div class="alert-tag" style="color:#dc2626">Critical Health Warning</div>
            <div class="alert-heading">Extremely Poor Air Quality Forecast for {CITY}</div>
            <div class="alert-body">
                Air quality is predicted to reach <strong>Extremely Poor (AQI {max_aqi:.0f})</strong>
                over the next 3 days. This is a serious health hazard for everyone in {CITY}.
                Prolonged exposure can cause severe respiratory and cardiovascular effects.
            </div>
            <div class="rec-title">Immediate Recommendations</div>
            <div class="rec-item">Stay indoors as much as possible and keep all windows closed</div>
            <div class="rec-item">Wear N95 or equivalent masks if outdoor activity is unavoidable</div>
            <div class="rec-item">Use air purifiers indoors if available</div>
            <div class="rec-item">Children, elderly and people with respiratory conditions must avoid all outdoor activities</div>
            <div class="rec-item">Seek medical attention immediately if experiencing breathing difficulties</div>
        </div>
        """, unsafe_allow_html=True)

    elif max_aqi > 80:
        st.markdown(f"""
        <div class="alert-danger">
            <div class="alert-tag" style="color:#dc2626">Health Warning</div>
            <div class="alert-heading">Very Poor Air Quality Expected</div>
            <div class="alert-body">
                Air quality is predicted to be <strong>Very Poor (AQI {max_aqi:.0f})</strong>.
                Everyone may experience health effects. Sensitive groups face serious risk.
            </div>
            <div class="rec-title">Recommendations</div>
            <div class="rec-item">Avoid prolonged outdoor activities</div>
            <div class="rec-item">Wear masks when outdoors</div>
            <div class="rec-item">Keep windows closed during peak pollution hours</div>
        </div>
        """, unsafe_allow_html=True)

    elif max_aqi > 60:
        st.markdown(f"""
        <div class="alert-warning">
            <div class="alert-tag" style="color:#d97706">Health Advisory</div>
            <div class="alert-heading">Poor Air Quality Expected</div>
            <div class="alert-body">
                Air quality is predicted to be <strong>Poor (AQI {max_aqi:.0f})</strong>.
                Everyone may begin to experience health effects with prolonged exposure.
            </div>
            <div class="rec-title">Recommendations</div>
            <div class="rec-item">Limit prolonged outdoor exertion</div>
            <div class="rec-item">Sensitive groups should stay indoors</div>
        </div>
        """, unsafe_allow_html=True)

    elif max_aqi > 40:
        st.markdown(f"""
        <div class="alert-moderate">
            <div class="alert-tag" style="color:#ea580c">Advisory</div>
            <div class="alert-heading">Moderate Air Quality Expected</div>
            <div class="alert-body">
                Air quality is predicted to be <strong>Moderate (AQI {max_aqi:.0f})</strong>.
                Unusually sensitive individuals should consider limiting outdoor activity.
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown(f"""
        <div class="alert-success">
            <div class="alert-tag" style="color:#16a34a">All Clear</div>
            <div class="alert-heading">Good Air Quality Expected</div>
            <div class="alert-body">
                Air quality is predicted to be <strong>{max_cat} (AQI {max_aqi:.0f})</strong>.
                No health impacts expected. Enjoy outdoor activities freely.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<p class="section-heading">European AQI Scale Reference</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Open-Meteo European Air Quality Index scale used in this project</p>', unsafe_allow_html=True)

    scale_df = pd.DataFrame([
        {"AQI Range": "0 - 20",   "Category": "Good",           "Health Impact": "No health risk. Air quality is satisfactory."},
        {"AQI Range": "21 - 40",  "Category": "Fair",           "Health Impact": "Acceptable quality. Minor concern for very sensitive people."},
        {"AQI Range": "41 - 60",  "Category": "Moderate",       "Health Impact": "Sensitive groups may experience health effects."},
        {"AQI Range": "61 - 80",  "Category": "Poor",           "Health Impact": "Everyone may experience health effects."},
        {"AQI Range": "81 - 100", "Category": "Very Poor",      "Health Impact": "Serious health effects for everyone."},
        {"AQI Range": "100+",     "Category": "Extremely Poor", "Health Impact": "Emergency conditions. Serious risk for entire population."},
    ])
    st.dataframe(scale_df, use_container_width=True, hide_index=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown(f"""
<div class="footer-text">
    Pearls AQI Predictor &nbsp;|&nbsp;
    Data: Open-Meteo + OpenWeather API &nbsp;|&nbsp;
    Database: MongoDB Atlas &nbsp;|&nbsp;
    Models: Ridge Regression, Lasso, Gradient Boosting &nbsp;|&nbsp;
    Location: {CITY}, Sindh, Pakistan &nbsp;|&nbsp;
    Last updated: {datetime.now().strftime("%d %b %Y, %H:%M")}
</div>
""", unsafe_allow_html=True)