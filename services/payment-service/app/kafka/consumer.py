import json

from confluent_kafka import Consumer

from app.core.logger import logger
from app.db.database import SessionLocal
from app.events.payment_events import InventoryReservedEvent
from app.kafka.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    INVENTORY_TOPIC,
    PAYMENT_CONSUMER_GROUP,
)
from app.services.payment_service import PaymentService


consumer = Consumer(
    {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": PAYMENT_CONSUMER_GROUP,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False
    }
)

consumer.subscribe([INVENTORY_TOPIC])

payment_service = PaymentService()


def consume_messages():

    logger.info("Payment Consumer Started...")

    while True:

        msg = consumer.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            logger.error(msg.error())
            continue

        event_data = json.loads(
            msg.value().decode("utf-8")
        )

        event = InventoryReservedEvent(**event_data)

        logger.info(
            f"Received InventoryReserved for "
            f"Order {event.order_id}"
        )

        db = SessionLocal()

        try:
            event_type=event.event_type

            if event_type=="InventoryReserved":


                payment_service.process_payment(
                    db=db,
                    event_id=event.event_id,
                    event_type=event_type,
                    order_id=event.order_id,
                    customer_id=event.customer_id,
                    product_id=event.product_id,
                    quantity=event.quantity,
                    total_amount=event.total_amount,
                )

                logger.info(
                    f"Processed InventoryReserved for "
                    f"Order {event.order_id}"
                )
            else:
                logger.warning(
                    f"Unknown event type: {event_type}"
                )

                # Do not commit unknown events yet.
                continue

            consumer.commit(
                message=msg,
                asynchronous=False,
            )

            logger.info(
                f"Kafka offset committed for "
                f"{event_type} "
                f"event_id={event.event_id}"
            )

        except Exception:
            logger.exception(
                "Payment processing failed"
            )

        finally:
            db.close()