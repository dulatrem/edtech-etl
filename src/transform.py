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


def summarize_by_ticker(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize long-format metric data into one row per ticker.

    Args:
        df: Long-format DataFrame with metrics, as returned by add_metrics.

    Returns:
        A DataFrame with one row per ticker and columns: latest_close (the
        last Close value), latest_return (the last daily_return value),
        latest_volatility (the last volatility_7d value), and
        avg_return_period (the mean daily_return across the whole period).
    """
    return df.groupby("Ticker").agg(
        latest_close=("Close", "last"),
        latest_return=("daily_return", "last"),
        latest_volatility=("volatility_7d", "last"),
        avg_return_period=("daily_return", "mean"),
    ).reset_index()
