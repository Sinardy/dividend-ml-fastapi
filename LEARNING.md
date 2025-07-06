
# 📚 Personal Learning Notes - Dividend ML API Project

This document captures personal insights and learning milestones from building this project.

---

## 🚀 What I Learned

### 🐳 Docker & Docker Compose
- How to create isolated environments for Python, FastAPI, and PostgreSQL.
- How to persist data using Docker volumes.
- How to mount SQL init scripts into PostgreSQL.

### ⚡ FastAPI
- Building professional REST APIs with data validation via Pydantic.
- Structuring endpoints for `/predict`, `/train`, `/metrics`, `/health`, and dynamic `/companies` management.
- Handling JSON requests and responses cleanly.

### 🐘 PostgreSQL & SQLAlchemy
- Designing tables for `fundamentals` and `companies`.
- Using SQLAlchemy for querying and inserting data.
- Ensuring idempotent inserts and avoiding duplicates with primary keys.

### 📈 Machine Learning
- Building a **LinearRegression** model using scikit-learn.
- Saving and loading models with `joblib`.
- Calculating MSE and R² to evaluate performance.

### 🔄 Data Fetching
- Using `yfinance` to pull historical EOD (end-of-day) data.
- Appending only new (delta) data since the last date in the DB.

### 🛠️ General DevOps
- Writing `reset_db.sh` to easily drop & recreate tables.
- Using `docker exec` to run SQL scripts directly inside containers.

### 🔑 GitHub & SSH
- Setting up passwordless SSH with `ssh-keygen` and `ssh-add`.
- Configuring GitHub for SSH instead of HTTPS for smooth pushes.

---

## 💡 Reflections
- Keeping everything modular and using Docker made testing and cleaning up extremely easy.
- Adding `/metrics` that describes if R² is too close to 1.0 (possible overfit) helped me interpret models.
- Using `/health` to show `last_modified` made debugging and tracking trainings clear.

---

## 📝 Future Ideas
- Swap out LinearRegression for RandomForest or XGBoost.
- Set up cron jobs (or FastAPI background tasks) to auto-train daily on new data.
- Build a simple front-end dashboard with React or Streamlit.

---

## ✅ Done
- FastAPI app with multiple endpoints.
- Data stored in PostgreSQL with dockerized volume.
- Daily incremental data loader.
- Clean GitHub repo with README and documentation.

---

_This file serves as a personal developer log to refer back to for future machine learning pipeline builds._

