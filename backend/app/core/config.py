from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_name: str = "Complex Stories API"
    debug: bool = False
    version: str = "0.1.0"

    # CORS settings
    allowed_origins: List[str] = ["http://localhost:5173", "http://localhost:5176", "http://localhost:3000", "https://complexstories.uvm.edu"]

    # PostgreSQL Database settings
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "complex_stories"
    postgres_user: str = "postgres"
    postgres_password: str = ""

    # Label Studio settings
    label_studio_url: str = ""
    label_studio_api_key: str = ""
    faculty_project_id: str = "42"
    department_project_id: str = ""

    fastapi_admin_token: str = ""

    mongodb_uri: str
    mongodb_uri_old: str
    
    s2_api_key: str
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Security
    secret_key: str = "your-secret-key-here"
    admin_token: str = "fake-super-secret-token"
    admin_username: str = "admin"
    admin_password: str = "admin123"

    # External APIs
    api_base: str = "http://localhost:8000"
    s2_api_key: str = ""
    
    sciscidb_data_root: str = ""
    s2_data_root: str = ""
    oa_data_root: str = ""
    
    duckdb_path: str = ""
    duckdb_temp: str = ""

    postgres_uri: str = ""
    mongodb_uri_old: str = ""

    # Data pipeline settings
    data_output_path: str = "../frontend/static/data"
    pipeline_schedule_interval: str = "0 6 * * *"  # Daily at 6 AM

    class Config:
        env_file = ".env"


settings = Settings()