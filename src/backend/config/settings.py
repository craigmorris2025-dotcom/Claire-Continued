"""
Application Settings — loaded from .env via pydantic-settings.
Single source of truth for all configuration.
"""
import os
from functools import lru_cache
from typing import List

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:
    # Fallback if pydantic-settings not installed yet
    class BaseSettings:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
            self._load_env()
        def _load_env(self):
            for attr in dir(self):
                if attr.startswith("_"):
                    continue
                env_key = f"CLAIRE_{attr.upper()}"
                env_val = os.environ.get(env_key)
                if env_val is not None:
                    current = getattr(self, attr, None)
                    if isinstance(current, int):
                        setattr(self, attr, int(env_val))
                    elif isinstance(current, bool):
                        setattr(self, attr, env_val.lower() in ("true", "1", "yes"))
                    else:
                        setattr(self, attr, env_val)
    def Field(default=None, **kwargs):
        return default


class Settings(BaseSettings):
    """All application settings with env var overrides."""

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    env: str = "development"
    log_level: str = "INFO"
    debug: bool = False

    # Database
    db_path: str = "data/claire.db"

    # Paths
    data_dir: str = "data"
    output_dir: str = "output"
    log_dir: str = "logs"

    # Security
    secret_key: str = "change-me-in-production"
    cors_origins: str = "*"

    # Connectors (for Connected / Hybrid mode)
    market_api_key: str = ""
    patent_api_key: str = ""
    financial_api_key: str = ""

    # Engine tuning
    engine_timeout_seconds: int = 30
    max_input_length: int = 50000
    min_input_length: int = 3

    class Config:
        env_prefix = "CLAIRE_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.env == "production"


@lru_cache()
def get_settings() -> Settings:
    """Cached singleton settings instance."""
    # Try loading dotenv
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    return Settings()
