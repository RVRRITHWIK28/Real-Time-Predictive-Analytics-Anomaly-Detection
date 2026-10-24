"""Build calendar-day demand histories from Online Retail II sale lines."""

from __future__ import annotations

import csv
import os
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv

from src.ingestion.online_retail_ii import (
    DEFAULT_ARCHIVE,
    iter_online_retail_sales,
    new_source_stats,
)

load_dotenv()


OUTPUT_FILE = Path("data/processed/daily_product_demand.csv")
MIN_ACTIVE_DAYS = int(os.getenv("ONLINE_RETAIL_MIN_ACTIVE_DAYS", "90"))
MIN_INVOICES = int(os.getenv("ONLINE_RETAIL_MIN_INVOICES", "100"))
MIN_UNITS = int(os.getenv("ONLINE_RETAIL_MIN_UNITS", "500"))
MIN_SPAN_DAYS = int(os.getenv("ONLINE_RETAIL_MIN_SPAN_DAYS", "365"))


def create_training_dataset(
    archive_path: str | Path = DEFAULT_ARCHIVE,
    output_path: str | Path = OUTPUT_FILE,
) -> dict[str, int]:
    """Create zero-filled daily histories for sufficiently observed SKU/country series.

    Zeroes are written only between a series' first and last recorded sale.
    The source has no inventory or assortment table, so those zeroes are not
    evidence that a product was in stock on every date.
    """
    daily_sales: dict[tuple[str, str, date], list] = defaultdict(
        lambda: [0, Decimal("0.00")]
    )
    series_stats: dict[tuple[str, str], dict] = {}
    source_stats = new_source_stats()

    for event in iter_online_retail_sales(archive_path, source_stats):
        product_id = event["product_id"]
        country = event["country"]
        business_day = date.fromisoformat(event["business_date"])
        key = (product_id, country)
        day_key = (product_id, country, business_day)
        daily_sales[day_key][0] += event["quantity"]
        daily_sales[day_key][1] += Decimal(str(event["revenue"]))

        stats = series_stats.setdefault(
            key,
            {
                "invoice_ids": set(),
                "active_dates": set(),
                "units": 0,
                "first_date": business_day,
                "last_date": business_day,
            },
        )
        stats["invoice_ids"].add(event["invoice_id"])
        stats["active_dates"].add(business_day)
        stats["units"] += event["quantity"]
        stats["first_date"] = min(stats["first_date"], business_day)
        stats["last_date"] = max(stats["last_date"], business_day)

    qualified = {
        key: stats
        for key, stats in series_stats.items()
        if len(stats["active_dates"]) >= MIN_ACTIVE_DAYS
        and len(stats["invoice_ids"]) >= MIN_INVOICES
        and stats["units"] >= MIN_UNITS
        and (stats["last_date"] - stats["first_date"]).days >= MIN_SPAN_DAYS
    }
    if not qualified:
        raise ValueError(
            "No product/country series met the current forecast-readiness "
            "thresholds. Lower ONLINE_RETAIL_MIN_ACTIVE_DAYS, "
            "ONLINE_RETAIL_MIN_INVOICES, ONLINE_RETAIL_MIN_UNITS, or "
            "ONLINE_RETAIL_MIN_SPAN_DAYS and retry."
        )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    row_count = 0
    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=[
                "date",
                "product_id",
                "store_id",
                "category",
                "region",
                "demand",
                "revenue",
            ],
        )
        writer.writeheader()

        for (product_id, country), stats in sorted(qualified.items()):
            current_day = stats["first_date"]
            while current_day <= stats["last_date"]:
                quantity, revenue = daily_sales.get(
                    (product_id, country, current_day),
                    (0, Decimal("0.00")),
                )
                writer.writerow(
                    {
                        "date": current_day.isoformat(),
                        "product_id": product_id,
                        # Existing model APIs use this key; for this dataset it is Country.
                        "store_id": country,
                        "category": "Unclassified",
                        "region": country,
                        "demand": quantity,
                        "revenue": f"{revenue:.2f}",
                    }
                )
                row_count += 1
                current_day += timedelta(days=1)

    result = {
        **source_stats,
        "eligible_product_country_series": len(qualified),
        "daily_training_rows": row_count,
    }
    print(f"Daily training data saved: {output_path}")
    print(f"Eligible product/country series: {len(qualified):,}")
    print(f"Daily rows written: {row_count:,}")
    print(f"Sale lines used: {source_stats['sale_events']:,}")
    print(
        "Cancellation/return/adjustment rows excluded: "
        f"{source_stats['cancellations_skipped'] + source_stats['returns_or_adjustments_skipped']:,}"
    )
    print(f"Missing/invalid rows skipped: {source_stats['invalid_rows_skipped']:,}")
    return result


if __name__ == "__main__":
    create_training_dataset()
