"""
Pydantic models for request/response schemas
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class UserLogin(BaseModel):
    """User login request"""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserCreate(BaseModel):
    """User registration request"""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email: Optional[str] = None


class Token(BaseModel):
    """JWT token response"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class SummaryRequest(BaseModel):
    """Text summarization request"""

    text: str = Field(
        ...,
        min_length=100,
        max_length=300000,
        description="Text to summarize (100 - 300K characters)",
    )
    strategy: Literal["hierarchical", "simple", "detailed"] = Field(
        default="hierarchical", description="Summarization strategy"
    )
    compression_ratio: float = Field(
        default=0.20,
        ge=0.05,
        le=0.50,
        description="Target summary size as percentage of original (0.05 to 0.50)",
    )

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate text content"""
        if not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")

        # Additional validation for length
        text_length = len(v.strip())
        if text_length > 300000:
            raise ValueError(
                f"Text exceeds maximum length of 300,000 characters. "
                f"Current length: {text_length:,} characters. "
                f"Please reduce text size."
            )

        return v.strip()


class SummaryResponse(BaseModel):
    """Text summarization response"""

    summary: str
    original_length: int
    summary_length: int
    compression_ratio: float
    strategy_used: str
    processing_time: Optional[float] = None


class ErrorResponse(BaseModel):
    """Error response"""

    detail: str
    error_code: Optional[str] = None
