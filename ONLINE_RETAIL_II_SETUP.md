# Switch the project to Online Retail II

This project copy replays the supplied Online Retail II transactions through the existing Kafka, MongoDB, FastAPI, anomaly, forecasting, and Streamlit pipeline. The data is historical, so the dashboard reports a replay rather than current live sales.

## 1. Place the dataset

From the project root, create `data/raw` if it does not exist, then copy the ZIP you downloaded:

```powershell
New-Item -ItemType Directory -Force data/raw | Out-Null
Copy-Item "C:\Users\rithw\Downloads\online+retail+ii.zip" "data/raw/online+retail+ii.zip"
```

The importer reads the Excel workbook inside the ZIP directly in read-only mode. Keep the ZIP out of Git.

## 2. Create the Python environment

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 3. Prepare and train the dataset-specific demand model

```powershell
.\.venv\Scripts\python.exe -m src.ml.create_training_dataset
.\.venv\Scripts\python.exe -m src.ml.feature_engineering
.\.venv\Scripts\python.exe -m src.ml.train_test_split
.\.venv\Scripts\python.exe -m src.ml.save_demand_model
```

The default forecast-readiness screen requires at least 90 active sale days, 100 distinct invoices, 500 units, and a 365-day observation span for each product/country series. You can adjust those values in `.env` using `ONLINE_RETAIL_MIN_ACTIVE_DAYS`, `ONLINE_RETAIL_MIN_INVOICES`, `ONLINE_RETAIL_MIN_UNITS`, and `ONLINE_RETAIL_MIN_SPAN_DAYS`.

Daily zeroes are added only between a product/country series' first and last recorded sale. Online Retail II does not include inventory availability, so those zeroes are a modeling assumption rather than proof that a product was in stock.

The source has StockCodes for both merchandise and service/manual entries, and its descriptions are not a clean merchandise category system. Some service codes may pass the numeric forecast-readiness screen; review product descriptions before treating every forecast as physical product demand.

## 4. Configure the separate database

Use the provided environment template so this run does not combine its records with the old synthetic demo database. If the project already has a `.env`, keep it and update the settings below instead of overwriting it:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.online-retail.example .env }
```

The template uses `DATABASE_NAME=online_retail_ii`. Change the MongoDB connection settings in `.env` if your local setup needs different values. Do not put a production password in a file that you commit.

## 5. Start the application

```powershell
docker compose up -d --build
```

The producer container mounts `data/raw` read-only and sends valid positive sale lines to Kafka in batches. Check progress with:

```powershell
docker compose logs -f transaction-producer
```

The full workbook has over one million transaction rows, so the initial replay can take time. The producer reports how many source rows were sent and how many cancellations, returns/adjustments, and invalid rows it skipped.

## How source fields are represented

- `StockCode` becomes the product identifier, and the supplied description is retained. The dataset has no category field, so `category` is marked `Unclassified`.
- The existing pipeline's internal `store_id` key carries the dataset's country value. The dashboard labels it **Country**; it does not invent physical stores.
- The dataset has no discount or payment method. Those fields are stored as null. Revenue is `Quantity × Price` in GBP.
- Missing customer IDs stay null. The workbook's local invoice clock is timezone-aware using `Europe/London`; a separate `business_date` preserves the original calendar date.
- For forecasting and sales anomaly detection, the stream sends only positive-quantity, positive-price, non-cancellation sale lines. Cancellation invoices and negative/zero-quantity returns or adjustments are counted and skipped by this stream. Use the separate Phase 1–3 analysis pipeline to analyze full cancellation and return accounting.

## Scope

The public AWS demo is not changed by this local source bundle. To see these changes at the existing URL, you would still need to deploy this source and configure the AWS environment for the dataset. The synthetic data generator remains available for the original demo; Docker Compose now starts the Online Retail II replay producer.
