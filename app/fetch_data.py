import os
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError, ProgrammingError
import logging
import datetime # Import datetime module

# Configure logging to DEBUG level for more detailed output
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Explicitly use the psycopg2 driver with 'postgresql+psycopg2://'
# This ensures SQLAlchemy knows which driver to use.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:password@db:5432/dividends")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

def get_companies():
    """Fetch ticker symbols from companies table."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT ticker FROM companies"))
            tickers = [row[0] for row in result]
        logging.info(f"Fetched {len(tickers)} companies from DB.")
        return tickers
    except Exception as e:
        logging.error(f"Failed to fetch companies from DB: {e}")
        return []

def get_existing_records():
    """
    Fetch existing (ticker, date) tuples from fundamentals table
    to avoid duplicates based on the PRIMARY KEY (ticker, date).
    """
    try:
        with engine.connect() as conn:
            # IMPORTANT: Fetch 'ticker' and 'date' to match the database's PRIMARY KEY
            result = conn.execute(text("SELECT ticker, date FROM fundamentals"))
            existing = set()
            for row in result.fetchall():
                ticker_val = row[0]
                date_val = row[1]
                # Ensure date_val is a datetime.date object for consistent hashing
                if isinstance(date_val, datetime.datetime):
                    date_val = date_val.date() # Convert datetime.datetime to datetime.date
                elif not isinstance(date_val, datetime.date):
                    logging.warning(f"Unexpected type for date in existing records: {type(date_val)}. Attempting conversion.")
                    try:
                        date_val = pd.to_datetime(date_val).date()
                    except Exception as conv_e:
                        logging.error(f"Failed to convert existing date value {date_val}: {conv_e}. Skipping this record.")
                        continue # Skip this problematic record

                existing.add((ticker_val, date_val))

        logging.info(f"Fetched {len(existing)} existing fundamental records based on (ticker, date).")
        logging.debug(f"Sample of existing_records: {list(existing)[:5]}") # Print first 5 for debug
        return existing
    except Exception as e:
        logging.error(f"Failed to fetch existing records from DB: {e}")
        return set()

def fetch_and_insert():
    tickers = get_companies()
    if not tickers:
        logging.warning("No tickers found to process. Exiting.")
        return

    existing_records = get_existing_records()

    for ticker in tickers:
        logging.info(f"📈 Fetching data for {ticker}")
        try:
            # Download quarterly data starting 2010-01-01
            data = yf.download(ticker, start="2010-01-01", interval="3mo", auto_adjust=True)

            if data.empty:
                logging.warning(f"⚠️ No data found for {ticker}")
                continue

            logging.info(f"✅ Downloaded {len(data)} records for {ticker}.")
            logging.debug(f"Original DataFrame head for {ticker}:\n{data.head()}")
            logging.debug(f"Original DataFrame info for {ticker}:\n{data.info()}")
            logging.debug(f"Original DataFrame columns for {ticker}: {data.columns}") # Added for debugging MultiIndex


            # --- MODIFIED: Flatten MultiIndex columns more robustly if present ---
            if isinstance(data.columns, pd.MultiIndex):
                logging.debug(f"DataFrame has MultiIndex columns. Original columns: {data.columns.tolist()}")
                # Extract the first level of the MultiIndex (e.g., 'Open', 'High')
                # This handles cases like ('Open', 'AAPL') -> 'Open'
                new_columns = [col[0] if isinstance(col, tuple) else col for col in data.columns.values]
                data.columns = new_columns
                logging.debug(f"Columns after flattening MultiIndex: {data.columns.tolist()}")

                # If 'Adj Close' is present, we should prefer it over 'Close' if auto_adjust=True
                if 'Adj Close' in data.columns and 'Close' in data.columns:
                    data.rename(columns={'Adj Close': 'Close'}, inplace=True)
                    logging.debug("Renamed 'Adj Close' to 'Close' after flattening.")
            else:
                logging.debug("DataFrame does not have MultiIndex columns.")


            # Rename index and columns to match DB schema
            data.reset_index(inplace=True)
            data.rename(columns={
                "Date": "date",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close", # This will now refer to the adjusted close if present
                "Volume": "volume"
            }, inplace=True)
            logging.debug(f"DataFrame columns after rename: {data.columns.tolist()}")

            # Add the ticker as a new column to the DataFrame
            data['ticker'] = ticker
            logging.debug(f"DataFrame columns after adding ticker: {data.columns.tolist()}")

            # Convert 'date' column to Python's datetime.date objects for SQL compatibility
            # This is crucial to avoid potential 'Series' type issues or driver mismatches.
            logging.debug(f"Before date conversion. First date value: {data['date'].iloc[0]}, Type: {type(data['date'].iloc[0])}")
            data['date'] = pd.to_datetime(data['date']).dt.date
            logging.debug(f"After date conversion. First date value: {data['date'].iloc[0]}, Type: {type(data['date'].iloc[0])}")


            # Calculate 'period' as Year + Q[1-4], e.g. 2025Q2
            logging.debug(f"Before period calculation. First date for period: {data['date'].iloc[0]}, Type: {type(data['date'].iloc[0])}")
            def get_period(date_obj):
                quarter = (date_obj.month - 1) // 3 + 1
                return f"{date_obj.year}Q{quarter}"

            # Explicitly cast 'period' column to string
            data['period'] = data['date'].apply(get_period).astype(str)
            logging.debug(f"After period calculation. First period value: {data['period'].iloc[0]}, Type: {type(data['period'].iloc[0])}")

            # Add static columns or defaults for dividends and earnings (update as needed)
            data['dividends'] = 0.0
            data['earnings'] = 1.0

            # Ensure all required columns are present and in correct order (optional, but good for debugging)
            required_columns = ['ticker', 'period', 'date', 'open', 'high', 'low', 'close', 'volume', 'dividends', 'earnings']
            logging.debug(f"Checking for required columns: {required_columns}")
            for col in required_columns:
                if col not in data.columns:
                    raise ValueError(f"Missing required column: {col} for {ticker}")
            logging.debug("All required columns are present.")
            logging.debug(f"DataFrame head before iteration for {ticker}:\n{data.head()}")
            logging.debug(f"DataFrame dtypes before iteration for {ticker}:\n{data.dtypes}")
            logging.debug(f"DataFrame index before iteration for {ticker}:\n{data.index}")
            logging.debug(f"DataFrame columns before iteration for {ticker}:\n{data.columns}")


            # Insert rows that don't already exist
            inserted_count = 0
            skipped_count = 0
            with engine.begin() as conn: # Use begin() for automatic commit/rollback
                for index, row in data.iterrows():
                    # IMPORTANT: Extract scalar values explicitly for all parameters
                    # This is the most robust way to ensure psycopg2 doesn't receive Series objects
                    try:
                        current_ticker_val = str(ticker) # Ensure ticker is string
                        current_period_val = str(row['period']) # Ensure period is string
                        current_date_val = row['date'] # Already datetime.date from earlier conversion

                        # Ensure it's datetime.date if it was datetime.datetime (redundant but safe after .dt.date)
                        if isinstance(current_date_val, datetime.datetime):
                            current_date_val = current_date_val.date()
                        elif not isinstance(current_date_val, datetime.date):
                             # This block should ideally not be hit after pd.to_datetime(...).dt.date
                             logging.error(f"❌ row['date'] is not datetime.date for {ticker} at index {index}: {type(current_date_val)}. Value: {current_date_val}. Skipping row.")
                             skipped_count += 1
                             continue

                        current_open_val = float(row['open'])
                        current_high_val = float(row['high'])
                        current_low_val = float(row['low'])
                        current_close_val = float(row['close'])
                        current_volume_val = int(row['volume']) # Ensure volume is int for BIGINT
                        current_dividends_val = float(row['dividends'])
                        current_earnings_val = float(row['earnings'])

                    except Exception as e:
                        logging.error(f"❌ Error extracting scalar values for {ticker} at index {index}: {e}. Skipping row.")
                        skipped_count += 1
                        continue

                    logging.debug(f"Processing row {index} for {ticker}. Extracted scalar values: "
                                  f"date={current_date_val} ({type(current_date_val)}), "
                                  f"open={current_open_val} ({type(current_open_val)}), "
                                  f"volume={current_volume_val} ({type(current_volume_val)})")

                    # IMPORTANT: Create the key based on (ticker, date) to match the DB's PRIMARY KEY
                    key = (current_ticker_val, current_date_val) # Use current_date_val which is guaranteed to be scalar datetime.date
                    logging.debug(f"Checking key: {key} (types: Ticker={type(key[0])}, Date={type(key[1])}) for row {index}")
                    if key in existing_records:
                        skipped_count += 1
                        continue

                    insert_stmt = text("""
                        INSERT INTO fundamentals (ticker, period, date, open, high, low, close, volume, dividends, earnings)
                        VALUES (:ticker, :period, :date, :open, :high, :low, :close, :volume, :dividends, :earnings)
                    """)
                    logging.debug(f"Attempting insert for {ticker} date {current_date_val}") # Use current_date_val in log
                    try:
                        conn.execute(insert_stmt, {
                            "ticker": current_ticker_val,
                            "period": current_period_val,
                            "date": current_date_val,
                            "open": current_open_val,
                            "high": current_high_val,
                            "low": current_low_val,
                            "close": current_close_val,
                            "volume": current_volume_val,
                            "dividends": current_dividends_val,
                            "earnings": current_earnings_val
                        })
                        existing_records.add(key) # Add to the set only on successful insertion
                        inserted_count += 1
                        logging.debug(f"Successfully inserted {ticker} date {current_date_val}")
                    except IntegrityError as e:
                        logging.warning(f"⚠️ Skipping duplicate or integrity violation for {ticker} date {current_date_val}: {e}")
                        skipped_count += 1
                    except ProgrammingError as e:
                        logging.error(f"❌ Database programming error during insert for {ticker} date {current_date_val}: {e}. Check column types/constraints.")
                        skipped_count += 1
                    except Exception as e:
                        logging.error(f"❌ Unexpected error during row insert for {ticker} date {current_date_val}: {e}")
                        skipped_count += 1
            logging.info(f"📊 {ticker}: Inserted {inserted_count} new records, skipped {skipped_count} existing/problematic records.")

        except Exception as e:
            logging.error(f"❌ Failed to process data for {ticker}: {e}")
            logging.error("Troubleshooting tips:")
            logging.error("1. Check internet connection (for yfinance)")
            logging.error("2. Verify ticker symbol is valid (e.g., AAPL, MSFT)")
            logging.error("3. Check if Yahoo Finance is accessible from your network")
            logging.error("4. Ensure PostgreSQL database is running and accessible (check DATABASE_URL, `db` hostname, port, user/password).")
            logging.error("5. Verify table schemas (`companies`, `fundamentals`) match the script's expectations.")
            logging.error("6. Ensure the 'companies' table has valid ticker symbols populated.")


if __name__ == "__main__":
    fetch_and_insert()
