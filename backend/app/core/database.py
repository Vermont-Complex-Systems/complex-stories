"""
Database configuration for Complex Stories backend with PostgreSQL and MongoDB
Using SQLAlchemy 2.0+ with async support for PostgreSQL and pymongo for MongoDB
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from typing import Optional, AsyncGenerator
import logging
from pymongo import MongoClient

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    pass


class Database:
    engine: Optional[object] = None
    async_session: Optional[async_sessionmaker] = None
    mongo_client: Optional[MongoClient] = None


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
    """Connect to PostgreSQL and MongoDB on startup"""
    try:
        # PostgreSQL connection
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

        # Test the PostgreSQL connection
        async with database.engine.begin() as conn:
            await conn.execute(text("SELECT 1"))

        logger.info("Successfully connected to PostgreSQL")

        # MongoDB connection (optional)
        try:
            from .config import settings
            database.mongo_client = MongoClient(settings.mongodb_uri)

            # Test the MongoDB connection
            database.mongo_client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
        except Exception as mongo_error:
            logger.warning(f"MongoDB connection failed: {mongo_error}")
            logger.warning("Continuing without MongoDB - MongoDB endpoints will be unavailable")
            database.mongo_client = None

    except Exception as e:
        logger.error(f"Failed to connect to databases: {e}")
        raise


async def close_database_connection():
    """Close PostgreSQL and MongoDB connections on shutdown"""
    if database.engine:
        await database.engine.dispose()
        logger.info("Disconnected from PostgreSQL")

    if database.mongo_client:
        database.mongo_client.close()
        logger.info("Disconnected from MongoDB")


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


def get_mongo_client():
    """Get the MongoDB client"""
    if not database.mongo_client:
        raise RuntimeError("MongoDB not available - connection failed during startup")
    return database.mongo_client


# MongoDB database caching for performance
_mongo_db_cache = {}

def get_wikimedia_db():
    """
    Get cached wikimedia database reference with optimizations.

    This reduces the overhead of repeatedly getting the database reference
    and allows us to apply database-level optimizations.
    """
    if "wikimedia" not in _mongo_db_cache:
        client = get_mongo_client()
        db = client.get_database("wikimedia")

        # Set read preference for analytics workloads
        # Using secondary preferred for better read performance
        from pymongo import ReadPreference
        db = db.with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)

        _mongo_db_cache["wikimedia"] = db
        logger.info("Cached wikimedia database with analytics optimizations")

    return _mongo_db_cache["wikimedia"]


def get_optimized_collection(db, collection_name: str, query_type: str = "analytics"):
    """
    Get MongoDB collection with optimizations based on query type.

    Args:
        db: MongoDB database instance
        collection_name: Name of the collection
        query_type: Type of queries ("analytics", "search", "aggregation")

    Returns:
        Optimized collection instance
    """
    collection = db.get_collection(collection_name)

    # Apply collection-level optimizations based on query type
    if query_type == "analytics":
        # For analytical queries, hint common indexes and batch size
        from pymongo import ReadPreference
        collection = collection.with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED,
            read_concern={"level": "majority"}
        )
    elif query_type == "search":
        # For search queries, prioritize low latency
        collection = collection.with_options(
            read_preference=ReadPreference.PRIMARY_PREFERRED
        )

    return collection