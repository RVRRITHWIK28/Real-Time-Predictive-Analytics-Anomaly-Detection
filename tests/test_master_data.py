from src.ingestion.master_data import PRODUCTS, STORES, CUSTOMERS


print("MASTER DATA VALIDATION")
print("=" * 50)

print(f"Number of products  : {len(PRODUCTS)}")
print(f"Number of stores    : {len(STORES)}")
print(f"Number of customers : {len(CUSTOMERS)}")

print("\nFirst product:")
print(PRODUCTS[0])

print("\nFirst store:")
print(STORES[0])

print("\nFirst five customers:")
print(CUSTOMERS[:5])

print("\nLast customer:")
print(CUSTOMERS[-1])

print("\nMaster data loaded successfully!")