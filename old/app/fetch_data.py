import os
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError, ProgrammingError
import logging
import datetime

# --------------------------------------
# Configure logging
# --------------------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --------------------------------------
# Database connection
# --------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:password@db:5432/dividends")
engine = create_engine(DATABASE_URL)

# --------------------------------------
# Helper functions
# --------------------------------------
def get_companies():
    """Fetch ticker symbols from companies table."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT ticker FROM companies"))
            tickers = [row[0] for row in result]
        logging.info(f"✅ Fetched {len(tickers)} companies from DB.")
        return tickers
    except Exception as e:
        logging.error(f"❌ Failed to fetch companies: {e}")
        return []

def get_existing_records():
    """Fetch existing (ticker, date) keys to prevent duplicate inserts."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT ticker, date FROM fundamentals"))
            existing = {(row[0], row[1].date() if isinstance(row[1], datetime.datetime) else row[1]) for row in result}
        logging.info(f"✅ Loaded {len(existing)} existing records.")
        return existing
    except Exception as e:
        logging.error(f"❌ Failed to fetch existing records: {e}")
        return set()

# --------------------------------------
# Main processing
# --------------------------------------
def fetch_and_insert():
    tickers = get_companies()
    if not tickers:
        logging.warning("No tickers found. Exiting.")
        return

    existing_records = get_existing_records()

    for ticker in tickers:
        logging.info(f"📈 Downloading data for {ticker}")
        try:
            data = yf.download(ticker, start="2010-01-01", interval="3mo", auto_adjust=True)

            if data.empty:
                logging.warning(f"⚠️ No data found for {ticker}")
                continue

            # Flatten MultiIndex columns if necessary
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = [col[0] for col in data.columns]

            data.reset_index(inplace=True)
            data.rename(columns={
                "Date": "date", "Open": "open", "High": "high",
                "Low": "low", "Close": "close", "Volume": "volume"
            }, inplace=True)
            data['ticker'] = ticker
            data['date'] = pd.to_datetime(data['date']).dt.date

            # Calculate period
            data['period'] = data['date'].apply(lambda d: f"{d.year}Q{(d.month - 1)//3 + 1}")
            data['dividends'] = 0.0
            data['earnings'] = 1.0

            # Insert into DB if not exists
            inserted, skipped = 0, 0
            with engine.begin() as conn:
                for _, row in data.iterrows():
                    key = (ticker, row['date'])
                    if key in existing_records:
                        skipped += 1
                        continue
                    conn.execute(text("""
                        INSERT INTO fundamentals 
                        (ticker, period, date, open, high, low, close, volume, dividends, earnings)
                        VALUES (:ticker, :period, :date, :open, :high, :low, :close, :volume, :dividends, :earnings)
                    """), {
                        "ticker": ticker,
                        "period": row['period'],
                        "date": row['date'],
                        "open": float(row['open']),
                        "high": float(row['high']),
                        "low": float(row['low']),
                        "close": float(row['close']),
                        "volume": int(row['volume']),
                        "dividends": float(row['dividends']),
                        "earnings": float(row['earnings'])
                    })
                    existing_records.add(key)
                    inserted += 1

            logging.info(f"📊 {ticker}: Inserted {inserted} new, skipped {skipped} existing.")
        
        except Exception as e:
            logging.error(f"❌ Error processing {ticker}: {e}")

if __name__ == "__main__":
    fetch_and_insert()
