from contextlib import asynccontextmanager

import threading

from fastapi import FastAPI
from sqlalchemy import text

from app.config.settings import settings
from app.db.database import create_tables, engine
from app.kafka.consumer import consume_messages
from app.kafka.producer import producer


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()

    thread = threading.Thread(target=consume_messages,daemon=True,)
    thread.start()

    yield

    producer.flush()
    producer.close()


app = FastAPI(
    title="Shipment Service",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "message": "Shipment Service is running",
        "database": settings.database_name,
        "status": "Database Connected",
    }