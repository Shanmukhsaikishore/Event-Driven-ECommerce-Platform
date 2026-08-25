from fastapi import FastAPI

from app.api.gateway_routes import router

app = FastAPI(title="API Gateway")

app.include_router(router)