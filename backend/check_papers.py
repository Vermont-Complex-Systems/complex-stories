#!/usr/bin/env python3
"""
Simple script to check the papers table
"""
import asyncio
from app.core.database import connect_to_database, close_database_connection, get_db_session
from sqlalchemy import text

async def check_papers_table():
    """Check the papers table"""
    try:
        await connect_to_database()

        async for db in get_db_session():
            # Count records
            result = await db.execute(text("SELECT COUNT(*) FROM papers"))
            count = result.scalar()
            print(f"📊 Papers in table: {count}")

            # Show a few sample records if any exist
            if count > 0:
                result = await db.execute(text("""
                    SELECT id, ego_display_name, title, publication_year
                    FROM papers
                    LIMIT 3
                """))
                records = result.fetchall()
                print("\n📄 Sample records:")
                for record in records:
                    print(f"  - {record.ego_display_name}: {record.title[:50]}... ({record.publication_year})")

            break

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await close_database_connection()

if __name__ == "__main__":
    asyncio.run(check_papers_table())