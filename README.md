
# 📈 Dividend ML Project

A containerized machine learning stack with:
- FastAPI backend (API)
- FastAPI-based UI (frontend)
- PostgreSQL database

## 🚀 How to run

1. Clone or unzip this project.
2. Make sure Docker & Docker Compose are installed.
3. Run:
```bash
docker compose up --build
```

- API available on: http://localhost:8000
- UI available on: http://localhost:8001

## 🔍 Endpoints

| Method | Endpoint              | Description |
|--------|------------------------|-------------|
| POST   | /predict               | Predict next close |
| GET    | /train                 | Retrain the model |
| GET    | /metrics               | MSE and R² |
| GET    | /health                | Check API & model |
| GET    | /companies/list        | List companies |
| POST   | /companies/add         | Add company |
| GET    | /fundamental/data      | Recent fundamentals |

## 🧑‍💻 Developer quick start

- Modify `app/api.py` to adjust data processing or ML logic.
- Modify `app/ui.py` and `templates/` to change UI.
- DB schema: `db/init.sql`.
