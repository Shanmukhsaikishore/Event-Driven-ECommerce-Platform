import json

from confluent_kafka import Producer

from app.core.logger import logger
from app.kafka.config import KAFKA_BOOTSTRAP_SERVERS


producer = Producer(
    {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
    }
)


def delivery_report(err, msg):
    if err:
        logger.error(f"Delivery failed: {err}")
    else:
        logger.info(
            f"Message delivered to {msg.topic()} [{msg.partition()}]"
        )


def publish_event(
    topic: str,
    event: dict,
):
    producer.produce(
        topic,
        json.dumps(event).encode("utf-8"),
        callback=delivery_report,
    )

    