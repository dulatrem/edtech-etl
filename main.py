from config.aws import BUCKET_NAME
from config.tickers import TICKERS
from src.dashboard import build_dashboard
from src.extract import fetch_prices
from src.load import save_data, save_to_s3
from src.transform import add_metrics, reshape_to_long, summarize_by_ticker


def run_pipeline():
    """Run the full ETL pipeline: extract raw prices, save to bronze,
    compute metrics, and save the transformed data to silver.
    """
    raw_data = fetch_prices(TICKERS)
    save_data(raw_data, "bronze")
    save_to_s3(raw_data, "bronze", BUCKET_NAME)

    long_data = reshape_to_long(raw_data)
    transformed_data = add_metrics(long_data)
    save_data(transformed_data, "silver")
    save_to_s3(transformed_data, "silver", BUCKET_NAME)

    summary_data = summarize_by_ticker(transformed_data)
    save_data(summary_data, "gold")
    save_to_s3(summary_data, "gold", BUCKET_NAME)

    build_dashboard(summary_data)


if __name__ == "__main__":
    run_pipeline()
