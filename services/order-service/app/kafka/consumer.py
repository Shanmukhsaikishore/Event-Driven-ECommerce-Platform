import json

from confluent_kafka import Consumer

from app.core.logger import logger
from app.db.database import SessionLocal
from app.kafka.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    PAYMENT_TOPIC,
    SHIPMENT_TOPIC,
    ORDER_CONSUMER_GROUP,
)
from app.services.order_service import OrderService


consumer = Consumer(
    {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": ORDER_CONSUMER_GROUP,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
    }
)

consumer.subscribe([
    PAYMENT_TOPIC,
    SHIPMENT_TOPIC,
])

order_service = OrderService()


def consume_messages():

    logger.info("Order Consumer Started...")

    while True:

        msg = consumer.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            logger.error(msg.error())
            continue

        event = json.loads(
            msg.value().decode("utf-8")
        )

        logger.info(
            f"Received {event.get('event_type')} "
            f"for Order {event.get('order_id')}"
        )

        db = SessionLocal()

        try:

            event_type = event.get("event_type")

            if event_type == "PaymentSucceeded":

                order_service.handle_payment_succeeded(
                    db,
                    event,
                )

                logger.info(
                    f"Processed PaymentSucceeded for "
                    f"Order {event['order_id']}"
                )

            elif event_type == "ShipmentCreated":

                order_service.handle_shipment_created(
                    db,
                    event,
                )

                logger.info(
                    f"Processed ShipmentCreated for "
                    f"Order {event['order_id']}"
                )

            else:

                logger.warning(
                    f"Unknown event type: {event_type}"
                )

                # Do not commit unknown events yet.
                continue

            # DB transaction has successfully committed
            # inside the OrderService handler.
            #
            # Only now commit the Kafka offset.
            consumer.commit(
                message=msg,
                asynchronous=False,
            )

            logger.info(
                f"Kafka offset committed for "
                f"{event_type} "
                f"event_id={event.get('event_id')}"
            )

        except Exception:

            logger.exception(
                "Order event processing failed"
            )

            # IMPORTANT:
            # No Kafka offset commit happens here.
            #
            # The message remains eligible for redelivery.

        finally:

            db.close()