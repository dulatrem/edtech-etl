import pandas as pd
import yfinance as yf


def fetch_prices(tickers: list[str], period: str = "1mo") -> pd.DataFrame:
    """Fetch daily historical price data for a list of tickers.

    Args:
        tickers: List of ticker symbols to fetch data for.
        period: Time period to fetch, e.g. "1mo", "1y" (defaults to "1mo").

    Returns:
        A pandas DataFrame containing the daily historical price data.
    """
    return yf.download(tickers, period=period, interval="1d")
