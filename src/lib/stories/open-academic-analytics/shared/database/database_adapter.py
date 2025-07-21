"""
database_adapter.py

Adapter to make Dagster's DuckDBResource work with existing DatabaseExporter interface.
This preserves all your existing business logic while using the official resource.
"""
import logging
import pandas as pd

logger = logging.getLogger(__name__)

class DatabaseExporterAdapter:
    """
    Adapter that wraps DuckDB connection to provide the same interface as DatabaseExporter.
    This allows us to use Dagster's official DuckDB resource without changing business logic.
    """
    
    def __init__(self, duckdb_connection):
        """
        Initialize with a DuckDB connection from Dagster's DuckDBResource.
        
        Args:
            duckdb_connection: Connection from DuckDBResource.get_connection()
        """
        self.con = duckdb_connection
        self._setup_tables()
    
    def _setup_tables(self):
        """Set up all required database tables if they don't exist"""
        # Paper table (exact same as original DatabaseExporter)
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS paper (
                ego_aid VARCHAR,
                ego_display_name VARCHAR,
                wid VARCHAR,
                pub_date DATE,
                pub_year INT,
                doi VARCHAR,
                title VARCHAR,
                work_type VARCHAR,
                primary_topic VARCHAR,
                authors VARCHAR,
                cited_by_count INT,
                ego_position VARCHAR,
                ego_institution VARCHAR,
                PRIMARY KEY(ego_aid, wid)
            )
        """)
        
        # Coauthor table (exact same as original DatabaseExporter)
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS coauthor2 (
                ego_aid VARCHAR,
                pub_date DATE,
                pub_year INT,
                coauthor_aid VARCHAR,
                coauthor_name VARCHAR,
                acquaintance VARCHAR,
                yearly_collabo INT,
                all_times_collabo INT,
                shared_institutions VARCHAR,
                coauthor_institution VARCHAR,
                PRIMARY KEY(ego_aid, coauthor_aid, pub_year)
            )
        """)
        
        # Author info table (exact same as original DatabaseExporter)
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS author (
                aid VARCHAR,
                display_name VARCHAR,
                institution VARCHAR,
                pub_year INT,
                first_pub_year INT,
                last_pub_year INT,
                PRIMARY KEY(aid, pub_year)
            )
        """)
    
    def load_existing_paper_data(self, cache_file):
        """
        Load existing data from parquet file into database if it exists.
        
        Args:
            cache_file (Path): Path to the parquet file containing existing data
        """
        if cache_file.exists():
            df_pap = pd.read_parquet(cache_file)
            # Insert existing data, ignoring conflicts since table might already have data
            self.con.execute("INSERT INTO paper SELECT * FROM df_pap ON CONFLICT DO NOTHING")
            logger.info(f"Loaded {len(df_pap)} existing papers from {cache_file}")
    
    def load_existing_author_data(self, cache_file):
        """
        Load existing data from parquet file into database if it exists.
        
        Args:
            cache_file (Path): Path to the parquet file containing existing data
        """
        if cache_file.exists():
            df_author = pd.read_parquet(cache_file)
            # Insert existing data, ignoring conflicts since table might already have data
            self.con.execute("INSERT INTO author SELECT * FROM df_author ON CONFLICT DO NOTHING")
            logger.info(f"Loaded {len(df_author)} existing authors from {cache_file}")
    
    def load_existing_coauthor_data(self, cache_file):
        """
        Load existing data from parquet file into database if it exists.
        
        Args:
            cache_file (Path): Path to the parquet file containing existing data
        """
        if cache_file.exists():
            df_coauthor = pd.read_parquet(cache_file)
            # Insert existing data, ignoring conflicts since table might already have data
            self.con.execute("INSERT INTO coauthor2 SELECT * FROM df_coauthor ON CONFLICT DO NOTHING")
            logger.info(f"Loaded {len(df_coauthor)} existing coauthors from {cache_file}")
    
    def get_author_cache_by_name(self, author_name):
        """
        Get existing database records for a given author name.
        EXACT SAME interface as original DatabaseExporter
        
        Args:
            author_name (str): OpenAlex display name
            
        Returns:
            dict or None: First matching author record as dict, None if not found
        """
        df = self.con.execute(
            "SELECT * FROM author WHERE display_name = ?",
            (author_name,)
        ).fetch_df()
        
        return df.iloc[0].to_dict() if not df.empty else None

    def get_author_cache(self, author_id):
        """
        Get existing database records for a given author ID.
        EXACT SAME interface as original DatabaseExporter
        
        Args:
            author_id (str): OpenAlex author ID
            
        Returns:
            tuple: (paper_cache, coauthor_cache)
        """
        paper_cache = self.con.execute(
            "SELECT ego_aid, wid FROM paper WHERE ego_aid = ?", 
            (author_id,)
        ).fetchall()
        
        coauthor_cache = self.con.execute(
            "SELECT ego_aid, coauthor_aid, pub_year FROM coauthor2 WHERE ego_aid = ?", 
            (author_id,)
        ).fetchall()
        
        return paper_cache, coauthor_cache
    
    def is_up_to_date(self, author_id, min_year, max_year):
        """
        Check if the database records for an author are up to date.
        EXACT SAME interface as original DatabaseExporter
        
        Args:
            author_id (str): OpenAlex author ID
            min_year (int): First publication year
            max_year (int): Latest publication year
            
        Returns:
            bool: True if up to date, False otherwise
        """
        # Get date range from database
        min_query = "SELECT MIN(pub_year) FROM paper WHERE ego_aid = ?"
        max_query = "SELECT MAX(pub_year) FROM paper WHERE ego_aid = ?"
        
        min_db = self.con.execute(min_query, (author_id,)).fetchone()
        max_db = self.con.execute(max_query, (author_id,)).fetchone()
        
        # If no data in DB or NULL values, not up to date
        if not min_db or not max_db or min_db[0] is None or max_db[0] is None:
            return False
        
        # Check if ranges match
        return min_db[0] <= min_year and max_db[0] >= max_year
    
    def save_papers(self, papers):
        """
        Save paper data to the database.
        EXACT SAME interface as original DatabaseExporter
        
        Args:
            papers (list): List of paper tuples
        """
        if not papers:
            return
            
        try:
            self.con.executemany("""
                INSERT INTO paper
                (ego_aid, ego_display_name, wid, pub_date, pub_year, doi, title, work_type, 
                primary_topic, authors, cited_by_count, ego_position, ego_institution)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (ego_aid, wid)
                DO UPDATE SET
                    work_type = COALESCE(EXCLUDED.work_type, paper.work_type),
                    primary_topic = COALESCE(EXCLUDED.primary_topic, paper.primary_topic)
            """, papers)
            self.con.commit()
        except Exception as e:
            logger.error(f"Error saving papers to database: {str(e)}")
            self.con.rollback()
    
    def save_coauthors(self, coauthors):
        """
        Save coauthor data to the database.
        EXACT SAME interface as original DatabaseExporter
        
        Args:
            coauthors (list): List of coauthor tuples
        """
        if not coauthors:
            return
            
        try:
            self.con.executemany("""
                INSERT INTO coauthor2
                (ego_aid, pub_date, pub_year, coauthor_aid, coauthor_name, acquaintance, 
                yearly_collabo, all_times_collabo, shared_institutions, coauthor_institution)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (ego_aid, coauthor_aid, pub_year)
                DO NOTHING
            """, coauthors)
            self.con.commit()
        except Exception as e:
            logger.error(f"Error saving coauthors to database: {str(e)}")
            self.con.rollback()
    
    def save_authors(self, authors):
        """
        Save author data to the database.
        EXACT SAME interface as original DatabaseExporter
        
        Args:
            authors (list): List of author tuples
        """
        if not authors:
            return
            
        try:
            self.con.executemany("""
                INSERT INTO author
                (aid, display_name, institution, pub_year, first_pub_year, last_pub_year)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT (aid, pub_year) 
                DO UPDATE SET
                    institution = COALESCE(EXCLUDED.institution, author.institution),
                    first_pub_year = COALESCE(EXCLUDED.first_pub_year, author.first_pub_year)
            """, authors)
            self.con.commit()
        except Exception as e:
            logger.error(f"Error saving authors to database: {str(e)}")
            self.con.rollback()
    
    def update_author_ages(self, author_id, first_pub_year):
        """
        Update author ages based on a known first publication year.
        EXACT SAME interface as original DatabaseExporter
        
        Args:
            author_id (str): OpenAlex author ID
            first_pub_year (int): Corrected first publication year
        """
        try:
            # Get all author records
            author_df = self.con.execute(
                "SELECT * FROM author WHERE aid = ?", 
                (author_id,)
            ).fetch_df()
            
            if len(author_df) == 0:
                return
            
            # Update first_pub_year and recalculate author_age
            author_df['first_pub_year'] = first_pub_year
            author_df['author_age'] = author_df.pub_year - author_df.first_pub_year
            
            # Update database
            self.con.executemany("""
                INSERT INTO author
                (aid, display_name, institution, pub_year, first_pub_year, last_pub_year, author_age)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (aid, pub_year) 
                DO UPDATE SET 
                    author_age = EXCLUDED.author_age,
                    first_pub_year = EXCLUDED.first_pub_year
            """, author_df.values.tolist())
            
            # Delete records with negative author_age
            self.con.execute(
                "DELETE FROM author WHERE aid = ? AND author_age < 0", 
                (author_id,)
            )
            self.con.commit()
        except Exception as e:
            logger.error(f"Error updating author ages: {str(e)}")
            self.con.rollback()
    
    def close(self):
        """
        Close database connection.
        NOTE: With Dagster's resource, this is handled automatically,
        but we keep this method for interface compatibility.
        """
        # Connection is managed by Dagster resource, so we don't need to close manually
        pass