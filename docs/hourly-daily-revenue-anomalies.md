# Hourly and daily revenue anomaly detection

## What the models score

The anomaly service aggregates positive Online Retail II sale-line revenue into two independent time series:

- **Hourly:** total revenue in each London-time hour.
- **Daily:** total revenue in each London-time calendar day.

Historical gaps between the first and last sale timestamps are filled with zero-revenue buckets. This lets the models learn normal quiet hours as well as busy periods. The live consumer scores an hour or day after that bucket is complete.

A separate scikit-learn Isolation Forest is used for each scale. Revenue is log-transformed and the feature set includes cyclical time features so the model can account for hour-of-day, weekday, and annual seasonality. Historical records are scored walk-forward against earlier buckets to avoid training on the same observation being judged. The first 14 days of hourly buckets and 60 days of daily buckets are warm-up history; no alerts are emitted during warm-up. Models refresh their rolling training window about every 30 days.

## Alert-rate setting

`REVENUE_IF_CONTAMINATION` defaults to `0.01` (1%) in the anomaly-consumer service. Isolation Forest uses this to set the expected outlier share in its training window. It is a tuning choice, not a measured false-positive rate or a claim that 1% of sales are truly anomalous. Lower values generally produce fewer alerts; review hourly and daily results against the business calendar before using them operationally.

To adjust it, set `REVENUE_IF_CONTAMINATION` in the copied `.env` file and recreate the anomaly consumer. A model backfill runs on startup.

## How to read the count

The dashboard's hourly count is the number of **hour buckets** classified as unusual; its daily count is the number of **day buckets** classified as unusual. A sale line can contribute to one hourly and one daily bucket, so the sum is not a count of unique transactions or customers. These are unsupervised review signals. The dataset has no labeled ground truth for revenue anomalies, so model alerts should not be described as confirmed fraud or verified incidents.

The prior minute-rule documents remain in MongoDB for history, but the API and dashboard count and display only records tagged with model version `isolation_forest_v1`.
