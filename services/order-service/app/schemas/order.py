from decimal import Decimal

from pydantic import BaseModel


class OrderCreate(BaseModel):
    customer_id: int
    product_id: int
    quantity: int
    unit_price: Decimal


class OrderResponse(BaseModel):
    order_id: str
    customer_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    total_amount: Decimal
    status: str

    model_config = {
        "from_attributes": True
    }