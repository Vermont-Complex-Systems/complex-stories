from dagster_duckdb import DuckDBResource
import dagster as dg
from typing import Optional
import os
import requests
from dotenv import load_dotenv

from shared.clients.semantic_scholar import SemanticScholarClient
from shared.clients.openalex import OpenAlexClient
from shared.clients.complex_stories_api import ComplexStoriesAPIClient
from dotenv import load_dotenv

load_dotenv()
logger = dg.get_dagster_logger()
load_dotenv()

class InitDuckDBResource(DuckDBResource):
    """A DuckDB resource that ensures schema/tables exist on initialization."""

    def get_connection(self):
        # Get the context manager from the parent
        context_manager = super().get_connection()

        # Create a custom context manager that initializes schema
        class InitializedConnection:
            def __init__(self, parent_cm, init_func):
                self.parent_cm = parent_cm
                self.init_func = init_func

            def __enter__(self):
                conn = self.parent_cm.__enter__()
                self.init_func(conn)
                return conn

            def __exit__(self, exc_type, exc_val, exc_tb):
                return self.parent_cm.__exit__(exc_type, exc_val, exc_tb)

        return InitializedConnection(context_manager, self._init_schema)

    def _init_schema(self, conn):
        """Run DDL or initialization SQL once (idempotent)."""
        logger.info("Initializing open-academic-analytics DuckDB schema if necessary...")

        # Create schemas
        conn.execute("CREATE SCHEMA IF NOT EXISTS oa.raw")
        conn.execute("CREATE SCHEMA IF NOT EXISTS oa.cache")
        conn.execute("CREATE SCHEMA IF NOT EXISTS oa.transform")

        # Publications table - one record per unique work
        conn.execute("""
            CREATE TABLE IF NOT EXISTS oa.raw.publications (
                id VARCHAR PRIMARY KEY,
                doi VARCHAR,
                title VARCHAR,
                display_name VARCHAR,
                publication_year INTEGER,
                publication_date DATE,
                language VARCHAR,
                type VARCHAR,
                type_crossref VARCHAR,

                -- Metrics
                cited_by_count INTEGER,
                fwci DOUBLE,
                has_fulltext BOOLEAN,
                fulltext_origin VARCHAR,
                is_retracted BOOLEAN,
                is_paratext BOOLEAN,

                -- Nested structures as STRUCTs
                ids STRUCT(
                    openalex VARCHAR,
                    doi VARCHAR,
                    mag VARCHAR,
                    pmid VARCHAR,
                    pmcid VARCHAR
                ),

                primary_location STRUCT(
                    is_oa BOOLEAN,
                    landing_page_url VARCHAR,
                    pdf_url VARCHAR,
                    source STRUCT(
                        id VARCHAR,
                        display_name VARCHAR,
                        type VARCHAR
                    ),
                    license VARCHAR,
                    version VARCHAR,
                    is_accepted BOOLEAN,
                    is_published BOOLEAN
                ),

                open_access STRUCT(
                    is_oa BOOLEAN,
                    oa_status VARCHAR,
                    oa_url VARCHAR,
                    any_repository_has_fulltext BOOLEAN
                ),

                primary_topic STRUCT(
                    id VARCHAR,
                    display_name VARCHAR,
                    score DOUBLE
                ),

                biblio STRUCT(
                    volume VARCHAR,
                    issue VARCHAR,
                    first_page VARCHAR,
                    last_page VARCHAR
                ),

                -- Arrays as VARCHAR for now
                concepts VARCHAR,
                topics VARCHAR,
                keywords VARCHAR,
                mesh VARCHAR,
                referenced_works VARCHAR,
                related_works VARCHAR,

                -- Counts
                countries_distinct_count INTEGER,
                institutions_distinct_count INTEGER,
                locations_count INTEGER,
                referenced_works_count INTEGER,

                -- Metadata
                updated_date TIMESTAMP,
                created_date DATE,

                -- UVM Professor tracking
                ego_author_id VARCHAR  -- ego_author_id from uvm_profs_2023 if this is a UVM publication
            )
        """)

        # Authorships table - many records per work (one per author)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS oa.raw.authorships (
                work_id VARCHAR,
                author_id VARCHAR,
                author_display_name VARCHAR,
                author_position VARCHAR,  -- first, middle, last
                institutions VARCHAR,     -- JSON array of author's institutions for this work
                raw_affiliation_strings VARCHAR,
                is_corresponding BOOLEAN,

                PRIMARY KEY (work_id, author_id)
            )
        """)

        # UVM professors sync status cache
        conn.execute("""
            CREATE TABLE IF NOT EXISTS oa.cache.uvm_profs_sync_status (
                ego_author_id VARCHAR PRIMARY KEY,
                last_synced_date TIMESTAMP,
                paper_count INTEGER,
                needs_update BOOLEAN DEFAULT TRUE,
                prof_data_last_updated TIMESTAMP  -- Track when professor data was last modified
            )
        """)

        # Coauthor cache table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS oa.cache.coauthor_cache (
                id VARCHAR PRIMARY KEY,
                display_name VARCHAR,
                first_pub_year INTEGER,
                last_pub_year INTEGER,
                last_fetched_date TIMESTAMP,
                fetch_successful BOOLEAN DEFAULT FALSE
            )
        """)

        # Embeddings table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS oa.raw.embeddings (
                doi VARCHAR PRIMARY KEY,
                paperId VARCHAR,
                title VARCHAR,
                abstract VARCHAR,
                fieldsOfStudy VARCHAR,
                s2FieldsOfStudy VARCHAR,
                embedding FLOAT[],
                status VARCHAR DEFAULT 'success',
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

        # UVM professors 2023 data (for reference)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS oa.raw.uvm_profs_2023 (
                payroll_name VARCHAR,
                payroll_year INTEGER,
                host_dept VARCHAR,
                ego_author_id VARCHAR PRIMARY KEY,
                first_pub_year INTEGER,
                group_size INTEGER,
                group_url VARCHAR,
                has_research_group BOOLEAN,
                perceived_as_male BOOLEAN,
                position VARCHAR,
                notes VARCHAR,
                last_updated TIMESTAMP
            )
        """)

        logger.info("DuckDB schema initialized successfully.")

database_resource = InitDuckDBResource(
    database="~/oa.duckdb"
)

class SemanticScholarResource(dg.ConfigurableResource):
    """https://www.semanticscholar.org/product/api"""
    api_key: Optional[str] = os.environ.get('S2')
    max_requests_per_second: int = 1
    max_requests_per_day: int = 100_000
    base_url: str = "https://api.semanticscholar.org/graph/v1"
    
    def get_client(self) -> SemanticScholarClient:
        """Create and return a stateful client instance"""
        return SemanticScholarClient(
            api_key=self.api_key,
            max_requests_per_second=self.max_requests_per_second,
            max_requests_per_day=self.max_requests_per_day,
            base_url=self.base_url
        )

class OpenAlexResource(dg.ConfigurableResource):
    """https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication"""
    email: str
    max_requests_per_second: int = 10
    max_requests_per_day: int = 100_000
    base_url: str = "https://api.openalex.org"   # add base_url

    def get_client(self) -> OpenAlexClient:
        return OpenAlexClient(
            email=self.email,
            max_requests_per_second=self.max_requests_per_second,
            max_requests_per_day=self.max_requests_per_day,
            base_url=self.base_url,
        )

class ComplexStoriesAPIResource(dg.ConfigurableResource):
    """Complex Stories FastAPI client resource"""
    base_url: str = os.environ.get('API_BASE', 'https://api.complexstories.uvm.edu')
    timeout: int = 30

    def get_client(self) -> ComplexStoriesAPIClient:
        return ComplexStoriesAPIClient(
            base_url=self.base_url,
            timeout=self.timeout
        )

@dg.definitions  
def resources():
    return dg.Definitions(
        resources={
            "duckdb": database_resource,
            "oa_resource": OpenAlexResource(
                email="jonathanstonge7@gmail.com",
            ),
            "s2_resource": SemanticScholarResource(),
            "complex_stories_api": ComplexStoriesAPIResource()
        }
    )
