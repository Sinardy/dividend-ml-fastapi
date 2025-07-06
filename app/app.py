from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import os
import datetime
import pandas as pd
import sqlalchemy
from sqlalchemy import text
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Database connection string
DB_URL = "postgresql://postgres:password@db:5432/dividends"
engine = sqlalchemy.create_engine(DB_URL)

app = FastAPI()

# Load model if exists
try:
    model = joblib.load("model.joblib")
    model_info = {
        "model_type": "LinearRegression",
        "trained": True,
        "features_count": 6
    }
except:
    model = None
    model_info = {
        "trained": False
    }

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
    company_name: str

@app.post("/predict")
def predict(data: InputData):
    if not model:
        raise HTTPException(status_code=400, detail="Model not trained yet.")
    X = np.array([[data.open, data.high, data.low, data.volume, data.dividends, data.earnings]])
    prediction = model.predict(X)
    return {"predicted_close": prediction[0]}

@app.get("/train")
def train():
    query = "SELECT open, high, low, volume, dividends, earnings, close FROM fundamentals"
    df = pd.read_sql(query, engine)

    if df.empty:
        raise HTTPException(status_code=400, detail="No data to train on.")

    X = df[['open', 'high', 'low', 'volume', 'dividends', 'earnings']]
    y = df['close']

    global model
    model = LinearRegression()
    model.fit(X, y)
    joblib.dump(model, "model.joblib")

    global model_info
    model_info = {
        "model_type": "LinearRegression",
        "features_count": X.shape[1],
        "trained": True
    }

    return {"status": "trained", "rows_used": len(df), "features": X.columns.tolist()}

@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_info": model_info,
        "model_last_modified": get_model_last_modified()
    }

@app.get("/metrics")
def metrics():
    query = "SELECT open, high, low, volume, dividends, earnings, close FROM fundamentals"
    df = pd.read_sql(query, engine)

    if df.empty or len(df) < 2:
        raise HTTPException(status_code=400, detail="Not enough data to compute metrics.")

    X = df[['open', 'high', 'low', 'volume', 'dividends', 'earnings']]
    y = df['close']

    preds = model.predict(X)
    mse = mean_squared_error(y, preds)
    r2 = r2_score(y, preds)

    interpretation = ""
    if r2 >= 0.95:
        interpretation = "⚠️ R² very close to 1.0 — might indicate overfitting."
    elif r2 < 0.5:
        interpretation = "⚠️ R² below 0.5 — model may not be explaining data well."
    else:
        interpretation = "✅ R² in reasonable range."

    return {
        "mse": mse,
        "r2": r2,
        "interpretation": interpretation
    }

@app.get("/data")
def get_data():
    query = "SELECT * FROM fundamentals ORDER BY date DESC LIMIT 10"
    df = pd.read_sql(query, engine)
    return df.to_dict(orient="records")

@app.post("/companies")
def add_company(company: Company):
    with engine.connect() as conn:
        try:
            conn.execute(
                text("INSERT INTO companies (ticker, company_name) VALUES (:ticker, :company_name)"),
                {"ticker": company.ticker.upper(), "company_name": company.company_name}
            )
            return {"status": "ok", "message": f"{company.ticker.upper()} added."}
        except Exception as e:
            if "duplicate key" in str(e) or "unique constraint" in str(e):
                return {"status": "duplicate", "message": f"Ticker {company.ticker.upper()} already exists."}
            raise HTTPException(status_code=400, detail=f"Insert failed: {e}")

@app.get("/companies/list")
def list_companies():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT ticker, company_name FROM companies"))
        companies = [{"ticker": row[0], "company_name": row[1]} for row in result.fetchall()]
    return {"companies": companies}

@app.delete("/delete_company/{ticker}")
def delete_company(ticker: str):
    with engine.connect() as conn:
        result = conn.execute(text("DELETE FROM companies WHERE ticker = :ticker"), {"ticker": ticker.upper()})
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Ticker {ticker.upper()} not found.")
    return {"status": "ok", "message": f"Deleted {ticker.upper()}"}
