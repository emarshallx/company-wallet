PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS periods (id TEXT PRIMARY KEY, end_date TEXT NOT NULL, basis TEXT NOT NULL CHECK(basis='US GAAP'));
CREATE TABLE IF NOT EXISTS metrics (code TEXT PRIMARY KEY, label TEXT NOT NULL, section TEXT NOT NULL, unit TEXT NOT NULL DEFAULT 'USD millions');
CREATE TABLE IF NOT EXISTS facts (period_id TEXT REFERENCES periods(id), metric_code TEXT REFERENCES metrics(code), value REAL NOT NULL, source_url TEXT NOT NULL, PRIMARY KEY(period_id, metric_code));
CREATE TABLE IF NOT EXISTS scenarios (id INTEGER PRIMARY KEY, name TEXT NOT NULL, period_id TEXT REFERENCES periods(id), assumptions TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE VIEW IF NOT EXISTS wallet_totals AS
SELECT period_id,
 MAX(CASE WHEN metric_code='cash' THEN value END) AS cash,
 MAX(CASE WHEN metric_code='liquidity' THEN value END) AS liquid_assets,
 MAX(CASE WHEN metric_code='debt_current' THEN value END)+MAX(CASE WHEN metric_code='debt_long' THEN value END) AS debt,
 MAX(CASE WHEN metric_code='cfo' THEN value END)-MAX(CASE WHEN metric_code='capex' THEN value END)-MAX(CASE WHEN metric_code='capex_principal' THEN value END) AS free_cash_flow
FROM facts GROUP BY period_id;
