# Company Wallet

An obsidian, emerald and cyan glass financial workspace built for Emmanuel. Python + SQLite powers the local app; the hosted browser demo uses the same exported financial snapshot and an equivalent JavaScript sensitivity model.

## Start on Windows / PyCharm

1. Extract the ZIP into a folder.
2. Open that folder in PyCharm or a terminal.
3. Run `python app.py` (or `py app.py` on Windows).
4. Open http://localhost:8000 in your browser.

Requires Python 3.10 or newer. No pip installations, API keys or paid services required. Keep the terminal running. To change port: `python app.py --port 8001`. The server binds to your computer only. This is a personal local app, not a production multi-user service.

## Features

- Wallet cards for cash, current investments, debt, net liquid assets and free cash flow.
- FY2025 / FY2026 selector; USD millions / billions.
- Click-to-explain figures with original source links.
- Cash bridge and comparative profitability analysis.
- Five-lever sensitivity model with presets and saved scenarios.
- Comparative condensed income, financial position and cash-flow reports; CSV export and browser Print / Save PDF.
- IFRS review notes, checklist and CSV export. No unsupported IFRS-compliance claim.

## Source and accounting basis

NVIDIA FY2026 public results, released February 25, 2026:
https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-Fourth-Quarter-and-Fiscal-2026/default.aspx

FY2026 ends January 25, 2026; FY2025 ends January 26, 2025. USD millions throughout the database. This is a pinned annual dataset, not a live feed or the latest interim results. Condensed statements in this source are labelled unaudited and use US GAAP. Financial labels are simplified in the UI. Current securities are derived as combined cash/securities less closing cash. Cash and securities are not interchangeable. Financial debt excludes leases.

Free cash flow = operating cash flow - purchases of property/equipment/intangibles - related principal payments. This is NVIDIA's disclosed non-GAAP definition. Net liquid assets is our analytical subtotal.

IFRS notes do not convert NVIDIA's figures. A compliant IFRS statement set would require supported recognition/measurement adjustments, policies, OCI, changes in equity, comparative information and disclosures. The checklist is limited and is not certification. No automatic GAAP-to-IFRS conversion is claimed.

## Scenario model

Starting cash is the selected year-end cash. A zero-change scenario repeats the selected year's cash flows for another year, so its ending cash differs from the historical closing cash. Revenue and gross margin drive net profit at fixed opex, other income and effective tax rate; no tax benefit on losses. CFO = historical CFO + change in profit - modeled revenue / 365 * additional collection days. Historical investing and financing repeat, adjusted for additional capital spending and borrowing. Other working capital and noncash adjustments remain fixed. No incremental depreciation, interest, repayment, or automatic securities sales. Negative ending cash denotes a funding gap. This is a sensitivity model, not company guidance or a complete three-statement forecast.

## Files

- `app.py`: standard-library web server, SQLite data and scenario API.
- `seed.py`: sourced facts; idempotent SQLite seeding and static export.
- `schema.sql`: normalized periods, metrics, facts, saved scenarios and wallet view.
- `model.py`: Python sensitivity model with input validation.
- `dist/`: responsive front end and exported dataset.
- `test_financials.py`: accounting reconciliation and model checks.

SQLite database `wallet.db` is created on first run. Scenario names and assumptions are saved there in local mode. Hosted demo scenario drafts and IFRS review drafts are temporary browser state; export them to retain a copy. In both modes IFRS review drafts use browser storage. Source facts stay unchanged.

## API

GET /api/data; GET /api/scenarios; POST /api/project; POST /api/scenarios.

JSON body for projection: {"period":"FY2026","assumptions":{"growth":0,"margin":0,"days":0,"capex":0,"borrowing":0}}. Add "name" when saving. The UI uses the equivalent JavaScript model for immediate slider response; the Python endpoint supports programmatic use and validates saved scenarios.

## Updating data

Add verified periods and sourced facts to seed.py, then run `python seed.py`. Maintain instant-versus-duration distinctions, source dates, units and accounting basis. Do not mix quarterly amounts with annual values. Rerun `python -m unittest test_financials.py` after changes.
