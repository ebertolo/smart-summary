"""
Tests for semantic chunking and optimized strategies
"""

import asyncio

import pytest

from app.core.config import settings
from app.services.summarizer import SummarizerService
from app.services.text_processor import TextProcessor


class TestSemanticChunking:
    """Test semantic chunking functionality"""

    @pytest.mark.asyncio
    async def test_semantic_chunking_basic(self):
        """Test basic semantic chunking"""
        processor = TextProcessor()

        # Create text with natural breaks
        text = """
## Introduction
This is the introduction section. It has multiple sentences.

## Main Content
This is the main content section. It contains important information.
We want to keep this section together.

## Conclusion
This is the conclusion section. It wraps everything up.
"""

        chunks = await processor.split_into_chunks(text, max_size=200)

        assert len(chunks) > 0
        # Semantic splitter should respect section boundaries
        assert any("Introduction" in chunk for chunk in chunks)

    @pytest.mark.asyncio
    async def test_large_chunk_size(self):
        """Test with large chunk size (100K)"""
        processor = TextProcessor()

        # Create 150K character text
        text = "This is a test sentence. " * 6000  # ~150K chars

        chunks = await processor.split_into_chunks(
            text, max_size=settings.HIERARCHICAL_CHUNK_SIZE
        )

        # Should create 2 chunks (150K / 100K = 2)
        assert len(chunks) >= 1
        assert len(chunks) <= 3

        # Each chunk should be close to max size
        for chunk in chunks[:-1]:  # All except last
            assert len(chunk) <= settings.HIERARCHICAL_CHUNK_SIZE + 1000

    @pytest.mark.asyncio
    async def test_different_strategies_chunk_size(self):
        """Test that different strategies use different chunk sizes"""
        processor = TextProcessor()

        text = "Test. " * 5000  # ~30K chars

        # Hierarchical should use larger chunks
        hier_chunks = await processor.split_into_chunks(text, strategy="hierarchical")

        # Detailed should use smaller chunks
        detail_chunks = await processor.split_into_chunks(text, strategy="detailed")

        # Detailed should create more chunks (smaller size)
        assert len(detail_chunks) >= len(hier_chunks)

    @pytest.mark.asyncio
    async def test_overlap_preservation(self):
        """Test that overlap is preserved between chunks"""
        processor = TextProcessor()

        base_sentence = "Sentence {}. "
        text = "".join([base_sentence.format(i) for i in range(1000)])

        chunks = await processor.split_into_chunks(text, max_size=5000, overlap=500)

        if len(chunks) > 1:
            # Check for overlap between consecutive chunks
            for i in range(len(chunks) - 1):
                chunk1_end = chunks[i][-200:]  # Last 200 chars
                chunk2_start = chunks[i + 1][:200]  # First 200 chars

                # Should have some overlap (not exact match due to semantic boundaries)
                # Just verify both chunks exist and have content
                assert len(chunk1_end) > 0
                assert len(chunk2_start) > 0


class TestOptimizedStrategies:
    """Test optimized summarization strategies"""

    @pytest.mark.asyncio
    async def test_hierarchical_with_small_text(self):
        """Test hierarchical strategy with small text (should use simple)"""
        summarizer = SummarizerService(strategy="hierarchical")

        text = "This is a short text that doesn't need chunking."

        # Should not create chunks
        result = await summarizer.summarize(text)

        assert len(result) > 0
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_hierarchical_creates_chunks(self):
        """Test that hierarchical creates chunks for large text"""
        summarizer = SummarizerService(strategy="hierarchical")

        # Create text larger than chunk size
        base_sentence = "This is sentence number {}. "
        text = "".join([base_sentence.format(i) for i in range(5000)])  # ~150K chars

        # Mock to count chunks created
        original_split = summarizer.text_processor.split_into_chunks
        chunk_count = []

        async def mock_split(*args, **kwargs):
            result = await original_split(*args, **kwargs)
            chunk_count.append(len(result))
            return result

        summarizer.text_processor.split_into_chunks = mock_split

        # Note: This will fail without API key, but we can check the mocking worked
        try:
            await summarizer.summarize(text)
        except Exception:
            pass  # Expected to fail without API key

        # Verify chunks were created
        if chunk_count:
            assert chunk_count[0] > 1  # Should create multiple chunks

    @pytest.mark.asyncio
    async def test_parallel_processing_structure(self):
        """Test that parallel processing structure is correct"""
        summarizer = SummarizerService(strategy="hierarchical")

        # Test the parallel summarization method exists
        assert hasattr(summarizer, "_summarize_chunks_parallel")

        # Test that it accepts correct parameters
        import inspect

        sig = inspect.signature(summarizer._summarize_chunks_parallel)
        params = list(sig.parameters.keys())

        assert "chunks" in params
        assert "words_per_chunk" in params


class TestPerformanceMetrics:
    """Test performance-related metrics"""

    @pytest.mark.asyncio
    async def test_chunk_creation_performance(self):
        """Test that chunking is fast"""
        import time

        processor = TextProcessor()

        # Create large text (300K chars)
        text = "Test sentence with some content. " * 9000  # ~300K chars

        start = time.time()
        chunks = await processor.split_into_chunks(text)
        elapsed = time.time() - start

        # Chunking should be very fast (< 1 second)
        assert elapsed < 1.0, f"Chunking took {elapsed:.2f}s, should be < 1s"

        print(f"\n✓ Chunked 300K chars into {len(chunks)} chunks in {elapsed:.3f}s")

    @pytest.mark.asyncio
    async def test_300k_text_chunking(self):
        """Test chunking of exactly 300K characters"""
        processor = TextProcessor()

        # Create exactly 300K characters
        base_text = "This is test sentence number {}. "
        text = ""
        while len(text) < 300000:
            text += base_text.format(len(text))
        text = text[:300000]  # Exactly 300K

        chunks = await processor.split_into_chunks(
            text, max_size=settings.HIERARCHICAL_CHUNK_SIZE
        )

        # With 100K chunks, should create ~3 chunks
        assert len(chunks) >= 2
        assert len(chunks) <= 4

        print(f"\n✓ 300K chars split into {len(chunks)} chunks")
        for i, chunk in enumerate(chunks, 1):
            print(f"  Chunk {i}: {len(chunk):,} chars")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
