from io import StringIO
from pathlib import Path

import boto3
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


def save_to_s3(df: pd.DataFrame, layer: str, bucket: str) -> None:
    """Upload a DataFrame as CSV to S3 under the given data layer.

    Args:
        df: DataFrame to upload.
        layer: Name of the data layer, e.g. "bronze", "silver", or "gold".
            Determines the destination key: <layer>/prices.csv.
        bucket: Name of the S3 bucket to upload to.
    """
    buffer = StringIO()
    df.to_csv(buffer, index=False)
    s3 = boto3.client("s3")
    s3.put_object(Bucket=bucket, Key=f"{layer}/prices.csv", Body=buffer.getvalue())
