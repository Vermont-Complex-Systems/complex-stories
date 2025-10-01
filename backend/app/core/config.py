from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_name: str = "Complex Stories API"
    debug: bool = False
    version: str = "0.1.0"

    # CORS settings
    allowed_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Database settings (for future use)
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "complex_stories"

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