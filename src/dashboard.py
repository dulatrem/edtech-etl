import os

import boto3
import pandas as pd
import plotly.graph_objects as go

SURFACE = "#fcfcfb"
PRIMARY_INK = "#0b0b0b"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"
POSITIVE = "#2a78d6"
NEGATIVE = "#e34948"


def build_dashboard(df: pd.DataFrame, output_path: str = "output/dashboard.html") -> None:
    """Build an HTML dashboard from the gold summary DataFrame.

    Args:
        df: Gold-layer summary DataFrame with one row per ticker and columns
            Ticker, latest_close, latest_return, latest_volatility, and
            avg_return_period, as returned by summarize_by_ticker.
        output_path: Path to write the combined HTML dashboard to. Parent
            directories are created if they don't already exist.
    """
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    bar_colors = [POSITIVE if v >= 0 else NEGATIVE for v in df["avg_return_period"]]
    bar_fig = go.Figure(
        go.Bar(x=df["Ticker"], y=df["avg_return_period"], marker_color=bar_colors)
    )
    bar_fig.update_layout(
        title="Average Daily Return by Company",
        xaxis_title="Ticker",
        yaxis_title="Average Daily Return",
        plot_bgcolor=SURFACE,
        paper_bgcolor=SURFACE,
        font_color=PRIMARY_INK,
    )
    bar_fig.update_xaxes(showgrid=False)
    bar_fig.update_yaxes(gridcolor=GRIDLINE, zerolinecolor=BASELINE)

    scatter_fig = go.Figure(
        go.Scatter(
            x=df["latest_volatility"],
            y=df["avg_return_period"],
            mode="markers+text",
            text=df["Ticker"],
            textposition="top center",
            marker=dict(color=POSITIVE, size=10),
        )
    )
    scatter_fig.update_layout(
        title="Risk vs Return",
        xaxis_title="Latest Volatility (7d)",
        yaxis_title="Average Daily Return",
        plot_bgcolor=SURFACE,
        paper_bgcolor=SURFACE,
        font_color=PRIMARY_INK,
    )
    scatter_fig.update_xaxes(gridcolor=GRIDLINE)
    scatter_fig.update_yaxes(gridcolor=GRIDLINE, zerolinecolor=BASELINE)

    bar_html = bar_fig.to_html(full_html=False, include_plotlyjs=True)
    scatter_html = scatter_fig.to_html(full_html=False, include_plotlyjs=False)

    page = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Ticker Dashboard</title>
</head>
<body style="background:#f9f9f7; font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;">
{bar_html}
{scatter_html}
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(page)


def build_dashboard_s3(df: pd.DataFrame, bucket: str, key: str = "dashboard.html") -> None:
    """Build an HTML dashboard from the gold summary DataFrame and upload it to S3.

    Args:
        df: Gold-layer summary DataFrame with one row per ticker and columns
            Ticker, latest_close, latest_return, latest_volatility, and
            avg_return_period, as returned by summarize_by_ticker.
        bucket: Name of the S3 bucket to upload the dashboard HTML to.
        key: S3 key to upload the dashboard HTML under.
    """
    bar_colors = [POSITIVE if v >= 0 else NEGATIVE for v in df["avg_return_period"]]
    bar_fig = go.Figure(
        go.Bar(x=df["Ticker"], y=df["avg_return_period"], marker_color=bar_colors)
    )
    bar_fig.update_layout(
        title="Average Daily Return by Company",
        xaxis_title="Ticker",
        yaxis_title="Average Daily Return",
        plot_bgcolor=SURFACE,
        paper_bgcolor=SURFACE,
        font_color=PRIMARY_INK,
    )
    bar_fig.update_xaxes(showgrid=False)
    bar_fig.update_yaxes(gridcolor=GRIDLINE, zerolinecolor=BASELINE)

    scatter_fig = go.Figure(
        go.Scatter(
            x=df["latest_volatility"],
            y=df["avg_return_period"],
            mode="markers+text",
            text=df["Ticker"],
            textposition="top center",
            marker=dict(color=POSITIVE, size=10),
        )
    )
    scatter_fig.update_layout(
        title="Risk vs Return",
        xaxis_title="Latest Volatility (7d)",
        yaxis_title="Average Daily Return",
        plot_bgcolor=SURFACE,
        paper_bgcolor=SURFACE,
        font_color=PRIMARY_INK,
    )
    scatter_fig.update_xaxes(gridcolor=GRIDLINE)
    scatter_fig.update_yaxes(gridcolor=GRIDLINE, zerolinecolor=BASELINE)

    bar_html = bar_fig.to_html(full_html=False, include_plotlyjs=True)
    scatter_html = scatter_fig.to_html(full_html=False, include_plotlyjs=False)

    page = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Ticker Dashboard</title>
</head>
<body style="background:#f9f9f7; font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;">
{bar_html}
{scatter_html}
</body>
</html>"""

    s3 = boto3.client("s3")
    s3.put_object(Bucket=bucket, Key=key, Body=page, ContentType="text/html")
