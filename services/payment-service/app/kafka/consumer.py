import json
import threading

from confluent_kafka import Consumer

from app.core.logger import logger
from app.db.database import SessionLocal
from app.kafka.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    INVENTORY_TOPIC,
    PAYMENT_TOPIC,
    PAYMENT_CONSUMER_GROUP,
)
from app.kafka.producer import publish
from app.models.payment import Payment
from app.repositories.payment_repository import PaymentRepository


consumer = Consumer(
    {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": PAYMENT_CONSUMER_GROUP,
        "auto.offset.reset": "earliest",
    }
)

consumer.subscribe([INVENTORY_TOPIC])

payment_repository = PaymentRepository()


def consume_messages():
    logger.info("Payment Consumer Started...")
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

            payment = Payment(
                order_id=event["order_id"],
                amount=event["total_amount"],
                status="SUCCESS",
            )

            payment_repository.create(db, payment)

            payment_event = {
                "event_type": "PaymentSucceeded",
                "order_id": event["order_id"],
                "customer_id": event["customer_id"],
                "product_id": event["product_id"],
                "quantity": event["quantity"],
                "total_amount": event["total_amount"],
            }

            publish(PAYMENT_TOPIC, payment_event)

            logger.info("PaymentSucceeded published")

    except Exception as e:
        logger.exception(e)

    finally:
        db.close()
        consumer.close()

