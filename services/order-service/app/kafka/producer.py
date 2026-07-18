import json

from confluent_kafka import Producer 

from app.kafka.config import KAFKA_BOOTSTRAP_SERVERS


producer = Producer(
    {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS
    }
)


def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(
            f"Message delivered to "
            f"{msg.topic()} [{msg.partition()}] "
            f"at offset {msg.offset()}"
        )


def publish_event(topic: str, event: dict):

    producer.produce(
        topic=topic,
        value=json.dumps(event),
        callback=delivery_report
    )

    producer.flush()