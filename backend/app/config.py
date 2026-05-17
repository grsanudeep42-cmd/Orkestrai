"""
Configuration management for OrkestrAI backend
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator, model_validator, ValidationError


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "OrkestrAI"
    VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = ""

    # Groq AI
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # AI Provider routing
    PROVIDER_PRIORITY: str = "bob,groq,gemini,openrouter,openai"
    PROVIDER_TIMEOUT: int = 120 # seconds
    
    # Database Pool Settings
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # OpenRouter
    OPENROUTER_API_KEY: str = ""

    # Gemini
    GEMINI_API_KEY: str = ""

    # OpenAI
    OPENAI_API_KEY: str = ""

    # Bob AI
    BOB_API_KEY: str = ""

    # GitHub Integration
    GITHUB_TOKEN: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_REDIRECT_URI: str = "http://localhost:8000/api/v1/github/callback"

    # Security
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Environment
    ENVIRONMENT: str = "development"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)

    @model_validator(mode="after")
    def validate_required_fields(self) -> "Settings":
        """Validate required environment variables at startup."""
        missing = []

        if not self.DATABASE_URL:
            missing.append("DATABASE_URL")

        if not self.SECRET_KEY:
            missing.append("SECRET_KEY")

        if missing:
            raise ValueError(
                f"Missing required environment variables:\n" + "\n".join(f"  - {m}" for m in missing)
            )

        return self

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Made with Bob
