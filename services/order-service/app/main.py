from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.config.settings import settings
from app.db.database import create_tables, engine
from app.api.order_routes import router as order_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="Order Service",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(order_router)

@app.get("/")
def health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
    "message": "Order Service is running",
    "database": settings.database_name,
    "status": "Database Connected"
    }