import json

from app.db.database import SessionLocal
from app.repositories.inventory_repository import InventoryRepository
from app.events.inventory_events import (
    InventoryReservedEvent,
    InventoryFailedEvent,
)
from app.kafka.config import KAFKA_INVENTORY_TOPIC
from app.kafka.producer import publish

from confluent_kafka import Consumer
from app.core.logger import logger

from app.kafka.config import (
    GROUP_ID,
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_ORDER_TOPIC,
)


consumer = Consumer(
    {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": GROUP_ID,
        "auto.offset.reset": "earliest",
    }
)

consumer.subscribe([KAFKA_ORDER_TOPIC])


def consume_orders():
    logger.info("Inventory Consumer Started...")

    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            print(msg.error())
            continue

        event = json.loads(msg.value().decode("utf-8"))

        logger.info(f"Received Event: {event}")

        db = SessionLocal()

        try:
            repository = InventoryRepository()

            inventory = repository.get_by_product_id(
                db=db,
                product_id=event["product_id"]
            )

            if inventory is None:
                print(f"Product {event['product_id']} not found in inventory.")
                continue

            quantity = event["quantity"]

            if inventory.available_quantity < quantity:
                event = InventoryFailedEvent(
                    order_id=event["order_id"],
                    customer_id=event["customer_id"],
                    product_id=event["product_id"],
                    total_amount= event["total_amount"],
                    reason="Insufficient Stock"
                )

                publish(
                    KAFKA_INVENTORY_TOPIC,
                    event.model_dump()
                )
                logger.info("InventoryFailed event published")


                continue

            repository.reserve_stock(
                db=db,
                inventory=inventory,
                quantity=quantity
            )

            event = InventoryReservedEvent(
                order_id=event["order_id"],
                customer_id=event["customer_id"],
                product_id=event["product_id"],
                quantity=quantity,
                total_amount= event["total_amount"]
            )

            publish(
                KAFKA_INVENTORY_TOPIC,
                event.model_dump()
            )

            logger.info("InventoryReserved event published")

        except Exception:
            logger.exception("Inventory consumer failed")

        finally:
            db.close()

        
