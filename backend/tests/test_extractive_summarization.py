"""
Tests for Extractive Summarization with Sumy
"""

import pytest

from app.services.extractive_analyzer import ExtractiveAnalyzer


class TestExtractiveAnalyzer:
    """Test extractive summarization functionality"""

    def test_different_algorithms(self):
        """Test initialization with different algorithms"""
        algorithms = ["textrank", "lexrank", "lsa", "luhn"]

        for algo in algorithms:
            analyzer = ExtractiveAnalyzer(algorithm=algo)
            assert analyzer.algorithm == algo
            assert analyzer.summarizer is not None

    def test_extract_sentences_basic(self):
        """Test basic sentence extraction"""
        analyzer = ExtractiveAnalyzer()

        text = """
        This is the first sentence about climate change.
        Climate change is affecting global temperatures.
        Rising temperatures impact wildlife habitats.
        Many species are at risk due to habitat loss.
        Conservation efforts are crucial for protection.
        Scientists study these changes carefully.
        Data shows increasing temperature trends.
        Action is needed to address these issues.
        """

        sentences = analyzer.extract_sentences(text, sentence_count=3)

        assert len(sentences) > 0
        assert len(sentences) <= 3
        assert all(isinstance(s, str) for s in sentences)

    def test_extract_with_compression_ratio(self):
        """Test extraction using compression ratio and calculation"""
        analyzer = ExtractiveAnalyzer()

        # Test 1: Basic compression ratio extraction
        text = ". ".join([f"Sentence number {i}" for i in range(100)])
        sentences = analyzer.extract_sentences(text, compression_ratio=0.3)

        assert len(sentences) > 0
        # Should extract around 30 sentences (30% of 100)
        assert 20 <= len(sentences) <= 40

        # Test 2: Verify compression ratio calculation
        ratio = len(sentences) / 100
        assert 0.2 <= ratio <= 0.4  # Allow some variance

    def test_extract_from_chunks(self):
        """Test extraction from multiple chunks"""
        analyzer = ExtractiveAnalyzer()

        chunks = [
            "First chunk with important information about topic A.",
            "Second chunk discussing different aspects of topic B.",
            "Third chunk with conclusions and recommendations.",
        ]

        sentences = analyzer.extract_from_chunks(chunks, sentences_per_chunk=1)

        assert len(sentences) > 0
        assert len(sentences) <= len(chunks)

    def test_extract_and_compress(self):
        """Test extraction and compression to string"""
        analyzer = ExtractiveAnalyzer()

        text = """
        Machine learning is a subset of artificial intelligence.
        It focuses on building systems that learn from data.
        Deep learning is a type of machine learning.
        Neural networks are used in deep learning.
        Training requires large amounts of data.
        Models can make predictions on new data.
        Applications include image recognition and NLP.
        The field is rapidly evolving.
        """

        compressed = analyzer.extract_and_compress(text, target_ratio=0.5)

        assert isinstance(compressed, str)
        assert len(compressed) > 0
        assert len(compressed) < len(text)

    def test_get_essential_content(self):
        """Test getting essential content within length limit (large and small text)"""
        analyzer = ExtractiveAnalyzer()

        # Test 1: Large text that needs compression
        large_text = "This is a test sentence. " * 1000  # ~25K chars
        essential_large = analyzer.get_essential_content(large_text, max_length=5000)

        assert len(essential_large) <= 5000
        assert len(essential_large) > 0

        # Test 2: Small text that doesn't need compression
        small_text = "Short text that doesn't need compression."
        essential_small = analyzer.get_essential_content(small_text, max_length=1000)

        assert essential_small == small_text

    def test_analyze_content_importance(self):
        """Test content importance analysis"""
        analyzer = ExtractiveAnalyzer()

        text = """
        Artificial intelligence is transforming industries.
        Healthcare benefits from AI diagnostics.
        Finance uses AI for fraud detection.
        Transportation is being revolutionized by autonomous vehicles.
        Education systems are incorporating AI tutors.
        Ethics in AI development is crucial.
        Privacy concerns must be addressed.
        Future of AI looks promising yet challenging.
        """

        analysis = analyzer.analyze_content_importance(text, num_sections=5)

        assert isinstance(analysis, list)
        assert len(analysis) > 0

        for item in analysis:
            assert "sentence" in item
            assert "score" in item
            assert "rank" in item
            assert isinstance(item["score"], float)

    def test_large_text_performance(self):
        """Test performance with large text"""
        import time

        analyzer = ExtractiveAnalyzer()

        # Create 50K character text
        base_sentence = "This is test sentence number {}. "
        text = "".join([base_sentence.format(i) for i in range(1500)])

        start = time.time()
        sentences = analyzer.extract_sentences(text, sentence_count=20)
        elapsed = time.time() - start

        assert len(sentences) > 0
        # TextRank algorithm is O(n²) for 1500 sentences - allow up to 15s
        assert elapsed < 15.0, f"Extraction took {elapsed:.2f}s, should be < 15s"

        print(
            f"\n✓ Extracted {len(sentences)} sentences from 50K chars in {elapsed:.3f}s"
        )

    def test_different_algorithms_comparison(self):
        """Compare different algorithms on same text"""
        text = """
        Natural language processing enables computers to understand human language.
        Text analysis involves various computational techniques.
        Machine learning models power modern NLP systems.
        Transformers have revolutionized the field.
        BERT and GPT are popular model architectures.
        Applications range from chatbots to translation.
        Context understanding is crucial for accuracy.
        The field continues to advance rapidly.
        """

        algorithms = ["textrank", "lexrank", "lsa", "luhn"]
        results = {}

        for algo in algorithms:
            analyzer = ExtractiveAnalyzer(algorithm=algo)
            sentences = analyzer.extract_sentences(text, sentence_count=3)
            results[algo] = sentences

        # All should extract sentences
        for algo, sentences in results.items():
            assert len(sentences) > 0, f"{algo} failed to extract sentences"
            print(f"\n{algo}: {len(sentences)} sentences")


class TestMapReducePipeline:
    """Test Map-Reduce pipeline with extractive + abstractive"""

    def test_map_phase_extraction(self):
        """Test MAP phase: extractive summarization"""
        analyzer = ExtractiveAnalyzer()

        chunks = [
            "Chunk 1: " + " ".join([f"Sentence {i}." for i in range(20)]),
            "Chunk 2: " + " ".join([f"Statement {i}." for i in range(20)]),
            "Chunk 3: " + " ".join([f"Point {i}." for i in range(20)]),
        ]

        # MAP: Extract from each chunk
        extracted = []
        for chunk in chunks:
            sentences = analyzer.extract_sentences(chunk, sentence_count=5)
            extracted.extend(sentences)

        # Should have extracted sentences from all chunks
        assert len(extracted) > 0
        assert len(extracted) <= len(chunks) * 5


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
