import json

from confluent_kafka import Consumer

from app.core.logger import logger
from app.db.database import SessionLocal
from app.kafka.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    SHIPMENT_TOPIC,
    NOTIFICATION_CONSUMER_GROUP,
)
from app.services.notification_service import NotificationService


consumer = Consumer(
    {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": NOTIFICATION_CONSUMER_GROUP,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
    }
)

consumer.subscribe([
    SHIPMENT_TOPIC,
])

notification_service = NotificationService()


def consume_messages():

    logger.info(
        "Notification Consumer Started..."
    )

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

            if event_type == "ShipmentCreated":

                notification_service.handle_shipment_created(
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

                db.close()
                continue

            consumer.commit(
                message=msg,
                asynchronous=False,
            )

            logger.info(
                f"Kafka offset committed for "
                f"{event_type} "
                f"event_id={event['event_id']}"
            )

        except Exception:

            logger.exception(
                "Notification event processing failed"
            )

        finally:
            db.close()