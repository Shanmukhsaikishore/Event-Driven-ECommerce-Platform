from sqlalchemy.orm import Session

from app.models.shipment import Shipment


class ShipmentRepository:

    def create(
        self,
        db: Session,
        shipment: Shipment,
    ) -> Shipment:

        db.add(shipment)
        db.commit()
        db.refresh(shipment)

        return shipment