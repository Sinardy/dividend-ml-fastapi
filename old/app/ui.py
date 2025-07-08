# /app/ui.py
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import requests

app = FastAPI(title="Dividend ML UI")
templates = Jinja2Templates(directory="templates")

API_BASE = "http://api:8000"

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/predict")
def predict_form(request: Request):
    return templates.TemplateResponse("predict.html", {"request": request})

@app.post("/predict")
def do_predict(request: Request, open: float = Form(...), high: float = Form(...),
               low: float = Form(...), volume: float = Form(...),
               dividends: float = Form(...), earnings: float = Form(...)):
    resp = requests.post(f"{API_BASE}/predict", json={
        "open": open, "high": high, "low": low,
        "volume": volume, "dividends": dividends, "earnings": earnings
    })
    pred = resp.json()
    return templates.TemplateResponse("predict.html", {"request": request, "prediction": pred})

@app.get("/metrics")
def metrics(request: Request):
    resp = requests.get(f"{API_BASE}/metrics")
    data = resp.json()
    return templates.TemplateResponse("metrics.html", {"request": request, "metrics": data})

@app.get("/companies")
def companies(request: Request):
    resp = requests.get(f"{API_BASE}/companies/list")
    data = resp.json()
    return templates.TemplateResponse("companies.html", {"request": request, "companies": data["companies"]})

@app.post("/companies")
def add_company(request: Request, ticker: str = Form(...), name: str = Form(...)):
    requests.post(f"{API_BASE}/companies/add", json={"ticker": ticker, "name": name})
    return RedirectResponse(url="/companies", status_code=303)

