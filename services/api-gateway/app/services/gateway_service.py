import httpx

from app.config.settings import settings


class GatewayService:

    async def forward_order_request(self, payload: dict):

        async with httpx.AsyncClient() as client:

            response = await client.post(
                f"{settings.ORDER_SERVICE_URL}/orders",
                json=payload,
            )

            return response.json(), response.status_code


gateway_service = GatewayService()