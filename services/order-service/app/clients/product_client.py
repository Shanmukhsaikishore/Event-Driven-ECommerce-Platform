import httpx
from fastapi import HTTPException

from app.config.settings import settings


class ProductClient:

    @staticmethod
    async def get_product(product_id: int):

        try:

            async with httpx.AsyncClient(timeout=5.0) as client:

                response = await client.get(
                    f"{settings.PRODUCT_SERVICE_URL}/internal/products/{product_id}"
                )

                response.raise_for_status()

                return response.json()

        except httpx.HTTPStatusError as exc:

            if exc.response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail="Product not found"
                )

            raise HTTPException(
                status_code=502,
                detail="Unexpected response from Product Service"
            )

        except (
            httpx.ConnectError,
            httpx.TimeoutException,
            httpx.RequestError,
        ):

            raise HTTPException(
                status_code=503,
                detail="Product Service is unavailable"
            )