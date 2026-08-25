from sqlalchemy.orm import Session

from app.models.order import Order


class OrderRepository:

    def create(
        self,
        db: Session,
        order: Order,
    ) -> Order:

        db.add(order)
        db.commit()
        db.refresh(order)

        return order

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

        db.flush()
        db.refresh(order)

        return order