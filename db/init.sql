
CREATE TABLE IF NOT EXISTS companies (
    ticker VARCHAR PRIMARY KEY,
    name VARCHAR
);
CREATE TABLE IF NOT EXISTS fundamentals (
    ticker VARCHAR,
    period VARCHAR,
    date DATE,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume BIGINT,
    dividends FLOAT,
    earnings FLOAT,
    PRIMARY KEY (ticker, date)
);
