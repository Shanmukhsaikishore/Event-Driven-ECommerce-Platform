from pydantic import BaseModel


class InventoryReservedEvent(BaseModel):
    event_type: str = "InventoryReserved"

    order_id: str
    product_id: int
    customer_id: int
    quantity: int
    total_amount: int


class InventoryFailedEvent(BaseModel):
    event_type: str = "InventoryFailed"

    order_id: str
    product_id: int
    customer_id: int
    total_amount: int 
    reason: str