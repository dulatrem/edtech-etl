# CLAUDE.md — Working preferences for this project

## How I want you to work with me
- I'm learning data engineering. Favor teaching me over doing things for me.
- Explain your reasoning before making non-trivial changes.
- When a test fails, explain what's causing it and let me decide the fix.
  Do NOT automatically change code just to make a test pass.
- Don't add features, error handling, or extras I didn't ask for.
- Keep changes small and focused on exactly what I requested.

## Project context
- ETL pipeline for edtech stock prices (extract → transform → load).
- Stack: Python, pandas, yfinance, pytest. Headed for AWS Lambda + S3.
- Structure: src/ (pipeline code), tests/ (pytest), config/ (settings), data/ (gitignored output).
- Every change follows: branch → build → commit → push → PR → merge.

## Commands
Run from the repo root, using the project venv:
- All tests: `venv/bin/python -m pytest`
- Single test file: `venv/bin/python -m pytest tests/test_transform.py`
- Single test: `venv/bin/python -m pytest tests/test_transform.py::test_daily_return_calculation`
- Install deps: `venv/bin/pip install -r requirements.txt`

## Architecture
- `src/extract.py` — `fetch_prices(tickers, period)` pulls daily OHLC history via `yfinance`.
- `src/transform.py` — `add_metrics(df)` takes a price DataFrame (expects a `Close` column) and returns a new DataFrame with derived columns (`daily_return`, `moving_avg_7d`, `volatility_7d`). Always works on a copy; never mutates the input.
- `src/load.py` — load stage, not yet implemented.
- `config/tickers.py` — the `TICKERS` list the extract stage runs against.
- Tests mirror `src/` module names and import with absolute paths (`from src.extract import fetch_prices`), so pytest must run from the repo root.