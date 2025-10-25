from dagster_duckdb import DuckDBResource
import dagster as dg
from typing import Optional
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

from shared.clients.label_studio import LabelStudioClient
from shared.clients.semantic_scholar import SemanticScholarClient

logger = dg.get_dagster_logger()

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
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
        conn.execute("CREATE SCHEMA IF NOT EXISTS transform")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS raw.gscholar_venues (
                source VARCHAR,
                venue VARCHAR,
                field VARCHAR,
                h5_index INTEGER,
                h5_median INTEGER,
                
                PRIMARY KEY (venue)
            )
        """)

        logger.info("DuckDB schema initialized successfully.")

# We use duckdb as our working space
database_resource = InitDuckDBResource(
    database='~/data_luminosity.duckdb'
)

class MongoDBResource(dg.ConfigurableResource):
    """MongoDB connection resource for papersDB"""
    
    def get_client(self) -> MongoClient:
        """Get MongoDB client instance"""
        return MongoClient(os.getenv('MONGODB_URI_OLD'))
    
    def get_database(self):
        """Get database instance"""
        client = self.get_client()
        return client['papersDB']

class LabelStudioResource(dg.ConfigurableResource):
    """Label Studio client resource with MongoDB dependency"""
    api_token: str = os.environ.get("LS_TOK")
    mongodb: dg.ResourceDependency[MongoDBResource]
    
    @property
    def database(self):
        """Get database instance from MongoDB resource"""
        return self.mongodb.get_database()
    
    def get_client(self) -> LabelStudioClient:
        return LabelStudioClient(
            api_token=self.api_token,
            database=self.database  # Pass database instead of resource
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

# Create resource instances
mongodb_resource = MongoDBResource()

@dg.definitions  
def resources():
    return dg.Definitions(
        resources={
            "duckdb": database_resource,
            "mongodb": mongodb_resource,
            "s2_resource": SemanticScholarResource(),
            "ls_resource": LabelStudioResource(
                mongodb=mongodb_resource  # This should pass the actual resource instance
            )
        }
    )