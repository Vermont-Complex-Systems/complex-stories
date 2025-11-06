import duckdb
from functools import lru_cache
from ..core.config import settings

class DuckDBClient:
    def __init__(self):
        self.conn = None
    
    def connect(self):
        if self.conn is None:
            # self.conn = duckdb.connect('/netfiles/compethicslab/scisciDB/duckdb_temp/eda.duckdb')
            self.conn = duckdb.connect()
            
            # self.conn.execute("INSTALL postgres;")
            # self.conn.execute("LOAD postgres;")
            
            # Attach Postgres (https://duckdb.org/docs/stable/core_extensions/postgres)
            # allows DuckDB to directly read and write data from a running PostgreSQL database instance.
            self.conn.execute(f"""
            ATTACH 'dbname=complex_stories host=localhost user=jstonge1 password={settings.postgres_password}' 
                AS pg (TYPE postgres, READ_ONLY);
            """)

            # Attach DuckLake (https://duckdb.org/docs/stable/core_extensions/ducklake)
            # add support for attaching to postgreSQL stored in the DuckLake format
            # Catalogs are stored in postgreSQL, duckdb client, and storage use parquet files on netfiles.
            # Users can run multiple DuckLake clients and connect concurrently to the catalog database – 
            # to work over the same DuckLake dataset.
            self.conn.execute("""
                ATTACH 'ducklake:postgres:dbname=complex_stories host=localhost user=jstonge1' AS scisciDB
                (DATA_PATH '/netfiles/compethicslab/scisciDB/');
            """)
            
            self.conn.execute("USE scisciDB;")
        return self.conn
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

@lru_cache()
def get_duckdb_client():
    return DuckDBClient()