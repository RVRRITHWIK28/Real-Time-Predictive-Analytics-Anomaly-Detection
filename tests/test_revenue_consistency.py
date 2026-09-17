import pandas as pd
from decimal import Decimal, ROUND_HALF_UP


FILE = "data/raw/anomalous_transactions.csv"


def calculate_expected_revenue(row):
    quantity = Decimal(str(row["quantity"]))
    unit_price = Decimal(str(row["unit_price"]))
    discount = Decimal(str(row["discount"]))

    revenue = (
        quantity
        * unit_price
        * (Decimal("1") - discount)
    )

    return revenue.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


def main():
    df = pd.read_csv(FILE)

    mismatches = 0

    for _, row in df.iterrows():

        expected = calculate_expected_revenue(row)

        actual = Decimal(
            str(row["revenue"])
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        if expected != actual:
            mismatches += 1

    print("=" * 60)
    print("REVENUE CONSISTENCY VALIDATION")
    print("=" * 60)
    print(f"Transactions checked : {len(df)}")
    print(f"Revenue mismatches   : {mismatches}")
    print("=" * 60)


if __name__ == "__main__":
    main()