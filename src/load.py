from pathlib import Path

import pandas as pd


def save_data(df: pd.DataFrame, layer: str) -> None:
    """Save a DataFrame to a CSV file under the given data layer.

    Args:
        df: DataFrame to save.
        layer: Name of the data layer, e.g. "bronze", "silver", or "gold".
            Determines the output folder: data/<layer>/prices.csv.
    """
    folder = Path("data") / layer
    folder.mkdir(parents=True, exist_ok=True)
    df.to_csv(folder / "prices.csv", index=False)
