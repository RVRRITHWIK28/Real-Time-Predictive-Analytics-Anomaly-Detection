# Online Retail II academic validation

## Scope and source

This report evaluates the weekly country–StockCode Random Forest forecast and hourly/daily revenue Isolation Forest using Online Retail II. UCI describes the dataset as two years of transactions from a UK-based online retailer, spanning 1 December 2009 through 9 December 2011; see the [UCI dataset record](https://archive.ics.uci.edu/dataset/502/online%2Bretail%2Bii). All forecasts are historical projections beyond each series' final observed week, not forecasts beyond today.

## Data preparation

The parser read 1,067,371 nonblank source rows: 1,041,670 positive sale lines, 19,494 cancellation invoices excluded, 3,457 nonpositive-quantity return/adjustment rows excluded, and 2,750 nonpositive-price rows excluded. No rows were classified invalid or blank. Revenue is quantity × unit price in GBP. Dates are interpreted in Europe/London business time.

Weekly demand is aggregated by country and StockCode. Missing weeks between the first and last sale for each series are filled with zero. Only pairs with at least 91 calendar weeks and at least 91 distinct weeks containing positive sales were evaluated. This leaves 479 eligible pairs and excludes 27,885 shorter or less active pairs. The eligible cohort is not representative of all products. The source does not provide inventory availability, so a zero-sales week can mean no demand or unavailable stock.

## Forecast evaluation design

The evaluated model is the project's Random Forest implementation: 200 trees, maximum depth 8, minimum leaf size 2, maximum feature fraction 0.9, fixed seed 42, lag/rolling/calendar features, and recursive forecasts up to 13 weeks. At each origin the model uses only data available before that origin.

For each eligible pair, the last 39 weeks in its own observed history are divided into three consecutive, non-overlapping 13-week test windows. The first test origin has at least 52 weeks of training history, which supports the seasonal-naive baseline. Each model produces 479 × 3 × 13 = 18,681 predictions. Metrics pool these predictions; they are not confidence intervals. MAE and RMSE are units sold, and WAPE is total absolute error divided by total actual units.

| Model | Predictions | MAE (units) | RMSE (units) | WAPE |
|---|---:|---:|---:|---:|
| Random Forest | 18,681 | 67.93 | 185.59 | 87.67% |
| Naive: repeat the last observed week | 18,681 | 63.59 | 169.26 | 82.07% |
| Seasonal naive: repeat the value 52 weeks earlier | 18,681 | 84.52 | 282.18 | 109.08% |

The Random Forest's MAE is 6.82% higher than the last-week baseline (worse) and 19.62% lower than the seasonal-naive baseline (better). It does not beat the strongest simple baseline overall. A pooled WAPE of 87.67% also means the aggregate absolute forecast error is large relative to aggregate actual demand. These results do not support describing the current forecast as reliable for inventory decisions without further model development and evaluation.

### Error by forecast horizon

| Week ahead | Random Forest MAE | Random Forest WAPE | Last-week naive MAE | 52-week seasonal naive MAE |
|---:|---:|---:|---:|---:|
| 1 | 63.62 | 80.68% | 60.92 | 73.17 |
| 2 | 69.89 | 96.27% | 57.00 | 94.74 |
| 3 | 74.32 | 102.50% | 58.46 | 83.41 |
| 4 | 82.61 | 98.61% | 65.08 | 89.13 |
| 5 | 68.58 | 97.71% | 59.44 | 79.12 |
| 6 | 64.61 | 88.81% | 61.62 | 76.92 |
| 7 | 63.88 | 91.98% | 61.10 | 83.36 |
| 8 | 66.53 | 78.38% | 68.57 | 82.23 |
| 9 | 63.33 | 74.29% | 67.70 | 84.07 |
| 10 | 59.78 | 72.26% | 66.04 | 79.78 |
| 11 | 67.46 | 82.62% | 67.40 | 78.35 |
| 12 | 67.45 | 95.80% | 62.63 | 95.57 |
| 13 | 71.07 | 86.41% | 70.77 | 98.89 |

There are 1,437 predictions at each horizon (479 pairs × 3 folds). The complete metrics, including RMSE, WAPE, and both baseline comparisons for each horizon, are in forecast_metrics_by_horizon.csv. The evaluation script also generates row-level forecasts and actuals in forecast_backtest_predictions.csv when run locally; that large intermediate file is not included in this pull request.

## Revenue anomaly evaluation

The project runs separate Isolation Forest detectors on hourly and daily revenue buckets with time/calendar features and log revenue, using chronological historical replay and periodic refits. The contamination parameter is 1%; that is a model setting, not measured incident prevalence.

The replay produced 198 hourly flags from 17,718 buckets (1.12%) and 74 daily flags from 739 buckets (10.01%). The totals are **model flags**, not confirmed incidents. Daily flag volume is notably higher than the configured contamination fraction and merits calibration review.

A chronological holdout contained 5,316 hourly and 222 daily buckets. The detector flagged 0.92% of hourly and 0.90% of daily holdout buckets. These are unlabeled holdout flag rates, not false-positive rates.

Controlled perturbations were applied to real positive-revenue holdout buckets. Results measure sensitivity only to those specific synthetic changes:

| Scale | Known perturbation | Cases | Detected | Detection rate |
|---|---|---:|---:|---:|
| Hourly | Revenue multiplied by 5 | 300 | 105 | 35.00% |
| Hourly | Revenue reduced by 90% | 300 | 1 | 0.33% |
| Daily | Revenue multiplied by 5 | 188 | 0 | 0.00% |
| Daily | Revenue reduced by 90% | 188 | 0 | 0.00% |

These results show that the current detector is not sufficiently sensitive to the tested shifts, especially at daily scale and for revenue drops. Natural-anomaly labels are absent, so precision, recall, and false-positive rates for real incidents cannot be estimated. Do not describe the 272 replay flags as confirmed anomalies.

A stratified 60-row audit sample contains 15 flags for each scale/direction combination. I screened the observed-to-baseline ratios with explicit descriptive bands: strong (at least 2× or at most 0.5×), moderate (at least 1.5× or at most 0.67×), mild (at least 1.25× or at most 0.8×), and near-median (0.8×–1.25×). The sample had 39 strong, 9 moderate, 3 mild, and 9 near-median cases. Because the sample is balanced by scale and direction rather than randomly sampled in proportion to all flags, these counts are only descriptive. An hourly spike sample often had a high largest-invoice share (median 76.96%); this can reflect a legitimate wholesaler order and is not proof of an incident. The detailed worksheet contains timestamps, revenue, and invoice-context fields, so it is retained locally and excluded from this pull request. Its review-label and notes fields remain blank for a human to adjudicate; no natural-event truth labels are claimed.

Generated anomaly outputs:
- academic_validation_summary.json: source counts, bucket counts, model flags, and holdout rates.
- anomaly_injection_validation.csv: controlled perturbation results.
- The detailed anomaly review worksheet is generated locally by the script and is excluded from the pull request.

## Limitations

- The dataset ends in December 2011; forecasts are historical projections after the observed data.
- The forecast is evaluated only for long-history/high-activity country–StockCode pairs.
- Zero-filled weeks may represent stockouts or no availability; inventory is not observed.
- Cancellations and returns are excluded, so the modeled target is positive gross sales rather than net demand or net revenue.
- The product codes may include service/manual entries; the source has no clean merchandise taxonomy.
- No labeled natural anomalies or adjudicated incidents exist.
- Results pool related time windows and SKU series, which are dependent; no uncertainty intervals are reported.
- This is retrospective validation, not a prospective deployment trial.

## Dataset citation

Chen, D. (2012). *Online Retail II* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D.