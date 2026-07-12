from pathlib import Path

import pandas as pd

from src.load import save_data


def test_saves_csv_file():
    """Check that save_data writes a CSV file to data/<layer>/prices.csv."""
    df = pd.DataFrame({"Close": [100, 101], "Volume": [1000, 1100]})
    save_data(df, "bronze")
    path = Path("data/bronze/prices.csv")
    assert path.exists()
    path.unlink()
