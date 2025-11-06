# # scripts/scisciDB/config.py
# from pathlib import Path
# from dataclasses import dataclass
# import os
# from dotenv import load_dotenv

# load_dotenv()

# @dataclass
# class Config:
#     # Paths
#     s2_data_root: Path = Path(os.getenv('S2_DATA_ROOT', '/netfiles/compethicslab/scisciDB/semanticscholar'))
#     duckdb_path: Path = Path(os.getenv('DUCKDB_PATH', '/netfiles/compethicslab/duckdb/research.duckdb'))
#     duckdb_temp: Path = Path(os.getenv('DUCKDB_TEMP', '/netfiles/compethicslab/duckdb_temp'))
    
#     # Database
#     postgres_uri: str = os.getenv('POSTGRES_URI', 'postgresql://jstonge1@localhost/complex_stories')
#     postgres_host: str = 'localhost'
#     postgres_db: str = 'complex_stories'
#     postgres_user: str = 'jstonge1'
    
#     # API
#     s2_api_key: str = os.getenv('S2_API_KEY')
    
#     # DuckDB settings
#     memory_limit: str = '35GB'
#     threads: int = 8

# config = Config()