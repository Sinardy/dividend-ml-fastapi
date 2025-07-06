import datetime
import pandas as pd
import sqlalchemy
from sqlalchemy import text
import yfinance as yf

# ============================
# 🚀 Database connection
# ============================
DB_URL = "postgresql://postgres:password@db:5432/dividends"
engine = sqlalchemy.create_engine(DB_URL)

# ============================
# 📌 Load tickers from companies table
# ============================
with engine.connect() as conn:
    result = conn.execute(text("SELECT ticker FROM companies"))
    tickers = [row[0] for row in result.fetchall()]

if not tickers:
    print("⚠️ No companies found in DB. Please add them via the /companies endpoint.")
    exit()

print(f"✅ Found tickers in DB: {tickers}")

# ============================
# 📅 Find latest date in fundamentals
# ============================
latest_date_query = text("SELECT MAX(date) FROM fundamentals;")

with engine.connect() as conn:
    result = conn.execute(latest_date_query).fetchone()

latest_date = result[0]
print(f"✅ Latest date in fundamentals: {latest_date}")

# ============================
# 🗓 Decide start date
# ============================
if latest_date is None:
    start_date = "2010-01-01"
else:
    start_date = (latest_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

end_date = datetime.datetime.today().strftime("%Y-%m-%d")
print(f"📈 Fetching data from {start_date} to {end_date}")

# ============================
# ⏬ Fetch + load loop
# ============================
rows_added = 0

for ticker in tickers:
    print(f"\n🔍 Downloading {ticker}...")
    try:
        df = yf.download(ticker, start=start_date, end=end_date, interval="3mo")
    except Exception as e:
        print(f"❌ Failed to download data for {ticker}: {e}")
        continue

    if df.empty:
        print(f"⚠️ No new data for {ticker}")
        continue

    # Prepare dataframe
    df.reset_index(inplace=True)
    df['ticker'] = ticker
    df['period'] = df['Date'].dt.to_period('Q').astype(str)
    df.rename(columns={
        "Date": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume"
    }, inplace=True)

    # Add dummy columns for dividends & earnings if needed
    df['dividends'] = 0
    df['earnings'] = 1

    # Keep consistent schema
    db_df = df[['ticker', 'period', 'date', 'open', 'high', 'low', 'close', 'volume', 'dividends', 'earnings']]

    # Insert into DB
    try:
        db_df.to_sql("fundamentals", engine, if_exists="append", index=False)
        print(f"✅ Loaded {len(db_df)} rows for {ticker}")
        rows_added += len(db_df)
    except Exception as e:
        print(f"❌ Failed to insert data for {ticker}: {e}")

# ============================
# 🎉 Summary
# ============================
print(f"\n🎯 Finished. Total new rows added: {rows_added}")
