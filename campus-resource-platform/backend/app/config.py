"""
Configuration module for the Campus Resource Platform.
Loads environment variables and provides app-wide settings.
"""

import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_ENV: str = "development"
    APP_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # IBM Cloudant
    CLOUDANT_URL: str = ""
    CLOUDANT_APIKEY: str = ""

    # CouchDB (local dev fallback)
    COUCHDB_URL: str = "http://couchdb:5984"
    COUCHDB_USER: str = "admin"
    COUCHDB_PASSWORD: str = "password"

    # JWT
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production-please"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60

    # IBM Cloud Object Storage
    COS_ENDPOINT: str = ""
    COS_API_KEY: str = ""
    COS_INSTANCE_ID: str = ""
    COS_BUCKET_NAME: str = "campus-resources"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def use_cloudant(self) -> bool:
        """Use IBM Cloudant in production, CouchDB locally."""
        return bool(self.CLOUDANT_URL and self.CLOUDANT_APIKEY)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
