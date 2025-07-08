# /app/api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy import text
import joblib
import datetime
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import os

DB_URL = "postgresql+psycopg2://postgres:password@db:5432/dividends"
engine = sqlalchemy.create_engine(DB_URL)

app = FastAPI(title="Dividend ML API")

try:
    model = joblib.load("model.joblib")
    model_info = {"trained": True, "model_type": "LinearRegression"}
except:
    model = None
    model_info = {"trained": False}

def get_model_last_modified():
    if os.path.exists("model.joblib"):
        return datetime.datetime.fromtimestamp(os.path.getmtime("model.joblib")).isoformat()
    return None

class InputData(BaseModel):
    open: float
    high: float
    low: float
    volume: float
    dividends: float
    earnings: float

class Company(BaseModel):
    ticker: str
    name: str

@app.post("/predict")
def predict(data: InputData):
    if not model:
        raise HTTPException(status_code=400, detail="Model not trained yet.")
    X = np.array([[data.open, data.high, data.low, data.volume, data.dividends, data.earnings]])
    prediction = model.predict(X)
    return {"predicted_close": prediction[0]}

@app.get("/train")
def train():
    df = pd.read_sql("SELECT open, high, low, volume, dividends, earnings, close FROM fundamentals", engine)
    if df.empty:
        raise HTTPException(status_code=400, detail="No data to train on.")
    X, y = df[['open','high','low','volume','dividends','earnings']], df['close']
    global model
    model = LinearRegression()
    model.fit(X, y)
    joblib.dump(model, "model.joblib")
    global model_info
    model_info.update({"trained": True})
    return {"status": "trained", "rows": len(df)}

@app.get("/metrics")
def metrics():
    if not model:
        raise HTTPException(status_code=400, detail="Model not trained yet.")
    df = pd.read_sql("SELECT open, high, low, volume, dividends, earnings, close FROM fundamentals", engine)
    if len(df) < 2:
        raise HTTPException(status_code=400, detail="Not enough data")
    X, y = df[['open','high','low','volume','dividends','earnings']], df['close']
    preds = model.predict(X)
    mse, r2 = mean_squared_error(y, preds), r2_score(y, preds)
    return {"mse": mse, "r2": r2}

@app.get("/health")
def health():
    return {"status": "ok", "model_info": model_info, "last_trained": get_model_last_modified()}

@app.post("/companies/add")
def add_company(company: Company):
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO companies (ticker, name) VALUES (:ticker, :name)"),
                     {"ticker": company.ticker.upper(), "name": company.name})
    return {"status": "ok", "message": f"Added {company.ticker.upper()}"}

@app.get("/companies/list")
def list_companies():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT ticker, name FROM companies"))
        return {"companies": [{"ticker": r[0], "name": r[1]} for r in res]}

@app.get("/fundamental/data")
def data():
    df = pd.read_sql("SELECT * FROM fundamentals ORDER BY date DESC LIMIT 10", engine)
    return df.to_dict(orient="records")
