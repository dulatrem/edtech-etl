import pandas as pd
import pytest

from src.transform import add_metrics, reshape_to_long, summarize_by_ticker


def test_reshape_produces_long_format():
    """Check that reshape_to_long converts wide MultiIndex data to one row per (Date, Ticker)."""
    columns = pd.MultiIndex.from_product(
        [["Close"], ["DUOL", "CHGG"]], names=["Price", "Ticker"]
    )
    df = pd.DataFrame([[100, 50], [110, 55]], columns=columns)
    df.index.name = "Date"
    result = reshape_to_long(df)
    assert "Ticker" in result.columns
    assert len(result) == 4


def test_adds_metric_columns():
    """Check that add_metrics adds the daily_return, moving_avg_7d, and volatility_7d columns."""
    df = pd.DataFrame({
        "Ticker": ["DUOL", "DUOL", "CHGG", "CHGG"],
        "Close": [100, 110, 50, 55],
    })
    result = add_metrics(df)
    assert "daily_return" in result.columns
    assert "moving_avg_7d" in result.columns
    assert "volatility_7d" in result.columns


def test_daily_return_per_ticker():
    """Check that daily_return is computed per ticker, not across the whole DataFrame."""
    df = pd.DataFrame({
        "Ticker": ["DUOL", "DUOL", "CHGG", "CHGG"],
        "Close": [100, 110, 50, 55],
    })
    result = add_metrics(df)
    assert result["daily_return"].iloc[1] == pytest.approx(0.10)
    assert result["daily_return"].iloc[3] == pytest.approx(0.10)
    assert pd.isna(result["daily_return"].iloc[0])
    assert pd.isna(result["daily_return"].iloc[2])


def test_one_row_per_ticker():
    """Check that summarize_by_ticker returns exactly one row per ticker."""
    df = pd.DataFrame({
        "Ticker": ["DUOL", "DUOL", "CHGG", "CHGG"],
        "Close": [100, 110, 50, 55],
        "daily_return": [0.10, 0.20, 0.30, 0.40],
        "volatility_7d": [0.01, 0.02, 0.03, 0.04],
    })
    result = summarize_by_ticker(df)
    assert len(result) == 2


def test_summary_values_per_ticker():
    """Check that summarize_by_ticker computes the latest and average values correctly per ticker."""
    df = pd.DataFrame({
        "Ticker": ["DUOL", "DUOL", "CHGG", "CHGG"],
        "Close": [100, 110, 50, 55],
        "daily_return": [0.10, 0.20, 0.30, 0.40],
        "volatility_7d": [0.01, 0.02, 0.03, 0.04],
    })
    result = summarize_by_ticker(df)
    duol_row = result[result["Ticker"] == "DUOL"].iloc[0]
    assert duol_row["latest_close"] == 110
    assert duol_row["avg_return_period"] == pytest.approx(0.15)
