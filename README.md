
# 📈 Dividend ML Prediction API

A production-style Python microservice that predicts stock closing prices based on historical and fundamental data, built for learning and demonstration purposes.

---

## 🚀 Tech Stack

- **FastAPI** — high-performance Python web framework for building REST APIs.
- **PostgreSQL** — relational database to store historical stock data and tracked tickers.
- **SQLAlchemy** — ORM for Python to interact with the database.
- **yfinance** — retrieves historical stock data from Yahoo Finance.
- **scikit-learn** — trains and serializes a linear regression model.
- **Docker & Docker Compose** — container orchestration for a reproducible, isolated environment.

---

## ⚙️ Getting Started

### Prerequisites
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- `curl` or Postman for testing endpoints.

### Running the full stack
```bash
docker compose up --build
```

This will:

- 🚀 **Start PostgreSQL** with initialized tables for `fundamentals` and `companies`.
- ⚡ **Start FastAPI** with endpoints to train, predict, fetch metrics, and manage data.

---

## 🧩 API Endpoints

| Method | Endpoint              | Description                                    |
|--------|------------------------|-----------------------------------------------|
| `POST` | `/predict`             | Predicts next close price given input features |
| `POST` | `/train`               | Retrains the model on latest database data    |
| `GET`  | `/metrics`             | Returns MSE and R² of the current model       |
| `GET`  | `/health`              | Shows model metadata & last training time     |
| `GET`  | `/data`                | Shows latest rows from fundamentals table    |
| `GET`  | `/companies/list`      | Lists all tracked tickers                     |
| `POST` | `/companies/add`       | Adds a new ticker to track (`{"ticker":"AAPL"}`) |

---

## 🔍 Quick Usage Examples

### Predict
```bash
curl -X POST "http://localhost:8000/predict" \
-H "Content-Type: application/json" \
-d '{"open":172,"high":180,"low":170,"volume":110000,"dividends":0.23,"earnings":1.28}'
```

### Add a company
```bash
curl -X POST "http://localhost:8000/companies/add" \
-H "Content-Type: application/json" \
-d '{"ticker":"AAPL"}'
```

### Check metrics
```bash
curl http://localhost:8000/metrics
```

---

## 🚀 Reset the database
```bash
bash ./reset_db.sh
```
This will drop and recreate all tables using the `reset.sql` script mounted into your Docker database container.

---

## 📄 License

MIT — use this project to learn, adapt, and explore machine learning pipelines with FastAPI and Docker.

