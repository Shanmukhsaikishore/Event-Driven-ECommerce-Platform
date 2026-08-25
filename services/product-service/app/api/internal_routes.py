from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.internal_product import ProductForOrderResponse
from app.services.product_service import ProductService


router = APIRouter(prefix="/internal", tags=["Internal"])


@router.get(
    "/products/{product_id}",
    response_model=ProductForOrderResponse,
)
def get_product_for_order(
    product_id: int,
    db: Session = Depends(get_db),
):


    product = ProductService.get_product_for_order(db,product_id)

    return ProductForOrderResponse(
        product_id=product.id,
        product_name=product.name,
        unit_price=product.price,
    )