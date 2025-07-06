from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./tmsiti.db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    frontend_url: str = "https://tmsiti.uz"
    allowed_hosts: List[str] = ["tmsiti.uz", "*.tmsiti.uz", "localhost", "127.0.0.1"]
    
    # API
    api_v1_str: str = "/api"
    project_name: str = "TMSITI Backend API"
    
    # Email
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = "your-email@gmail.com"
    smtp_password: str = "your-app-password"
    
    # Application
    app_version: str = "1.0.0"
    debug: bool = False
    redis_url: str = "redis://localhost:6379/0"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

settings = Settings()