import json

from confluent_kafka import Producer

from app.kafka.config import KAFKA_BOOTSTRAP_SERVERS


producer = Producer(
    {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS
    }
)


def delivery_report(err, msg):
    if err:
        print(err)
    else:
        print(
            f"Published to {msg.topic()} "
            f"[{msg.partition()}] "
            f"Offset {msg.offset()}"
        )


def publish(topic: str, event: dict):

    producer.produce(
        topic=topic,
        value=json.dumps(event),
        callback=delivery_report
    )

    producer.flush()