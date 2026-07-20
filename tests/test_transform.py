import pandas as pd
import pytest

from src.transform import add_metrics, reshape_to_long


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
