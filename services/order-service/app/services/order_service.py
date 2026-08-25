from sqlalchemy.orm import Session

from app.kafka.config import KAFKA_ORDER_TOPIC
from app.kafka.producer import publish_event
from app.models.order import Order
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate
from app.events.order_events import OrderCreatedEvent
from app.clients.product_client import ProductClient
from app.models.processed_event import ProcessedEvent
from app.repositories.processed_event_repository import ProcessedEventRepository
from uuid import uuid4

class OrderService:

    def __init__(self):
        self.repository = OrderRepository()
        self.processed_event_repository = ProcessedEventRepository()

    async def create_order(
        self,
        db: Session,
        order: OrderCreate,
    ) -> Order:

        product = await ProductClient.get_product(
            order.product_id
        )

        unit_price = product["unit_price"]

        total_amount = unit_price * order.quantity

        db_order = Order(
            customer_id=order.customer_id,
            product_id=order.product_id,
            quantity=order.quantity,
            unit_price=unit_price,
            total_amount=total_amount,
            status="PENDING_PAYMENT",
        )

        created_order = self.repository.create(
            db,
            db_order,
        )

        event = OrderCreatedEvent(
            order_id= created_order.order_id,
            customer_id= created_order.customer_id,
            product_id=created_order.product_id,
            quantity=created_order.quantity,
            total_amount= float(created_order.total_amount),
        )

        publish_event(
            KAFKA_ORDER_TOPIC,
            event.model_dump(),
        )

        return created_order
    
    def handle_payment_succeeded(
        self,
        db: Session,
        event: dict,
    ) -> None:

        event_id = event["event_id"]
        event_type = event["event_type"]
        order_id = event["order_id"]

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

            # 2. Find the order
            order = self.repository.get_by_order_id(
                db,
                order_id,
            )
            if order is None:
                raise ValueError(
                    f"Order {order_id} not found"
                )

            # 3. Apply the business operation if necessary
            if order.status == "PENDING_PAYMENT":

                self.repository.update_status(
                    db,
                    order,
                    "PAYMENT_SUCCESS",
                )

            elif order.status != "PAYMENT_SUCCESS":

                raise ValueError(
                    f"Cannot process PaymentSucceeded for "
                    f"Order {order_id} in status {order.status}"
                )

            # 4. Record the event as successfully processed
            processed_event = ProcessedEvent(
                event_id=event_id,
                event_type=event_type,
                order_id=order_id,
            )

            self.processed_event_repository.create(
                db,
                processed_event,
            )

            # 5. Commit business operation + processed event together
            db.commit()

        except Exception:
            db.rollback()
            raise

    def handle_shipment_created(
    self,
    db: Session,
    event: dict,
) -> None:

        event_id = event["event_id"]
        event_type = event["event_type"]
        order_id = event["order_id"]

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

            # 2. Find the order
            order = self.repository.get_by_order_id(
                db,
                order_id,
            )

            if order is None:
                raise ValueError(
                    f"Order {order_id} not found"
                )

            # 3. Apply the business operation if necessary
            if order.status == "PAYMENT_SUCCESS":

                self.repository.update_status(
                    db,
                    order,
                    "COMPLETED",
                )

            elif order.status != "COMPLETED":

                raise ValueError(
                    f"Cannot process ShipmentCreated for "
                    f"Order {order_id} in status {order.status}"
                )

            # 4. Record the event as successfully processed
            processed_event = ProcessedEvent(
                event_id=event_id,
                event_type=event_type,
                order_id=order_id,
            )

            self.processed_event_repository.create(
                db,
                processed_event,
            )

            # 5. Commit both operations atomically
            db.commit()

        except Exception:
            db.rollback()
            raise