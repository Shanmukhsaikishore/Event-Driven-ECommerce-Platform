from pydantic import BaseModel


class ProductForOrderResponse(BaseModel):
    product_id: int
    product_name: str
    unit_price: float