from sqlalchemy.orm import Session

from app.kafka.config import KAFKA_ORDER_TOPIC
from app.kafka.producer import publish_event
from app.models.order import Order
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate


class OrderService:

    def __init__(self):
        self.repository = OrderRepository()

    def create_order(self, db: Session, order: OrderCreate) -> Order:

        created_order = self.repository.create(db, order)

        event = {
            "event_type": "OrderCreated",
            "order_id": created_order.order_id,
            "customer_id": created_order.customer_id,
            "product_id": created_order.product_id,
            "quantity": created_order.quantity,
            "total_amount": float(created_order.total_amount),
        }

        publish_event(KAFKA_ORDER_TOPIC, event)

        return created_order