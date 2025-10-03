#!/usr/bin/env python3
"""
Simple script to clear the papers table manually
"""
import asyncio
from app.core.database import connect_to_database, close_database_connection, get_db_session
from sqlalchemy import text

async def clear_papers_table():
    """Clear the papers table manually"""
    try:
        # Connect to database
        await connect_to_database()
        print("Connected to database")

        # Get session and clear table
        async for db in get_db_session():
            print("Clearing papers table...")
            await db.execute(text("TRUNCATE TABLE papers RESTART IDENTITY CASCADE"))
            await db.commit()
            print("✅ Papers table cleared successfully!")
            break

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await close_database_connection()
        print("Database connection closed")

if __name__ == "__main__":
    asyncio.run(clear_papers_table())