# Pearls AQI Predictor


A complete end-to-end machine learning pipeline for predicting Air Quality Index (AQI) in Sukkur, Sindh, Pakistan for the next 3 days using a 100% serverless stack.

---

## Live Demo

**Streamlit Dashboard:** https://10pearls-aqi-predictor-9ja3gnjph6biv392fykzwy.streamlit.app/

---

## Project Overview

This project predicts AQI using real-time weather and pollution data. It includes automated data collection, feature engineering, model training, and real-time predictions through a web dashboard. The system runs completely automatically using GitHub Actions for CI/CD.

---

## Technology Stack

| Category | Technology |
|---|---|
| Language | Python 3.10+ |
| Data APIs | Open-Meteo (historical), OpenWeather (live + forecast) |
| Database | MongoDB Atlas (Feature Store) |
| ML Models | Ridge Regression, Lasso, Gradient Boosting, LSTM, DNN |
| Explainability | SHAP |
| Dashboard | Streamlit |
| API | FastAPI |
| CI/CD | GitHub Actions |
| Deployment | Streamlit Cloud |

---

## Project Structure

```
pearls-aqi-predictor/
│
├── .github/
│   └── workflows/
│       ├── feature_pipeline.yml    # runs every hour
│       └── training_pipeline.yml   # runs every day
│
├── api/
│   └── main.py                     # FastAPI endpoints
│
├── dashboard/
│   └── streamlit_app.py            # Streamlit dashboard
│
├── data_fetch/
│   ├── fetch_historical.py         # fetch 3 months historical data
│   └── merge_historical.py         # merge AQI + weather data
│
├── feature_pipeline/
│   ├── feature_engineering.py      # engineer features
│   └── run_pipeline.py             # hourly CI/CD pipeline
│
├── models/
│   ├── ridge.pkl
│   ├── lasso.pkl
│   ├── gradient_boosting.pkl
│   ├── scaler.pkl
│   └── label_encoder.pkl
│
├── training_pipeline/
│   ├── 01_train_models.ipynb       # train all models
│   ├── 02_shap_analysis.ipynb      # SHAP feature importance
│   ├── 03_forecast.ipynb           # 3-day forecast
│   └── run_training.py             # daily CI/CD training
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Architecture

```
Open-Meteo API              OpenWeather API
(Historical AQI)            (Live + Forecast)
        │                           │
        └───────────┬───────────────┘
                    │
           Feature Engineering
           (23 features including
            lag, rolling mean,
            time of day, season)
                    │
             MongoDB Atlas
             (Feature Store)
                    │
          ┌─────────┴──────────┐
          │                    │
    Model Training        3-Day Forecast
    (Ridge, Lasso,        (Recursive
    Gradient Boosting,     Prediction)
    LSTM, DNN)                 │
          │                    │
    Model Registry       Streamlit Dashboard
    (saved .pkl files)   (Live on Cloud)
          │
    GitHub Actions
    (Hourly + Daily
     Automation)
```

---

## Data Sources

| Source | Type | Coverage |
|---|---|---|
| Open-Meteo Air Quality | Historical AQI, PM2.5, PM10, NO2, CO, O3 | Last 3 months |
| Open-Meteo Archive | Historical temperature, humidity, wind | Last 3 months |
| OpenWeather Current | Live weather + pollution | Real-time |
| OpenWeather Forecast | 5-day weather forecast | Next 3 days |

---

## Features Engineered

| Feature | Description |
|---|---|
| hour, day, month | Time-based features |
| temperature, humidity, wind_speed | Weather features |
| pm2_5, pm10, no2, co, o3 | Pollutant features |
| aqi_lag_1 | AQI 1 hour ago |
| aqi_lag_3 | AQI 3 hours ago |
| aqi_lag_24 | AQI 24 hours ago |
| aqi_rolling_mean_24 | 24-hour rolling average |
| aqi_change_rate | Rate of AQI change |
| time_of_day | Morning/Afternoon/Evening/Night |
| is_weekend | Weekend flag |
| season | Winter/Spring/Summer/Autumn |

**Total: 23 features, 2160 hourly records**

---

## Model Performance

| Model | R² Score | RMSE | MAE | Verdict |
|---|---|---|---|---|
| Ridge Regression | 1.0000 | 0.0662 | 0.0438 | No overfitting |
| Lasso | 0.9999 | 0.1469 | 0.1097 | No overfitting |
| Gradient Boosting | 0.9995 | 0.2710 | 0.1148 | No overfitting |
| Random Forest | 0.9972 | 0.6600 | 0.2758 | No overfitting |
| ElasticNet | 0.9960 | 0.7914 | 0.5632 | No overfitting |
| LSTM | -19.10 | 61.966 | 52.577 | Overfitting |

**Primary model: Ridge Regression**

---

## AQI Scale (European)

| AQI Range | Category | Health Impact |
|---|---|---|
| 0 - 20 | Good | No health risk |
| 21 - 40 | Fair | Minor concern for sensitive people |
| 41 - 60 | Moderate | Sensitive groups may be affected |
| 61 - 80 | Poor | Everyone may experience effects |
| 81 - 100 | Very Poor | Serious health effects |
| 100+ | Extremely Poor | Emergency conditions |

---

## Dashboard Features

**Tab 1 — Forecast**
- 3-day AQI forecast cards
- Daily average AQI bar chart
- 72-hour forecast trend (3-hour intervals)
- Temperature and humidity forecast

**Tab 2 — History**
- Last 3 months AQI statistics
- Daily average AQI trend
- Temperature trend
- PM10 and PM2.5 trends
- Monthly average AQI

**Tab 3 — Analysis**
- SHAP feature importance chart
- Current pollutant levels
- All model performance metrics

**Tab 4 — Alerts**
- Health warnings based on forecast
- Recommendations by AQI level
- European AQI scale reference

**Sidebar**
- Model selector (Ridge, Lasso, Gradient Boosting)
- Selected model performance metrics

---

## FastAPI Endpoints

| Endpoint | Method | Description |
|---|---|---|
| / | GET | Project info |
| /health | GET | Health check |
| /current | GET | Current AQI and weather |
| /forecast | GET | 3-day forecast (Ridge) |
| /forecast/{model} | GET | 3-day forecast (selected model) |
| /historical | GET | Historical data |
| /models | GET | Available models and metrics |

**API Docs:** http://localhost:8000/docs

---

## CI/CD Pipeline

```
Every Hour:
GitHub Actions → fetch Open-Meteo AQI →
compute lag features → save to MongoDB

