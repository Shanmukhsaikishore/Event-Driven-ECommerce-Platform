from datetime import datetime

from pydantic import BaseModel


class ShipmentResponse(BaseModel):
    shipment_id: str
    order_id: str
    tracking_number: str
    status: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }