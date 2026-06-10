# Pearls AQI Predictor

A complete end-to-end machine learning pipeline for predicting Air Quality Index (AQI) in Sukkur, Sindh, Pakistan for the next 3 days using a 100% serverless stack.

---

## Live Demo

| Service | URL |
|---|---|
| React Frontend | https://10pearls-aqi-predictor.vercel.app/ |
| FastAPI Backend | https://pearls-aqi.onrender.com |
| API Documentation | https://pearls-aqi.onrender.com/docs |
| Streamlit Dashboard | https://10pearls-aqi-predictor-9ja3gnjph6biv392fykzwy.streamlit.app |

---

## Project Overview

This project predicts AQI using real-time weather and pollution data. It includes automated data collection, feature engineering, model training, and real-time predictions through a React web dashboard and REST API. The system runs completely automatically using GitHub Actions for CI/CD.

---

## Technology Stack

| Category | Technology |
|---|---|
| Language | Python 3.11+ |
| Frontend | React + Vite + Recharts |
| Data APIs | Open-Meteo (historical AQI), OpenWeather (live + forecast) |
| Database | MongoDB Atlas (Feature Store) |
| ML Models | Gradient Boosting, Random Forest, Ridge Regression, LSTM, DNN |
| Explainability | SHAP |
| Backend API | FastAPI |
| Dashboard | Streamlit (reference) |
| CI/CD | GitHub Actions |
| Deployment | Vercel (frontend), Render (API) |

---

## Project Structure

```
pearls-aqi-predictor/
│
├── .github/
│   └── workflows/
│       ├── feature_pipeline.yml     # runs every hour
│       └── training_pipeline.yml    # runs every day
│
├── api/
│   ├── main.py                      # FastAPI endpoints
│   ├── requirements.txt             # API dependencies
│   ├── runtime.txt                  # Python 3.11
│   └── Procfile                     # Render start command
│
├── dashboard/
│   └── streamlit_app.py             # Streamlit dashboard (reference)
│
├── data_fetch/
│   ├── fetch_historical.py          # fetch 3 months historical data
│   └── merge_historical.py          # merge AQI + weather data
│
├── feature_pipeline/
│   ├── feature_engineering.py       # engineer 23 features
│   └── run_pipeline.py              # hourly CI/CD pipeline
│
├── models/
│   ├── gradient_boosting.pkl        # primary model
│   ├── random_forest.pkl            # secondary model
│   ├── ridge.pkl                    # secondary model
│   ├── scaler.pkl
│   └── label_encoder.pkl
│
├── pearls-aqi-frontend/             # React frontend
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx        # current AQI + 3-day forecast
│   │   │   ├── History.jsx          # 3-month historical charts
│   │   │   ├── Analysis.jsx         # SHAP + model metrics
│   │   │   └── Alerts.jsx           # health warnings
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── Card.jsx
│   │   │   ├── Loading.jsx
│   │   │   └── SectionTitle.jsx
│   │   ├── api.js                   # API calls to FastAPI
│   │   └── utils.js                 # AQI helpers
│   └── package.json
│
├── training_pipeline/
│   ├── 01_train_models.ipynb        # train all models
│   ├── 02_shap_analysis.ipynb       # SHAP feature importance
│   ├── 03_forecast.ipynb            # 3-day forecast
│   └── run_training.py              # daily CI/CD training
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
   ┌────────┴────────┐
   │                 │
Model Training    3-Day Forecast
(Gradient Boosting, (Recursive
 Random Forest,      Prediction)
 Ridge, LSTM, DNN)       │
        │                │
   Models saved     FastAPI Backend
   (.pkl files)       (Render)
        │                │
 GitHub Actions    React Frontend
 (Hourly + Daily)    (Vercel)
```

---

## Data Sources

| Source | Type | Coverage |
|---|---|---|
| Open-Meteo Air Quality | Historical AQI, PM2.5, PM10, NO2, CO, O3 | Last 3 months |
| Open-Meteo Archive | Historical temperature, humidity, wind | Last 3 months |
| OpenWeather Current | Live weather data | Real-time |
| OpenWeather Forecast | 5-day weather forecast | Next 3 days |

**Note:** All AQI values use the European AQI scale (0-500+) from Open-Meteo, not the OpenWeather 1-5 scale.

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

**Total: 23 features, 2160+ hourly records**

---

## Model Performance

| Model | R² Score | RMSE | MAE | Verdict | Status |
|---|---|---|---|---|---|
| Gradient Boosting | 0.9917 | 1.2187 | 0.3714 | No overfitting | Primary |
| Random Forest | 0.9846 | 1.6580 | 0.5181 | No overfitting | Secondary |
| Ridge Regression | 0.8862 | 4.5046 | 2.5873 | No overfitting | Secondary |
| Lasso | 0.8833 | 4.5620 | 2.5094 | No overfitting | Trained |
| ElasticNet | 0.8789 | 4.6471 | 2.6446 | No overfitting | Trained |
| LSTM | -24.49 | 67.358 | 61.343 | Overfitting | Experimental |

