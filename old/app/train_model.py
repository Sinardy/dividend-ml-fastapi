import pandas as pd
from sqlalchemy import create_engine
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
import json
from datetime import datetime

# Load database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:password@db:5432/dividends")
engine = create_engine(DATABASE_URL)

# Read data from DB
df = pd.read_sql("SELECT open, high, low, volume, dividends, earnings, close FROM fundamentals", engine)

if df.empty:
    print("⚠️ No data found in the database to train on. Skipping training.")
    # Write metadata anyway for /health endpoint
    model_info = {
        "model_type": "LinearRegression",
        "features_count": 6,
        "trained": False,
        "last_trained": str(datetime.utcnow())
    }
    with open("model_info.json", "w") as f:
        json.dump(model_info, f)
    exit(0)

print("✅ Loaded data from DB:")
print(df.head())

X = df[["open", "high", "low", "volume", "dividends", "earnings"]]
y = df["close"]

# Fit the model
model = LinearRegression()
model.fit(X, y)

# Evaluate
predictions = model.predict(X)
mse = mean_squared_error(y, predictions)
r2 = r2_score(y, predictions)

print(f"📈 Training completed: MSE={mse:.4f}, R²={r2:.4f}")

# Save model
joblib.dump(model, "model.joblib")

# Save metadata
model_info = {
    "model_type": "LinearRegression",
    "features_count": X.shape[1],
    "trained": True,
    "last_trained": str(datetime.utcnow()),
    "mse": mse,
    "r2": r2
}
with open("model_info.json", "w") as f:
    json.dump(model_info, f)

print("✅ Model saved to model.joblib and metadata saved to model_info.json")
