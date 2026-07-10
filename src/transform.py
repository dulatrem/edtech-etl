import pandas as pd


def add_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute daily return, moving average, and volatility metrics for stock price data.

    Args:
        df: DataFrame of daily stock price data containing a "Close" column.

    Returns:
        A copy of the input DataFrame with three additional columns:
        daily_return (percent change in closing price from the previous day),
        moving_avg_7d (7-day rolling average of the closing price), and
        volatility_7d (7-day rolling standard deviation of the daily return).
    """
    result = df.copy()
    result["daily_return"] = result["Close"].pct_change()
    result["moving_avg_7d"] = result["Close"].rolling(window=7).mean()
    result["volatility_7d"] = result["daily_return"].rolling(window=7).std()
    return result
