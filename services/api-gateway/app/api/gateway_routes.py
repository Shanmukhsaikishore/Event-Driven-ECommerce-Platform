from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.schemas.order import OrderCreate


from app.services.gateway_service import gateway_service

router = APIRouter()


@router.post("/orders")
async def create_order(order: OrderCreate):

    response, status = await gateway_service.forward_order_request(order.model_dump())

    return JSONResponse(
        content=response,
        status_code=status,
    )


