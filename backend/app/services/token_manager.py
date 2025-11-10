"""
Token counting and management for Anthropic Claude models
Ensures inputs don't exceed model token limits
"""

from typing import Dict, Optional

import tiktoken


class TokenManager:
    """
    Manages token counting and truncation for Anthropic Claude models
    All Claude models support 200K tokens
    """

    # All Claude models have the same token limit
    TOKEN_LIMIT = 200_000
    ENCODING_NAME = "cl100k_base"

    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize TokenManager for Claude models

        Args:
            model: Model name (all Claude models use same limits)
        """
        self.model = model
        self.encoding = tiktoken.get_encoding(self.ENCODING_NAME)
        self.max_tokens = self.TOKEN_LIMIT

        # Safety margin (use 90% of limit to be safe)
        self.safe_max_tokens = int(self.max_tokens * 0.9)

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text for the current model

        Args:
            text: Input text to count

        Returns:
            Number of tokens
        """
        if not text:
            return 0

        try:
            tokens = self.encoding.encode(text)
            return len(tokens)
        except Exception as e:
            # Fallback: rough estimation (1 token ≈ 4 characters)
            print(f"Warning: Token counting failed, using estimation. Error: {e}")
            return len(text) // 4

    def truncate_to_limit(
        self, text: str, max_tokens: Optional[int] = None, preserve_end: bool = False
    ) -> str:
        """
        Truncate text to fit within token limit

        Args:
            text: Input text to truncate
            max_tokens: Maximum tokens (uses safe_max_tokens if not provided)
            preserve_end: If True, keep end of text; if False, keep beginning

        Returns:
            Truncated text that fits within token limit
        """
        if not text:
            return text

        target_tokens = max_tokens or self.safe_max_tokens
        current_tokens = self.count_tokens(text)

        # No truncation needed
        if current_tokens <= target_tokens:
            return text

        # Binary search for optimal truncation point
        if preserve_end:
            # Keep the end of the text
            left, right = 0, len(text)
            result = text

            while left < right:
                mid = (left + right) // 2
                candidate = text[mid:]

                if self.count_tokens(candidate) <= target_tokens:
                    result = candidate
                    right = mid
                else:
                    left = mid + 1

            # Add truncation notice
            return f"[... texto truncado ...]\n\n{result}"
        else:
            # Keep the beginning of the text (default)
            left, right = 0, len(text)
            result = text

            while left < right:
                mid = (left + right + 1) // 2
                candidate = text[:mid]

                if self.count_tokens(candidate) <= target_tokens:
                    result = candidate
                    left = mid
                else:
                    right = mid - 1

            # Add truncation notice
            return f"{result}\n\n[... texto truncado ...]"

    def get_token_info(self, text: str) -> Dict[str, any]:
        """
        Get detailed token information for text

        Args:
            text: Input text to analyze

        Returns:
            Dictionary with token stats
        """
        token_count = self.count_tokens(text)

        return {
            "model": self.model,
            "token_count": token_count,
            "max_tokens": self.max_tokens,
            "safe_max_tokens": self.safe_max_tokens,
            "within_limit": token_count <= self.safe_max_tokens,
            "usage_percentage": round((token_count / self.safe_max_tokens) * 100, 2),
            "needs_truncation": token_count > self.safe_max_tokens,
            "character_count": len(text),
            "tokens_to_chars_ratio": round(token_count / len(text), 3) if text else 0,
        }

    def chunk_by_tokens(
        self, text: str, chunk_size: int = 50_000, overlap: int = 500
    ) -> list[str]:
        """
        Split text into chunks by token count (not character count)

        ⚠️ WARNING: This method loads ALL tokens into memory at once.
        For texts >100K characters, use TextProcessor.split_into_chunks() instead.

        Memory usage guide:
        - Text < 50K chars: Safe to use this method
        - Text > 50K chars: Use TextProcessor.split_into_chunks() for better efficiency
        - Text > 200K chars: MUST use TextProcessor.split_into_chunks()

        Args:
            text: Text to split
            chunk_size: Target tokens per chunk
            overlap: Overlap tokens between chunks

        Returns:
            List of text chunks

        Raises:
            ValueError: If text is too large (>200K characters)
        """
        if not text:
            return []

        # Safety check for large texts
        if len(text) > 200_000:
            raise ValueError(
                f"Text too large ({len(text):,} chars) for token-based chunking. "
                f"This method loads all tokens into memory and can cause memory overflow. "
                f"Use TextProcessor.split_into_chunks() instead for better memory efficiency."
            )

        # Encode entire text
        tokens = self.encoding.encode(text)
        total_tokens = len(tokens)

        if total_tokens <= chunk_size:
            return [text]

        # Validate overlap
        if overlap >= chunk_size:
            overlap = chunk_size // 2  # Max 50% overlap
            print(f"Warning: overlap reduced to {overlap} (was >= chunk_size)")

        chunks = []
        start = 0
        iteration_count = 0
        max_iterations = (total_tokens // (chunk_size - overlap)) + 5  # Safety margin

        while start < total_tokens:
            # Safety check for infinite loops
            iteration_count += 1
            if iteration_count > max_iterations:
                print(
                    f"Warning: Maximum iterations ({max_iterations}) reached. Breaking loop."
                )
                break

            end = min(start + chunk_size, total_tokens)

            # Decode chunk
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)

            # Prevent infinite loop - break if we've reached the end
            if end >= total_tokens:
                break

            # Move to next chunk with overlap
            start = end - overlap

            # Additional safety: ensure we're making progress
            if start + chunk_size <= end:
                # Not making progress - adjust
                start = end - (overlap // 2)

        return chunks

    @classmethod
    def get_model_limit(cls, model: str) -> int:
        """
        Get token limit for Claude models

        Args:
            model: Model name (ignored - all Claude models have same limit)

        Returns:
            Maximum input tokens (200K for all Claude models)
        """
        return cls.TOKEN_LIMIT

    @classmethod
    def validate_text_length(cls, text: str, model: str) -> tuple[bool, str]:
        """
        Validate if text is within safe limits for model

        Args:
            text: Text to validate
            model: Model name

        Returns:
            Tuple of (is_valid, error_message)
        """
        manager = cls(model)
        token_count = manager.count_tokens(text)

        if token_count <= manager.safe_max_tokens:
            return True, ""

        error_msg = (
            f"Text exceeds safe token limit for {model}. "
            f"Current: {token_count:,} tokens, "
            f"Safe limit: {manager.safe_max_tokens:,} tokens. "
            f"Text will be automatically truncated."
        )

        return False, error_msg
