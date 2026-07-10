import pandas as pd
import pytest

from src.transform import add_metrics


def test_adds_expected_columns():
    """Check that add_metrics adds the daily_return, moving_avg_7d, and volatility_7d columns."""
    df = pd.DataFrame({"Close": [100, 102, 101, 105, 107]})
    result = add_metrics(df)
    assert "daily_return" in result.columns
    assert "moving_avg_7d" in result.columns
    assert "volatility_7d" in result.columns


def test_daily_return_calculation():
    """Check that daily_return is computed correctly as the percent change from the previous day."""
    df = pd.DataFrame({"Close": [100, 110]})
    result = add_metrics(df)
    assert result["daily_return"].iloc[1] == pytest.approx(0.10)


def test_original_not_modified():
    """Check that add_metrics does not modify the original DataFrame."""
    df = pd.DataFrame({"Close": [100, 102, 101]})
    add_metrics(df)
    assert "daily_return" not in df.columns
