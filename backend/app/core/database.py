"""
Database configuration for Complex Stories backend with PostgreSQL
Using SQLAlchemy 2.0+ with async support
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from typing import Optional, AsyncGenerator
import logging

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    pass


class Database:
    engine: Optional[object] = None
    async_session: Optional[async_sessionmaker] = None


database = Database()


def get_database_url() -> str:
    """Get PostgreSQL connection URL from settings"""
    from .config import settings

    # Check for full DATABASE_URL first (common in deployment)
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Convert postgres:// to postgresql+psycopg:// if needed
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
        return database_url

    # Use settings instead of os.getenv for consistency
    return f"postgresql+psycopg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"


async def connect_to_database():
    """Connect to PostgreSQL on startup"""
    try:
        database_url = get_database_url()
        logger.info(f"Connecting to PostgreSQL at {database_url.split('@')[1] if '@' in database_url else database_url}")

        database.engine = create_async_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=20,
            max_overflow=0,
            echo=False  # Set to True for SQL debugging
        )

        database.async_session = async_sessionmaker(
            database.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        # Test the connection
        async with database.engine.begin() as conn:
            await conn.execute(text("SELECT 1"))

        logger.info("Successfully connected to PostgreSQL")

    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        raise


async def close_database_connection():
    """Close PostgreSQL connection on shutdown"""
    if database.engine:
        await database.engine.dispose()
        logger.info("Disconnected from PostgreSQL")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session for dependency injection"""
    if not database.async_session:
        raise RuntimeError("Database not initialized")

    async with database.async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_engine():
    """Get the current database engine"""
    return database.engine