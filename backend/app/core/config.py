from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_name: str = "Complex Stories API"
    debug: bool = False
    version: str = "0.1.0"

    # CORS settings
    allowed_origins: List[str] = ["http://localhost:5173", "http://localhost:3000", "https://complexstories.uvm.edu"]

    # PostgreSQL Database settings
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "complex_stories"
    postgres_user: str = "postgres"
    postgres_password: str = ""

    label_studio_api_key: str
    label_studio_url: str
    faculty_project_id: int
    department_project_id: int
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Security
    secret_key: str = "your-secret-key-here"
    admin_token: str = "fake-super-secret-token"

    # Data pipeline settings
    data_output_path: str = "../frontend/static/data"
    pipeline_schedule_interval: str = "0 6 * * *"  # Daily at 6 AM

    class Config:
        env_file = ".env"


settings = Settings()