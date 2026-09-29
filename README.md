# Edtech Stock ETL Pipeline

An ETL pipeline that extracts daily stock price data for publicly traded edtech
companies, computes return/volatility metrics, and loads the results through a
bronze → silver → gold medallion layout. The gold layer also drives a small
Plotly dashboard summarizing each ticker's risk and return.

## Architecture

The pipeline runs as a single `run_pipeline()` call (`main.py`) with three stages:

1. **Extract** — `src/extract.py` pulls daily OHLC history for each configured
   ticker via `yfinance`.
2. **Transform** — `src/transform.py` reshapes the wide multi-ticker data into
   long form (one row per date/ticker), then computes `daily_return`,
   `moving_avg_7d`, and `volatility_7d` per ticker.
3. **Load** — `src/load.py` writes each stage's output as CSV, either to the
   local `data/` folder or to S3, depending on which function is called.

### Medallion layers

| Layer | Contents | Produced by |
|---|---|---|
| **Bronze** | Raw price data straight from `yfinance`, wide format, untouched | `fetch_prices` |
| **Silver** | Long-format data with `daily_return`, `moving_avg_7d`, `volatility_7d` added | `reshape_to_long` + `add_metrics` |
| **Gold** | One row per ticker: latest close, latest return, latest volatility, average return over the period | `summarize_by_ticker` |

Each layer is written to its own path (`bronze/`, `silver/`, `gold/`) so
downstream consumers can read exactly the level of processing they need. The
gold layer also feeds `src/dashboard.py`, which renders an HTML dashboard
(bar chart of average return, scatter of risk vs. return).

## Tech stack

- **Python** — pipeline logic
- **pandas** — data wrangling and metric calculation
- **yfinance** — market data source
- **plotly** — dashboard charts
- **boto3** — S3 I/O and AWS integration
- **pytest** — tests
- **Docker** — Lambda container packaging
- **AWS Lambda + ECR + S3 + EventBridge** — scheduled cloud execution

## Project structure

```
.
├── main.py              # run_pipeline(): wires extract -> transform -> load
├── lambda_function.py   # Lambda entry point, calls run_pipeline()
├── Dockerfile            # Lambda container image build
├── config/
│   ├── tickers.py       # TICKERS list the extract stage runs against
│   └── aws.py           # BUCKET_NAME and other AWS settings
├── src/
│   ├── extract.py       # fetch_prices(tickers, period)
│   ├── transform.py     # reshape_to_long, add_metrics, summarize_by_ticker
│   ├── load.py          # save_data (local CSV), save_to_s3 (S3 CSV)
│   └── dashboard.py     # build_dashboard / build_dashboard_s3
├── tests/                # pytest suite, mirrors src/ module names
└── data/                 # local bronze/silver/gold output (gitignored)
```

## Local setup

```bash
python -m venv venv
venv/bin/pip install -r requirements.txt
```

## Running locally

```bash
venv/bin/python main.py
```

This runs the full pipeline and writes bronze/silver/gold CSVs to the S3
bucket configured in `config/aws.py` (`main.py` calls `save_to_s3` for each
layer). `src/load.py` also has a `save_data` function for writing to the
local `data/` folder instead, if you want to run without AWS credentials.

## Running tests

```bash
venv/bin/python -m pytest
```

## AWS Deployment

This pipeline is deployed as a **container-image Lambda** (rather than a zip)
because of its heavier dependencies (pandas, plotly, yfinance). The steps below
build the image, push it to ECR, create the Lambda, and schedule it to run daily.

**Values to replace with your own:**

| Value | Placeholder |
|---|---|
| AWS account ID | `<ACCOUNT_ID>` |
| Region | `us-east-1` (change if needed) |
| S3 bucket | `ed-tech-invest` |
| ECR repo / Lambda name | `edtech-etl` |
| Execution role | `edtech-etl-lambda-role` |

### 1. Build the container image

```bash
DOCKER_BUILDKIT=0 docker build -t edtech-etl .
```

`DOCKER_BUILDKIT=0` is required: the default modern Docker builder produces OCI
image manifests that AWS Lambda rejects. Disabling BuildKit produces the older
manifest format Lambda accepts.

### 2. Push the image to ECR

ECR (Elastic Container Registry) is AWS's storage for container images.

```bash
# Create the ECR repository (one time)
aws ecr create-repository --repository-name edtech-etl --region us-east-1

# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS \
    --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# Tag the local image with its ECR address
docker tag edtech-etl:latest \
  <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/edtech-etl:latest

# Push it
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/edtech-etl:latest
```

### 3. Create the Lambda execution role

The Lambda needs permission to read/write S3 and write logs to CloudWatch.

```bash
# Trust policy: allow Lambda to assume the role
cat > trust-policy.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Service": "lambda.amazonaws.com" },
    "Action": "sts:AssumeRole"
  }]
}
EOF

aws iam create-role --role-name edtech-etl-lambda-role \
  --assume-role-policy-document file://trust-policy.json

aws iam attach-role-policy --role-name edtech-etl-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-role-policy --role-name edtech-etl-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

### 4. Create the Lambda function from the image

```bash
aws lambda create-function \
  --function-name edtech-etl \
  --package-type Image \
  --code ImageUri=<ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/edtech-etl:latest \
  --role arn:aws:iam::<ACCOUNT_ID>:role/edtech-etl-lambda-role \
  --timeout 300 \
  --memory-size 1024 \
  --region us-east-1
```

`--package-type Image` deploys from the ECR container image (the container
equivalent of `--zip-file`). Timeout (300s) and memory (1024MB) are sized for
the pandas/plotly workload.

### 5. Schedule daily runs with EventBridge

EventBridge is AWS's scheduler — the cloud equivalent of cron.

```bash
# Create a rule that fires daily at 22:00 UTC
aws events put-rule --name edtech-etl-daily \
  --schedule-expression "cron(0 22 * * ? *)" \
  --region us-east-1

# Grant EventBridge permission to invoke the Lambda
aws lambda add-permission \
  --function-name edtech-etl \
  --statement-id eventbridge-invoke \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-1:<ACCOUNT_ID>:rule/edtech-etl-daily \
  --region us-east-1

# Point the rule at the Lambda
aws events put-targets --rule edtech-etl-daily \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:<ACCOUNT_ID>:function:edtech-etl" \
  --region us-east-1
```

### 6. Redeploying after code changes

Rebuild, push, and update the function to the new image:

```bash
DOCKER_BUILDKIT=0 docker build -t edtech-etl .
docker tag edtech-etl:latest \
  <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/edtech-etl:latest
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/edtech-etl:latest
aws lambda update-function-code \
  --function-name edtech-etl \
  --image-uri <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/edtech-etl:latest \
  --region us-east-1
```