
#!/usr/bin/env python3
"""
Deduplicate databases
"""
import argparse
from pathlib import Path
import sys
import duckdb
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

def create_oa_works_deduped(conn):
    """Create deduplicated OpenAlex works view with best record per DOI."""
    logger.info("Creating deduplicated oa_works view...")
    conn.execute("""
        CREATE OR REPLACE VIEW oa_works_deduped AS
        SELECT * FROM (
            SELECT *,
                ROW_NUMBER() OVER (
                    PARTITION BY doi 
                    ORDER BY 
                        CASE WHEN doi_registration_agency = 'crossref' THEN 1 ELSE 2 END,
                        concepts_count DESC NULLS LAST,
                        topics_count DESC NULLS LAST,
                        id
                ) as rn
            FROM oa_works
            WHERE doi IS NOT NULL
        ) ranked
        WHERE rn = 1;
    """)
    
    # Get stats
    original = conn.execute("SELECT COUNT(*) FROM oa_works WHERE doi IS NOT NULL").fetchone()[0]
    deduped = conn.execute("SELECT COUNT(*) FROM oa_works_deduped").fetchone()[0]
    removed = original - deduped
    logger.info(f"Deduplicated: {original:,} → {deduped:,} works (removed {removed:,} duplicates)")