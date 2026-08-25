from uuid import uuid4

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    shipment_id: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        default=lambda: str(uuid4()),
    )

    order_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )

    tracking_number: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="CREATED",
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )