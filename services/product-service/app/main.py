from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.api.product_routes import router as product_router
from app.api.internal_routes import router as internal_router
from app.config.settings import settings
from app.db.database import create_tables, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="Product Service",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(product_router)
app.include_router(internal_router)

@app.get("/")
def health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "message": "Product Service is running",
        "database": settings.database_name,
        "status": "Database Connected",
    }