from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import OrderService

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

service = OrderService()


@router.post(
    "",
    response_model=OrderResponse,
    status_code=201
)
async def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db)
):
    order= await service.create_order(db, order)
    return order