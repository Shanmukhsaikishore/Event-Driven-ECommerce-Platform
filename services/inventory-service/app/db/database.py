from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base

from app.config.settings import settings

DATABASE_URL = (
    f"postgresql+psycopg://{settings.database_user}:"
    f"{settings.database_password}@"
    f"{settings.database_host}:"
    f"{settings.database_port}/"
    f"{settings.database_name}"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def create_tables():
    Base.metadata.create_all(bind=engine)