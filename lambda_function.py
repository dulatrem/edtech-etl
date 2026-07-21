from main import run_pipeline


def lambda_handler(event, context):
    """AWS Lambda entry point that runs the ETL pipeline."""
    run_pipeline()
    return {"statusCode": 200, "body": "Pipeline completed successfully."}
