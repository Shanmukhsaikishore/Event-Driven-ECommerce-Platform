from pydantic import BaseModel,Field
from uuid import uuid4

class PaymentSucceededEvent(BaseModel):
    event_type: str
    event_id:str
    order_id: str
    customer_id: int


    

class ShipmentCreatedEvent(BaseModel):
    event_type: str = "ShipmentCreated"
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    customer_id: int
    order_id: str
    shipment_id: str
    tracking_number: str
    status: str