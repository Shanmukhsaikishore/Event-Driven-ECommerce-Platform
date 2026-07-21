import json
import threading

from confluent_kafka import Consumer

from app.core.logger import logger
from app.db.database import SessionLocal
from app.kafka.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    PAYMENT_TOPIC,
    ORDER_CONSUMER_GROUP,
)
from app.repositories.order_repository import OrderRepository


consumer = Consumer(
    {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": ORDER_CONSUMER_GROUP,
        "auto.offset.reset": "earliest",
    }
)

consumer.subscribe([PAYMENT_TOPIC])

repository = OrderRepository()


def consume_messages():
    logger.info("Order Consumer Started...")
    db = SessionLocal()

    try:
        while True:

            msg = consumer.poll(1.0)

            if msg is None:
                continue

            if msg.error():
                logger.error(msg.error())
                continue

            event = json.loads(msg.value().decode("utf-8"))

            print("=" * 60)
            print("Received Event:")
            print(event)
            print("=" * 60)

            if event["event_type"] != "PaymentSucceeded":
                continue

            order = repository.get_by_order_id(
                db,
                event["order_id"],
            )

            if order is None:
                logger.error("Order not found")
                continue

            repository.update_status(
                db,
                order,
                "COMPLETED",
            )

            logger.info(f"Order {order.order_id} marked COMPLETED")

    except Exception as e:
        logger.exception(e)

    finally:
        db.close()
        consumer.close()

