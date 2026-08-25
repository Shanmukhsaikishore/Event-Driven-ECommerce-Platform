import json

from confluent_kafka import Producer

from app.config.settings import settings

producer = Producer(
    {
        "bootstrap.servers": settings.kafka_bootstrap_servers,
    }
)


event = {
    "event_id": "22222222-2222-4222-8222-222222222222",
    "event_type": "PaymentSucceeded",
    "order_id": "b171a7f6-2869-4b2a-8366-6844bab30126",
    "customer_id": 1,
    "product_id": 1,
    "quantity": 1,
    "total_amount": 100,
}

producer.produce(
    topic="payment",
    value=json.dumps(event),
)

producer.flush()

print("Test event published")
print(json.dumps(event, indent=2))