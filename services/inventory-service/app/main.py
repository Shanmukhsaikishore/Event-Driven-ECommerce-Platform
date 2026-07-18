from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.config.settings import settings
from app.db.database import create_tables, engine

import threading

from app.kafka.consumer import consume_orders
from app.kafka.producer import producer
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()

    consumer_thread = threading.Thread(
        target=consume_orders,
        daemon=True
    )
    consumer_thread.start()

    yield

    producer.flush()
    producer.close()



app = FastAPI(
    title="Inventory Service",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
    "message": "Inventory Service is running",
    "database": settings.database_name,
    "status": "Database Connected"
    }