from pydantic import BaseModel


class ShipmentCreatedEvent(BaseModel):
    event_id: str
    event_type: str
    order_id: str
    customer_id: int
    shipment_id: str
    tracking_number: str
    status: str