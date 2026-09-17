import pandas as pd


FILE_PATH = "data/raw/historical_transactions.csv"


print("=" * 60)
print("ML DATA INSPECTION")
print("=" * 60)


# Load dataset
df = pd.read_csv(FILE_PATH)


# Basic information
print("\nDataset shape:")
print(df.shape)


# Column names
print("\nColumns:")
print(df.columns.tolist())


# First 5 rows
print("\nFirst 5 rows:")
print(df.head())


# Data types
print("\nData types:")
print(df.dtypes)


# Missing values
print("\nMissing values:")
print(df.isnull().sum())


# Unique products
print("\nUnique products:")
print(df["product_id"].nunique())


# Unique stores
print("\nUnique stores:")
print(df["store_id"].nunique())


# Date range
print("\nTimestamp range:")
print(df["timestamp"].min())
print(df["timestamp"].max())


print("\n" + "=" * 60)
print("INSPECTION COMPLETE")
print("=" * 60)