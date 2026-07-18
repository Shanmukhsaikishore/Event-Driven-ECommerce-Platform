from sqlalchemy.orm import Session

from app.models.inventory import Inventory


class InventoryRepository:

    def get_by_product_id(
        self,
        db: Session,
        product_id: int
    ) -> Inventory | None:

        return (
            db.query(Inventory)
            .filter(Inventory.product_id == product_id)
            .first()
        )

    def reserve_stock(
        self,
        db: Session,
        inventory: Inventory,
        quantity: int
    ) -> None:

        inventory.available_quantity -= quantity
        inventory.reserved_quantity += quantity

        db.commit()
        db.refresh(inventory)