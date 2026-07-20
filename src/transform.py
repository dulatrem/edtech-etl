import pandas as pd


def reshape_to_long(df: pd.DataFrame) -> pd.DataFrame:
    """Reshape multi-ticker price data from wide to long format.

    Args:
        df: Wide-format DataFrame with MultiIndex columns (price field x ticker),
            as returned by fetch_prices for multiple tickers.

    Returns:
        A long-format DataFrame with one row per (Date, Ticker).
    """
    return df.stack(future_stack=True).reset_index()


def add_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute per-ticker metrics on long-format price data.

    Args:
        df: Long-format DataFrame with one row per (Date, Ticker), including
            "Ticker" and "Close" columns.

    Returns:
        A copy of df with three additional columns, each computed within
        each ticker group: daily_return (percent change in closing price
        from the previous day), moving_avg_7d (7-day rolling average of the
        closing price), and volatility_7d (7-day rolling standard deviation
        of the daily return).
    """
    result = df.copy()
    result["daily_return"] = result.groupby("Ticker")["Close"].pct_change()
    result["moving_avg_7d"] = result.groupby("Ticker")["Close"].transform(
        lambda close: close.rolling(window=7).mean()
    )
    result["volatility_7d"] = result.groupby("Ticker")["daily_return"].transform(
        lambda daily_return: daily_return.rolling(window=7).std()
    )
    return result
