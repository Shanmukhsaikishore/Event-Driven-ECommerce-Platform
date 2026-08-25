from contextlib import asynccontextmanager
import threading

from fastapi import FastAPI

from app.config.settings import settings
from app.db.database import create_tables, engine
from app.kafka.consumer import consume_messages


@asynccontextmanager
async def lifespan(app: FastAPI):

    create_tables()

    consumer_thread = threading.Thread(
        target=consume_messages,
        daemon=True,
    )

    consumer_thread.start()

    yield


app = FastAPI(
    title="Notification Service",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def health_check():

    with engine.connect() as connection:
        connection.execute(
            __import__("sqlalchemy").text("SELECT 1")
        )

    return {
        "message": "Notification Service is running",
        "database": settings.database_name,
        "status": "Database Connected",
    }