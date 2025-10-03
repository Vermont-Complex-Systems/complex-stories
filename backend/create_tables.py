#!/usr/bin/env python3
"""
Database table creation script for Complex Stories backend.

This script creates all the necessary tables in PostgreSQL.
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the backend directory to the Python path
import sys
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import connect_to_database, get_engine, close_database_connection
from app.models import Base


async def create_tables():
    """Create all database tables."""
    try:
        print("🔌 Connecting to PostgreSQL...")
        await connect_to_database()

        engine = get_engine()

        print("📋 Creating database tables...")
        async with engine.begin() as conn:
            # Create all tables defined in models
            await conn.run_sync(Base.metadata.create_all)

        print("✅ Database tables created successfully!")

        # List created tables
        async with engine.begin() as conn:
            result = await conn.exec_driver_sql("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = result.fetchall()

            print(f"\n📊 Created tables:")
            for table in tables:
                print(f"  - {table[0]}")

    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise
    finally:
        await close_database_connection()


async def drop_tables():
    """Drop all database tables (for development)."""
    try:
        print("🔌 Connecting to PostgreSQL...")
        await connect_to_database()

        engine = get_engine()

        print("🗑️  Dropping database tables...")
        async with engine.begin() as conn:
            # Drop all tables
            await conn.run_sync(Base.metadata.drop_all)

        print("✅ Database tables dropped successfully!")

    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        raise
    finally:
        await close_database_connection()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Manage Complex Stories database tables")
    parser.add_argument("--drop", action="store_true", help="Drop all tables instead of creating them")
    args = parser.parse_args()

    if args.drop:
        asyncio.run(drop_tables())
    else:
        asyncio.run(create_tables())