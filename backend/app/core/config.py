"""
Application configuration
Load settings from environment variables
"""

from typing import List

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    API_TITLE: str = "Smart Summary API"
    API_VERSION: str = "1.0.0"

    # Security
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60

    # LLM Configuration
    ANTHROPIC_API_KEY: str = ""

    # LLM Provider: only "anthropic" supported
    LLM_PROVIDER: str = "anthropic"
    LLM_MODEL: str = "claude-3-5-sonnet-20241022"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 4096

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://your-app.vercel.app",
    ]

    # Text Processing
    MAX_TEXT_LENGTH: int = 300000  # 300K characters (aligned with schemas)
    MIN_TEXT_LENGTH: int = 100

    # Chunking Configuration (Semantic Splitting)
    CHUNK_SIZE: int = 100000  # Large chunks for better context
    CHUNK_OVERLAP: int = 1000  # Overlap between chunks

    # Strategy-specific chunk sizes
    HIERARCHICAL_CHUNK_SIZE: int = 100000  # ~25K tokens for Claude
    DETAILED_CHUNK_SIZE: int = 100000  # Same size for consistent chunking

    # Semantic splitting separators (in order of priority)
    SEMANTIC_SEPARATORS: List[str] = [
        "\n## ",  # Markdown H2 headers
        "\n### ",  # Markdown H3 headers
        "\n#### ",  # Markdown H4 headers
        "\n\n",  # Paragraph breaks
        "\n",  # Line breaks
        ". ",  # Sentence endings
        " ",  # Words
    ]

    # Parallel processing
    MAX_PARALLEL_CHUNKS: int = 5  # Process up to 5 chunks simultaneously

    # Extractive Summarization (Map-Reduce pipeline)
    EXTRACTIVE_ALGORITHM: str = "textrank"  # textrank, lexrank, lsa, luhn
    EXTRACTIVE_COMPRESSION_RATIO: float = 0.3  # Extract 30% of content
    EXTRACTIVE_SENTENCES_PER_CHUNK: int = 10  # Sentences to extract per chunk

    # Relevance Detection (Quality optimization)
    RELEVANCE_THRESHOLD: float = 0.5  # Minimum relevance score (0.0-1.0)
    PRIORITY_CHUNK_RATIO: float = 0.7  # Prioritize top 70% of chunks
    USE_RELEVANCE_FILTERING: bool = True  # Enable relevance-based filtering

    # Token Limits (all Claude models support 200K tokens with 90% safety margin)
    TOKEN_LIMIT: int = 180_000  # 90% of 200K

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./smart_summary.db"

    # Environment
    PYTHON_ENV: str = "development"  # ou "production"

    model_config = ConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


settings = Settings()
