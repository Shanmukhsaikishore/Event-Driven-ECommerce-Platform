from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        default=lambda: str(uuid4())
    )

    customer_id: Mapped[int] = mapped_column(Integer)

    product_id: Mapped[int] = mapped_column(Integer)

    quantity: Mapped[int] = mapped_column(Integer)

    unit_price: Mapped[float] = mapped_column(
        Numeric(10, 2)
    )

    total_amount: Mapped[float] = mapped_column(
        Numeric(10, 2)
    )

    status: Mapped[str] = mapped_column(
        String(30)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )