from sqlalchemy.orm import Session

from app.events.inventory_events import (
    InventoryFailedEvent,
    InventoryReservedEvent,
)
from app.kafka.config import KAFKA_INVENTORY_TOPIC
from app.kafka.producer import publish_event
from app.repositories.inventory_repository import InventoryRepository
from app.models.processed_event import ProcessedEvent
from app.repositories.processed_event_repository import ProcessedEventRepository


class InventoryService:

    def __init__(self):
        self.repository = InventoryRepository()
        self.processed_event_repository=ProcessedEventRepository()

    def process_order(
        self,
        db: Session,
        event_id:str,
        event_type:str,
        order_id: str,
        customer_id: int,
        product_id: int,
        quantity: int,
        total_amount: int,
    ):
      
        try:
            # 1. Check whether this exact event was already processed
            processed_event = (
                self.processed_event_repository.get_by_event_id(
                    db,
                    event_id,
                )
            )
            if processed_event is not None:
                return 
            
            inventory = self.repository.get_by_product_id(
                db=db,
                product_id=product_id,
            )

            if inventory is None:

                event = InventoryFailedEvent(
                    order_id=order_id,
                    customer_id=customer_id,
                    product_id=product_id,
                    total_amount=total_amount,
                    reason="Product not found in inventory",
                )

                publish_event(
                    KAFKA_INVENTORY_TOPIC,
                    event.model_dump(),
                )

                return

            if inventory.available_quantity < quantity:

                event = InventoryFailedEvent(
                    order_id=order_id,
                    customer_id=customer_id,
                    product_id=product_id,
                    total_amount=total_amount,
                    reason="Insufficient Stock",
                )

                publish_event(
                    KAFKA_INVENTORY_TOPIC,
                    event.model_dump(),
                )

                return

            self.repository.reserve_stock(
                db=db,
                inventory=inventory,
                quantity=quantity,
            )

            event = InventoryReservedEvent(
                order_id=order_id,
                customer_id=customer_id,
                product_id=product_id,
                quantity=quantity,
                total_amount=total_amount,
            )

            publish_event(
                KAFKA_INVENTORY_TOPIC,
                event.model_dump(),
            )

            processed_event = ProcessedEvent(
                event_id=event_id,
                event_type=event_type,
                order_id=order_id,
            )

            self.processed_event_repository.create(
                db,
                processed_event,
            )

            db.commit()
        except Exception:
            db.rollback()
            raise