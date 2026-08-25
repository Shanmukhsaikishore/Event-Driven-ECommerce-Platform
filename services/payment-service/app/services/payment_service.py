from sqlalchemy.orm import Session

from app.events.payment_events import PaymentSucceededEvent
from app.kafka.config import PAYMENT_TOPIC
from app.kafka.producer import publish_event
from app.models.payment import Payment
from app.repositories.payment_repository import PaymentRepository
from app.repositories.processed_event_repository import ProcessedEventRepository
from app.models.processed_event import ProcessedEvent

class PaymentService:

    def __init__(self):
        self.repository = PaymentRepository()
        self.processed_event_repository = ProcessedEventRepository()


    def process_payment(
        self,
        db: Session,
        event_id:str,
        event_type:str,
        order_id: str,
        customer_id: int,
        product_id: int,
        quantity: int,
        total_amount: int,
    ) -> Payment:
        
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

            payment = Payment(
                order_id=order_id,
                amount=total_amount,
                status="SUCCESS",
            )

            created_payment = self.repository.create(
                db,
                payment,
            )

            event = PaymentSucceededEvent(
                order_id=order_id,
                customer_id=customer_id,
                product_id=product_id,
                quantity=quantity,
                total_amount=total_amount,
            )

            publish_event(
                PAYMENT_TOPIC,
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

