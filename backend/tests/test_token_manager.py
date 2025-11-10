"""
Tests for TokenManager service
"""

import pytest

from app.services.token_manager import TokenManager


class TestTokenManager:
    """Test token counting and truncation"""

    def test_count_tokens_simple(self):
        """Test basic token counting"""
        manager = TokenManager(model="claude-3-5-sonnet-20241022")

        text = "Hello world, this is a test."
        token_count = manager.count_tokens(text)

        assert token_count > 0
        assert token_count < 20  # Should be around 8-10 tokens

    def test_truncate_within_limit(self):
        """Test text that doesn't need truncation"""
        manager = TokenManager()
        text = "Short text"

        truncated = manager.truncate_to_limit(text, max_tokens=1000)
        assert truncated == text

    def test_truncate_exceeds_limit(self):
        """Test text that needs truncation"""
        manager = TokenManager()

        # Create text that's definitely too long
        text = "Hello world. " * 10000  # ~20k tokens

        truncated = manager.truncate_to_limit(text, max_tokens=100)

        # Should be truncated
        assert len(truncated) < len(text)
        assert "[... texto truncado ...]" in truncated

        # Verify it's within limit (allow small margin for truncation notice)
        token_count = manager.count_tokens(truncated)
        assert token_count <= 110, f"Token count {token_count} exceeds limit of 110"

    def test_truncate_preserve_end(self):
        """Test truncation preserving end of text"""
        manager = TokenManager()

        text = "Start of text. " * 1000 + "END_MARKER"
        truncated = manager.truncate_to_limit(text, max_tokens=100, preserve_end=True)

        assert "END_MARKER" in truncated
        assert "[... texto truncado ...]" in truncated

    def test_get_token_info(self):
        """Test token info retrieval"""
        manager = TokenManager()
        text = "This is a test sentence."

        info = manager.get_token_info(text)

        assert "token_count" in info
        assert "model" in info
        assert "within_limit" in info
        assert info["token_count"] > 0
        assert info["character_count"] == len(text)

    def test_chunk_by_tokens(self):
        """Test chunking by token count"""
        manager = TokenManager()

        # Create text with ~500 tokens
        text = "This is a sentence. " * 100

        chunks = manager.chunk_by_tokens(text, chunk_size=50, overlap=10)

        assert len(chunks) > 1
        for chunk in chunks:
            token_count = manager.count_tokens(chunk)
            assert token_count <= 50

    def test_model_limits(self):
        """Test model limit retrieval"""
        limit = TokenManager.get_model_limit("claude-3-5-sonnet-20241022")
        assert limit == 200_000

        limit = TokenManager.get_model_limit("gpt-4-turbo")
        assert limit == 128_000

    def test_different_models(self):
        """Test initialization with different models"""
        models = ["claude-3-5-sonnet-20241022", "gpt-4-turbo", "gemini-1.5-pro"]

        for model in models:
            manager = TokenManager(model=model)
            assert manager.model == model
            assert manager.max_tokens > 0

            # Test counting works
            count = manager.count_tokens("Test text")
            assert count > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
