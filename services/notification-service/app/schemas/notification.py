from pydantic import BaseModel


class NotificationResponse(BaseModel):
    notification_id: str
    order_id: str
    customer_id: int
    type: str
    message: str
    status: str

    model_config = {
        "from_attributes": True
    }