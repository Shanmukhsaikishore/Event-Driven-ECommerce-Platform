from uuid import uuid4

from sqlalchemy.orm import Session

from app.events.shipment_events import ShipmentCreatedEvent
from app.kafka.config import KAFKA_SHIPMENT_TOPIC
from app.kafka.producer import publish_event
from app.models.shipment import Shipment
from app.repositories.shipment_repository import ShipmentRepository
from app.repositories.processed_event_repository import ProcessedEventRepository
from app.models.processed_event import ProcessedEvent

class ShipmentService:

    def __init__(self):
        self.repository = ShipmentRepository()
        self.processed_event_repository = ProcessedEventRepository()

    def create_shipment(
        self,
        db: Session,
        event_id:str,
        event_type:str,
        order_id: str,
        customer_id:int
    ) -> Shipment:
        
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

            tracking_number = f"TRK-{uuid4().hex[:8].upper()}"

            shipment = Shipment(
                order_id=order_id,
                tracking_number=tracking_number,
            )

            created_shipment = self.repository.create(
                db,
                shipment,
            )

            event = ShipmentCreatedEvent(
                order_id=created_shipment.order_id,
                customer_id=customer_id,
                shipment_id=created_shipment.shipment_id,
                tracking_number=created_shipment.tracking_number,
                status=created_shipment.status,
            )

            publish_event(
                KAFKA_SHIPMENT_TOPIC,
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

