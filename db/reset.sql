-- Truncate data only (keep structure)
TRUNCATE TABLE fundamentals;
TRUNCATE TABLE companies;

-- Optionally, reinsert your default companies
INSERT INTO companies (ticker, name) VALUES
('AAPL', 'Apple Inc.'),
('MSFT', 'Microsoft Corporation'),
('TSLA', 'Tesla Inc.')
ON CONFLICT (ticker) DO NOTHING;
