from config.tickers import TICKERS
from src.extract import fetch_prices
from src.load import save_data
from src.transform import add_metrics, reshape_to_long, summarize_by_ticker


def run_pipeline():
    """Run the full ETL pipeline: extract raw prices, save to bronze,
    compute metrics, and save the transformed data to silver.
    """
    raw_data = fetch_prices(TICKERS)
    save_data(raw_data, "bronze")

    long_data = reshape_to_long(raw_data)
    transformed_data = add_metrics(long_data)
    save_data(transformed_data, "silver")

    summary_data = summarize_by_ticker(transformed_data)
    save_data(summary_data, "gold")


if __name__ == "__main__":
    run_pipeline()
