"""
Text processing utilities with semantic chunking
"""

import re
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings


class TextProcessor:
    """Text preprocessing and semantic chunking utilities"""

    def __init__(self):
        """Initialize text processor with semantic splitter"""
        self.semantic_splitter = RecursiveCharacterTextSplitter(
            separators=settings.SEMANTIC_SEPARATORS,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            is_separator_regex=False,
        )

    async def preprocess(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove special characters that might cause issues
        text = text.encode("utf-8", "ignore").decode("utf-8")

        return text.strip()

    async def split_into_chunks(
        self,
        text: str,
        max_size: int = None,
        overlap: int = None,
        strategy: str = "hierarchical",
    ) -> List[str]:
        """
        Split text into semantic chunks using intelligent splitting

        Args:
            text: Text to split
            max_size: Maximum chunk size in characters (uses config if None)
            overlap: Overlap between chunks (uses config if None)
            strategy: Summarization strategy to determine chunk size

        Returns:
            List of semantically coherent text chunks
        """
        # Use strategy-specific chunk size if not provided
        if max_size is None:
            if strategy == "detailed":
                max_size = settings.DETAILED_CHUNK_SIZE
            else:
                max_size = settings.HIERARCHICAL_CHUNK_SIZE

        if overlap is None:
            overlap = settings.CHUNK_OVERLAP

        # Ensure overlap is not larger than chunk_size
        if overlap >= max_size:
            overlap = max_size // 2  # Max 50% overlap

        # Clean text first
        text = await self.preprocess(text)

        # Create splitter with current parameters
        splitter = RecursiveCharacterTextSplitter(
            separators=settings.SEMANTIC_SEPARATORS,
            chunk_size=max_size,
            chunk_overlap=overlap,
            length_function=len,
            is_separator_regex=False,
        )

        # Split text semantically
        chunks = splitter.split_text(text)

        # Log chunking result
        avg_size = sum(len(c) for c in chunks) // len(chunks) if chunks else 0
        print(
            f"[TEXT_PROCESSOR] Chunking completed - {len(chunks)} chunks, avg_size: {avg_size} chars"
        )

        return chunks

    async def split_into_chunks_by_tokens(
        self, text: str, max_tokens: int = 25000, overlap_tokens: int = 250
    ) -> List[str]:
        """
        Split text into chunks by token count (more accurate for LLMs)

        ⚠️ DEPRECATED: Use split_into_chunks() instead for better performance.

        This method has high memory consumption for large texts because it
        encodes all tokens at once. The split_into_chunks() method uses
        RecursiveCharacterTextSplitter which is much more memory-efficient.

        Memory limits:
        - Safe for texts < 50K characters
        - Avoid for texts > 200K characters (will raise ValueError)

        Args:
            text: Text to split
            max_tokens: Maximum tokens per chunk
            overlap_tokens: Overlap tokens between chunks

        Returns:
            List of text chunks sized by tokens

        Raises:
            ValueError: If text exceeds 200K characters
        """
        import warnings

        from app.services.token_manager import TokenManager

        # Warn about deprecation
        if len(text) > 100_000:
            warnings.warn(
                f"split_into_chunks_by_tokens() is inefficient for large texts ({len(text):,} chars). "
                f"Consider using split_into_chunks() instead for better memory efficiency.",
                DeprecationWarning,
                stacklevel=2,
            )

        # Clean text first
        text = await self.preprocess(text)

        # Use token manager for splitting (will raise ValueError if text too large)
        token_manager = TokenManager(model=settings.LLM_MODEL)
        chunks = token_manager.chunk_by_tokens(
            text, chunk_size=max_tokens, overlap=overlap_tokens
        )

        return chunks

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Simple sentence splitter
        For production, consider using nltk or spacy
        """
        # Split on common sentence endings
        sentences = re.split(r"(?<=[.!?])\s+", text)

        # Filter out empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    async def count_words(self, text: str) -> int:
        """Count words in text"""
        return len(text.split())

    async def estimate_reading_time(
        self, text: str, words_per_minute: int = 200
    ) -> int:
        """Estimate reading time in minutes"""
        word_count = await self.count_words(text)
        return max(1, word_count // words_per_minute)
