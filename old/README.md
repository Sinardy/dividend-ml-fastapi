
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

## 📂 Project Structure

```
.
├── app
│   ├── app.py            # FastAPI application
│   ├── fetch_data.py     # Fetches Yahoo Finance data, inserts into DB
│   ├── train_model.py    # Trains sklearn LinearRegression model
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile        # API container
├── db
│   ├── init.sql          # DB schema initialization
│   ├── reset.sql         # Manual reset script
│   └── reset_db.sh       # Helper shell script to reset
├── docker-compose.yml    # Compose file for API & Postgres
├── project.sh            # Helper script to restart, rebuild, fetch, train, add companies
├── README.md             # This file
└── LEARNING.md           # Notes for personal study
```

---

## ⚙️ Getting Started

### Prerequisites

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- `curl` or Postman for testing endpoints.

---

### 🚀 Running the full stack

```bash
docker compose up -d --build
```

This will:

- 🚀 **Start PostgreSQL** with initialized tables for `fundamentals` and `companies`.
- ⚡ **Start FastAPI** with endpoints to train, predict, fetch metrics, and manage data.

---

## 🛠 Helper script

For convenience, use `project.sh`:

```bash
./project.sh restart                       # Restart containers
./project.sh rebuild                       # Rebuild containers
./project.sh fetch                         # Fetch stock data from Yahoo Finance
./project.sh train                         # Train ML model
./project.sh reset_db                      # Reset database tables
./project.sh add_company AAPL "Apple Inc." # Insert company via API
```

---

## 🧩 API Endpoints

| Method   | Endpoint                       | Description                                     |
|----------|--------------------------------|-------------------------------------------------|
| `POST`   | `/predict`                     | Predicts next close price given input features  |
| `GET`    | `/train`                       | Retrains the model on latest database data      |
| `GET`    | `/metrics`                     | Returns MSE and R² of the current model         |
| `GET`    | `/health`                      | Shows model metadata & last training time       |
| `GET`    | `/fundamental/data`            | Shows latest rows from fundamentals table      |
| `GET`    | `/companies/list`              | Lists all tracked tickers                       |
| `POST`   | `/companies/add`               | Adds a new ticker & name to track               |
| `DELETE` | `/companies/delete/{ticker}`   | Removes a tracked company by ticker             |

---

## 🔍 Quick Usage Examples

### Predict

```bash
curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" -d '{"open":172,"high":180,"low":170,"volume":110000,"dividends":0.23,"earnings":1.28}'
```

### Add a company

```bash
curl -X POST "http://localhost:8000/companies/add" -H "Content-Type: application/json" -d '{"ticker":"AAPL", "name":"Apple Inc."}'
```

### Check metrics

```bash
curl http://localhost:8000/metrics
```

---

## 🚀 Reset the database

```bash
bash ./db/reset_db.sh
```

This will drop and recreate all tables using `reset.sql` in your Docker database container.

---

## 📄 License

MIT — use this project to learn, adapt, and explore machine learning pipelines with FastAPI and Docker.
