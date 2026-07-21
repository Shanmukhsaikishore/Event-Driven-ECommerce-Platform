from sqlalchemy.orm import Session

from app.models.order import Order
from app.schemas.order import OrderCreate


class OrderRepository:

    def create(self, db: Session, order: OrderCreate) -> Order:

        total_amount = order.quantity * order.unit_price

        db_order = Order(
            customer_id=order.customer_id,
            product_id=order.product_id,
            quantity=order.quantity,
            unit_price=order.unit_price,
            total_amount=total_amount,
            status="PENDING_PAYMENT"
        )

        db.add(db_order)
        db.commit()
        db.refresh(db_order)

        return db_order
    
    def get_by_order_id(self, db: Session, order_id: str):

        return (
            db.query(Order)
            .filter(Order.order_id == order_id)
            .first()
        )
    
    def update_status(
        self,
        db: Session,
        order: Order,
        status: str,
    ):

        order.status = status

        db.commit()

        db.refresh(order)

        return order