Every Day:
GitHub Actions → fetch all features from MongoDB →
retrain Ridge model → save metrics to MongoDB

Streamlit Dashboard:
Cache refreshes every hour → always shows latest data
```

---

## Setup and Installation

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/pearls-aqi-predictor.git
cd pearls-aqi-predictor
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` file
```
OPENWEATHER_API_KEY=your_openweather_key
MONGODB_URI=your_mongodb_uri
LAT=27.7052
LON=68.8574
CITY=Sukkur
```

### 5. Fetch historical data
```bash
cd data_fetch
python fetch_historical.py
```

### 6. Run feature engineering
```bash
cd ../feature_pipeline
python feature_engineering.py
```

### 7. Train models
Open and run all cells in:
```
training_pipeline/01_train_models.ipynb
training_pipeline/02_shap_analysis.ipynb
training_pipeline/03_forecast.ipynb
```

### 8. Run dashboard
```bash
cd ../dashboard
streamlit run streamlit_app.py
```

### 9. Run FastAPI
```bash
cd ../api
uvicorn main:app --reload
```

---

## Deployment

### Streamlit Cloud
1. Push code to GitHub
2. Go to share.streamlit.io
3. Select repo and set main file: `dashboard/streamlit_app.py`
4. Add secrets in Advanced Settings
5. Deploy

### GitHub Actions Secrets Required
```
OPENWEATHER_API_KEY
MONGODB_URI
LAT
LON
CITY
```

---

## SHAP Analysis Results

Top 5 most important features across all models:

| Rank | Feature | Importance |
|---|---|---|
| 1 | aqi_lag_1 | 9.03 |
| 2 | aqi_change_rate | 0.75 |
| 3 | aqi_lag_3 | 0.50 |
| 4 | aqi_rolling_mean_24 | 0.08 |
| 5 | aqi_lag_24 | 0.02 |

**Key insight:** Previous hour's AQI is the strongest predictor — Sukkur's air quality follows strong temporal patterns driven by dust and particulate matter.

---

## Project Requirements Fulfilled

| Requirement | Status |
|---|---|
| Feature Pipeline | ✅ Complete |
| Historical Data Backfill (3 months) | ✅ Complete |
| Training Pipeline | ✅ Complete |
| Multiple ML Models | ✅ Complete |
| RMSE, MAE, R² Evaluation | ✅ Complete |
| Automated CI/CD Pipeline | ✅ Complete |
| Web Dashboard | ✅ Complete |
| Feature Store (MongoDB) | ✅ Complete |
| SHAP Explainability | ✅ Complete |
| AQI Alerts | ✅ Complete |
| Multiple Forecasting Models | ✅ Complete |
| TensorFlow/Deep Learning | ✅ Complete |
| FastAPI | ✅ Complete |
| Streamlit | ✅ Complete |
| GitHub Actions | ✅ Complete |
| Cloud Deployment | ✅ Complete |

---

## City Information

**Sukkur, Sindh, Pakistan**
- Coordinates: 27.7052°N, 68.8574°E
- Climate: Hot desert (BWh)
- Average summer temperature: 40-48°C
- Main pollution source: Dust and particulate matter
- AQI typically ranges 80-120 in summer months

---

## Author

Developed as part of 10Pearls internship capstone project.

---

## Data Sources Credits

- [Open-Meteo](https://open-meteo.com/) — Free weather and air quality API
- [OpenWeather](https://openweathermap.org/) — Weather forecast API
- [MongoDB Atlas](https://www.mongodb.com/atlas) — Cloud database
