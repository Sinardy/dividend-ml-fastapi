-- Drop existing tables to avoid conflicts
DROP TABLE IF EXISTS fundamentals;
DROP TABLE IF EXISTS companies;

-- Create companies table
CREATE TABLE companies (
    ticker VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255)
);

-- Create fundamentals table
CREATE TABLE fundamentals (
    ticker VARCHAR(10) REFERENCES companies(ticker),
    period VARCHAR(10),
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

-- Optional: Insert some initial companies
INSERT INTO companies (ticker, name) VALUES
('AAPL', 'Apple Inc.'),
('MSFT', 'Microsoft Corporation'),
('TSLA', 'Tesla Inc.')
ON CONFLICT (tic