**Primary model: Gradient Boosting**

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

## React Frontend Pages

**Dashboard (/)**
- Current AQI card with temperature, humidity, wind
- Model selector (Gradient Boosting, Random Forest, Ridge)
- 3-day forecast cards
- 72-hour AQI trend line chart

**History (/history)**
- Stats row (average, max, min, total records)
- Daily average AQI trend chart
- Temperature trend chart
- PM10 and PM2.5 trend chart
- Monthly average AQI bar chart

**Analysis (/analysis)**
- SHAP feature importance chart
- Current pollutant levels bar chart
- All model performance metrics table

**Alerts (/alerts)**
- Health warning based on 3-day forecast
- Recommendations by AQI level
- European AQI scale reference table

---

## FastAPI Endpoints

| Endpoint | Method | Description |
|---|---|---|
| / | GET | Project info and available endpoints |
| /health | GET | Health check |
| /current | GET | Current AQI and weather (European scale) |
| /forecast | GET | 3-day forecast using Gradient Boosting |
| /forecast/{model} | GET | 3-day forecast using selected model |
| /historical | GET | Historical data from MongoDB |
| /models | GET | Available models and metrics |

**Available model names:** `gradient_boosting`, `random_forest`, `ridge`

**Live API Docs:** https://pearls-aqi.onrender.com/docs

---

## CI/CD Pipeline

```
Every Hour (GitHub Actions):
→ Fetch Open-Meteo European AQI for Sukkur
→ Compute lag features from MongoDB history
→ Save new record to MongoDB

Every Day (GitHub Actions):
→ Fetch all features from MongoDB
→ Retrain Ridge model
→ Save updated metrics to MongoDB

React Frontend:
→ Calls FastAPI endpoints in real-time
→ Always shows latest data from MongoDB
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

### 3. Install Python dependencies
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

Open and run all cells in order:

```
training_pipeline/01_train_models.ipynb
training_pipeline/02_shap_analysis.ipynb
training_pipeline/03_forecast.ipynb
```

### 8. Run FastAPI locally
```bash
cd ../api
uvicorn main:app --reload
```

### 9. Run React frontend locally
```bash
cd ../pearls-aqi-frontend
npm install
npm run dev
```

### 10. Run Streamlit dashboard (optional reference)
```bash
cd ../dashboard
streamlit run streamlit_app.py
```

---

## Deployment

### React Frontend (Vercel)
1. Push code to GitHub
2. Go to vercel.com → New Project
3. Select repo
4. Set Root Directory: `pearls-aqi-frontend`
5. Framework: Vite
6. Click Deploy

### FastAPI Backend (Render)
1. Go to render.com → New Web Service
2. Select repo
3. Set Root Directory: `api`
4. Runtime: Python 3.11
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. Add environment variables
8. Click Deploy

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

Top 5 most important features:

| Rank | Feature | Importance |
|---|---|---|
| 1 | aqi_lag_1 | 9.03 |
| 2 | aqi_change_rate | 0.75 |
| 3 | aqi_lag_3 | 0.50 |
| 4 | aqi_rolling_mean_24 | 0.08 |
| 5 | aqi_lag_24 | 0.02 |

**Key insight:** Previous hour's AQI is the strongest predictor. Sukkur's air quality follows strong temporal patterns driven by dust and particulate matter. Weather features have minimal impact confirming dust as the primary pollution source.

---

## Project Requirements Fulfilled

| Requirement | Status |
|---|---|
| Feature Pipeline | Complete |
| Historical Data Backfill (3 months) | Complete |
| Training Pipeline | Complete |
| Multiple ML Models | Complete |
| RMSE, MAE, R² Evaluation | Complete |
| Automated CI/CD Pipeline | Complete |
| Web Dashboard (React + Streamlit) | Complete |
| Feature Store (MongoDB) | Complete |
| SHAP Explainability | Complete |
| AQI Alerts | Complete |
| Multiple Forecasting Models | Complete |
| TensorFlow/Deep Learning | Complete |
| FastAPI | Complete |
| GitHub Actions | Complete |
| Cloud Deployment (Vercel + Render) | Complete |

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

- [Open-Meteo](https://open-meteo.com/) — Free weather and air quality API (no API key required)
- [OpenWeather](https://openweathermap.org/) — Weather forecast API
- [MongoDB Atlas](https://www.mongodb.com/atlas) — Cloud database (Feature Store)
