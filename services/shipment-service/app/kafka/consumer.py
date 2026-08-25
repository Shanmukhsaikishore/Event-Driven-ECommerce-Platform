import json

from confluent_kafka import Consumer

from app.core.logger import logger
from app.db.database import SessionLocal
from app.events.shipment_events import PaymentSucceededEvent
from app.kafka.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_PAYMENT_TOPIC,
    SHIPMENT_CONSUMER_GROUP,
)
from app.services.shipment_service import ShipmentService


consumer = Consumer(
    {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": SHIPMENT_CONSUMER_GROUP,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False

    }
)

consumer.subscribe([KAFKA_PAYMENT_TOPIC])

shipment_service = ShipmentService()


def consume_messages():
    logger.info("Shipment Consumer Started...")


    while True:

        msg = consumer.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            logger.error(msg.error())
            continue

        event = PaymentSucceededEvent(
            **json.loads(msg.value().decode("utf-8"))
        )

        logger.info(
            f"Received PaymentSucceeded for Order {event.order_id}"
        )
        
        db = SessionLocal()

        try:
            event_type=event.event_type

            if event_type=="PaymentSucceeded":

                shipment_service.create_shipment(
                    db=db,
                    event_id = event.event_id,
                    event_type=event.event_type,
                    order_id=event.order_id,
                    customer_id=event.customer_id
                )
                logger.info(
                    f"Processed PaymentSucceeded for "
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
                    "Shipment consumer failed"
                )

        finally:
            db.close()
