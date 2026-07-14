from decimal import Decimal

from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    description: str
    price: Decimal


class ProductResponse(ProductCreate):
    id: int

    model_config = {
        "from_attributes": True
    }

class ProductUpdate(ProductCreate):
    pass