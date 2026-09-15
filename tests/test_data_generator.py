from src.ingestion.data_generator import generate_transaction


print("TRANSACTION GENERATOR TEST")
print("=" * 60)

for i in range(5):
    event = generate_transaction()

    print(f"\nTransaction {i + 1}")
    print(event)

print("\nGenerator test completed successfully!")