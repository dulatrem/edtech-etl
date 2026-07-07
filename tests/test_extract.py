import pandas as pd

from src.extract import fetch_prices


def test_returns_dataframe():
    """Check that fetch_prices returns a pandas DataFrame."""
    result = fetch_prices(["DUOL"])
    assert isinstance(result, pd.DataFrame)


def test_dataframe_not_empty():
    """Check that fetch_prices returns a DataFrame with rows."""
    result = fetch_prices(["DUOL"])
    assert len(result) > 0


def test_accepts_multiple_tickers():
    """Check that fetch_prices works with more than one ticker."""
    result = fetch_prices(["DUOL", "CHGG"])
    assert len(result) > 0
