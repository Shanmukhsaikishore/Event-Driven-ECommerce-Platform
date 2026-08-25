from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.processed_event import ProcessedEvent
from app.repositories.notification_repository import (
    NotificationRepository,
)
from app.repositories.processed_event_repository import (
    ProcessedEventRepository,
)


class NotificationService:

    def __init__(self):
        self.repository = NotificationRepository()
        self.processed_event_repository = (
            ProcessedEventRepository()
        )

    def handle_shipment_created(
        self,
        db: Session,
        event: dict,
    ) -> None:

        event_id = event["event_id"]
        event_type = event["event_type"]
        order_id = event["order_id"]
        customer_id = event["customer_id"]

        try:

            # 1. Check idempotency
            processed_event = (
                self.processed_event_repository.get_by_event_id(
                    db,
                    event_id,
                )
            )

            if processed_event is not None:
                return

            # 2. Create notification
            notification = Notification(
                order_id=order_id,
                customer_id=customer_id,
                type="ORDER_SHIPPED",
                message=(
                    f"Your order has been shipped. "
                    f"Tracking number: "
                    f"{event['tracking_number']}"
                ),
                status="SENT",
            )

            self.repository.create(
                db,
                notification,
            )

            # 3. Record processed event
            processed_event = ProcessedEvent(
                event_id=event_id,
                event_type=event_type,
                order_id=order_id,
            )

            self.processed_event_repository.create(
                db,
                processed_event,
            )

            # 4. Atomic commit
            db.commit()

        except Exception:
            db.rollback()
            raise