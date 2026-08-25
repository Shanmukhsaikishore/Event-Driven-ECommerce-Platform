import json

from confluent_kafka import Consumer

from app.core.logger import logger
from app.db.database import SessionLocal
from app.kafka.config import (
    GROUP_ID,
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_ORDER_TOPIC,
)
from app.events.inventory_events import OrderCreatedEvent
from app.services.inventory_service import InventoryService


consumer = Consumer(
    {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": GROUP_ID,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False
    }
)

consumer.subscribe([KAFKA_ORDER_TOPIC])

inventory_service = InventoryService()


def consume_orders():

    logger.info("Inventory Consumer Started...")

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


        event = OrderCreatedEvent(**event_data)

        logger.info(
            f"Received OrderCreated for Order {event.order_id}"
        )

        db = SessionLocal()

        try:
            event_type=event.event_type

            if event_type=="OrderCreated":

                inventory_service.process_order(
                    db=db,
                    event_id=event.event_id,
                    event_type=event.event_type,
                    order_id=event.order_id,
                    customer_id=event.customer_id,
                    product_id=event.product_id,
                    quantity=event.quantity,
                    total_amount=event.total_amount,
                )

                logger.info(
                    f"Processed OrderCreated for "
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
                "Inventory processing failed"
            )

        finally:
            db.close()