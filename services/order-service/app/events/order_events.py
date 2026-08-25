from pydantic import BaseModel,Field
from uuid import uuid4

class OrderCreatedEvent(BaseModel):
    event_type: str = "OrderCreated"
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    order_id: str
    product_id: int
    customer_id: int
    quantity: int
    total_amount: int


