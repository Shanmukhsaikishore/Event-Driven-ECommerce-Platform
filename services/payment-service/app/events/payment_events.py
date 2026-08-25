from pydantic import BaseModel,Field
from uuid import uuid4

class InventoryReservedEvent(BaseModel):
    event_type: str
    event_id:str
    order_id: str
    customer_id: int
    product_id: int
    quantity: int
    total_amount: int


class PaymentSucceededEvent(BaseModel):
    event_type: str = "PaymentSucceeded"
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    order_id: str
    customer_id: int
    product_id: int
    quantity: int
    total_amount: int