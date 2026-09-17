from src.streaming.consumer import create_consumer


consumer = create_consumer()

print("Waiting for transactions...")

for message in consumer:
    print("Received transaction:")
    print(message.value)
    break

consumer.close()

print("Consumer test completed successfully!")