"""
Application settings configuration.

Loads settings from environment variables with defaults.
"""

import os
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Ontology settings
    URI_ONTOLOGIA: str = "https://w3id.org/OntoExhibit#" # kept as sensible default

    # Virtuoso settings
    VIRTUOSO_URL: str
    DEFAULT_GRAPH_URL: str = ""
    VIRTUOSO_USER: str = "dba"
    VIRTUOSO_PASSWORD: str = ""  # Must be provided by env

    # CORS - comma-separated list of allowed origins
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,https://complexhibit.uma.es"
    
    # App config
    PROJECT_NAME: str = "Complexhibit API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = ""
    DEPLOY_PATH: str = ""
    
    # User service URL (optional)
    USER_SERVICE_URL: str = ""
    
    # Database (PostgreSQL for auth)
    DATABASE_URL: str = ""  # Must be provided by env
    
    # JWT Auth
    JWT_SECRET: str = ""    # Must be provided by env
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    
    # Admin
    ADMIN_EMAIL: str = ""    # Must be provided by env (notification recipient)
    ADMIN_PASSWORD: str = "" # Must be provided by env
    # Auto-seeded admins: "email:pass,email:pass" (split each entry on the FIRST ':')
    ADMIN_USERS: str = ""

    # Password reset
    PASSWORD_RESET_EXPIRE_MINUTES: int = 60
    
    # SMTP Email
    SMTP_HOST: str = ""      # Must be provided by env
    SMTP_PORT: int = 587
    SMTP_USER: str = ""      # Must be provided by env
    SMTP_PASSWORD: str = ""  # Must be provided by env
    SMTP_FROM: str = ""      # Must be provided by env
    
    # Frontend URL (for email links)
    FRONTEND_URL: str = ""   # Must be provided by env

    @field_validator("VIRTUOSO_URL", "DATABASE_URL", "JWT_SECRET")
    @classmethod
    def _required_non_empty(cls, value: str, info) -> str:
        """Fail fast at startup if a critical secret/config is missing or blank.

        NOTE: VIRTUOSO_PASSWORD is intentionally NOT required — read-only SPARQL
        queries hit the public endpoint without auth, and the deployment only sets
        VIRTUOSO_DBA_PASSWORD (for the Virtuoso container itself).
        """
        if not value or not str(value).strip():
            raise ValueError(
                f"Required setting '{info.field_name}' must be provided via environment "
                f"and cannot be empty."
            )
        return value

    @property
    def cors_origins_list(self) -> List[str]:
        """Parsed list of allowed CORS origins."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
