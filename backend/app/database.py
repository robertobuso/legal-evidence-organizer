from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import DATABASE_URL

# Convert SQLite URL to async version
ASYNC_DATABASE_URL = DATABASE_URL.replace('sqlite:///', 'sqlite+aiosqlite:///')

# Create async engine
engine = create_async_engine(
    ASYNC_DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in ASYNC_DATABASE_URL else {}
)

# SessionLocal factory
AsyncSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, 
    class_=AsyncSession
)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()