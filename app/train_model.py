# train_model.py
import pandas as pd
import sqlalchemy
from sklearn.linear_model import LinearRegression
import joblib

# connection string for SQLAlchemy
engine = sqlalchemy.create_engine("postgresql://postgres:password@db:5432/dividends")

# Load data into a DataFrame
df = pd.read_sql("SELECT * FROM fundamentals", engine)
print(df.head())

# Features and target
X = df[["open", "high", "low", "volume", "dividends", "earnings"]]
y = df["close"]

# Initialize and train the model
model = LinearRegression()
model.fit(X, y)

# Save the trained model to a file
joblib.dump(model, "model.joblib")
print("Model saved to model.joblib")
