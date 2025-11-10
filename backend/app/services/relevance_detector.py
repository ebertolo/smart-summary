"""
Relevance Detection Service using TextRank
Identifies and ranks the most important parts of text for quality summarization
"""

from typing import Dict, List, Tuple

from app.core.config import settings
from app.services.extractive_analyzer import ExtractiveAnalyzer


class RelevanceDetector:
    """
    Detects and ranks text sections by relevance/importance
    Uses TextRank algorithm for fast, accurate importance scoring
    """

    def __init__(self, algorithm: str = "textrank"):
        """
        Initialize relevance detector

        Args:
            algorithm: Algorithm to use (textrank recommended for quality)
        """
        self.analyzer = ExtractiveAnalyzer(language="english", algorithm=algorithm)

    def extract_essential_parts(
        self, text: str, target_ratio: float = 0.3, min_sentences: int = 10
    ) -> str:
        """
        Extract the most essential parts of text

        Args:
            text: Input text to analyze
            target_ratio: Target compression ratio (0.0-1.0)
            min_sentences: Minimum sentences to extract

        Returns:
            Text containing only essential parts
        """
        if not text or not text.strip():
            return text

        # Use extractive analyzer to get essential content
        essential = self.analyzer.extract_and_compress(text, target_ratio=target_ratio)

        # Ensure minimum sentences
        sentences = essential.split(". ")
        if len(sentences) < min_sentences:
            # If too few, increase ratio
            essential = self.analyzer.extract_and_compress(
                text, target_ratio=min(target_ratio * 1.5, 1.0)
            )

        return essential

    def rank_chunks_by_importance(
        self, chunks: List[str], top_k: int = None
    ) -> List[Tuple[int, str, float]]:
        """
        Rank chunks by importance and return top K

        Args:
            chunks: List of text chunks
            top_k: Number of top chunks to return (None = all)

        Returns:
            List of tuples (original_index, chunk, importance_score)
        """
        chunk_scores = []

        for idx, chunk in enumerate(chunks):
            # Analyze importance of this chunk
            analysis = self.analyzer.analyze_content_importance(
                chunk, num_sections=5  # Get top 5 sentences to calculate score
            )

            # Calculate average score as chunk importance
            if analysis:
                avg_score = sum(item["score"] for item in analysis) / len(analysis)
            else:
                avg_score = 0.0

            chunk_scores.append((idx, chunk, avg_score))

        # Sort by score (descending)
        chunk_scores.sort(key=lambda x: x[2], reverse=True)

        # Return top K or all
        if top_k is not None:
            return chunk_scores[:top_k]

        return chunk_scores

    def prioritize_chunks(
        self, chunks: List[str], priority_ratio: float = 0.7
    ) -> Tuple[List[str], List[str]]:
        """
        Separate chunks into high-priority and low-priority

        Args:
            chunks: List of text chunks
            priority_ratio: Ratio of chunks to mark as high priority

        Returns:
            Tuple of (high_priority_chunks, low_priority_chunks)
        """
        # Rank all chunks
        ranked = self.rank_chunks_by_importance(chunks)

        # Calculate split point
        split_point = max(1, int(len(ranked) * priority_ratio))

        # Split into high and low priority
        high_priority = [chunk for _, chunk, _ in ranked[:split_point]]
        low_priority = [chunk for _, chunk, _ in ranked[split_point:]]

        return high_priority, low_priority

    def get_importance_map(
        self, text: str, num_sections: int = 10
    ) -> List[Dict[str, any]]:
        """
        Get detailed importance map of text sections

        Args:
            text: Input text
            num_sections: Number of sections to analyze

        Returns:
            List of dicts with section info and importance scores
        """
        return self.analyzer.analyze_content_importance(text, num_sections)

    def filter_by_threshold(
        self, chunks: List[str], threshold: float = 0.5
    ) -> List[str]:
        """
        Filter chunks by importance threshold

        Args:
            chunks: List of text chunks
            threshold: Minimum importance score (0.0-1.0)

        Returns:
            List of chunks above threshold
        """
        ranked = self.rank_chunks_by_importance(chunks)

        # Normalize scores to 0-1 range
        if not ranked:
            return chunks

        max_score = max(score for _, _, score in ranked)
        if max_score == 0:
            return chunks

        # Filter by normalized threshold
        filtered = [
            chunk for _, chunk, score in ranked if (score / max_score) >= threshold
        ]

        # Ensure at least one chunk
        if not filtered and ranked:
            filtered = [ranked[0][1]]

        return filtered

    def smart_chunking_with_priority(
        self, text: str, chunk_size: int = 100000, max_chunks: int = 10
    ) -> List[Dict[str, any]]:
        """
        Split text and assign priority scores to each chunk

        Args:
            text: Input text
            chunk_size: Target size for chunks
            max_chunks: Maximum number of chunks

        Returns:
            List of dicts with chunk, index, and priority score
        """
        from app.services.text_processor import TextProcessor

        processor = TextProcessor()

        # Split into chunks
        import asyncio

        chunks = asyncio.run(processor.split_into_chunks(text, max_size=chunk_size))

        # Limit to max chunks
        chunks = chunks[:max_chunks]

        # Rank chunks
        ranked = self.rank_chunks_by_importance(chunks)

        # Create output with priority info
        result = []
        for idx, chunk, score in ranked:
            result.append(
                {
                    "original_index": idx,
                    "chunk": chunk,
                    "priority_score": score,
                    "size": len(chunk),
                    "is_essential": score
                    > (sum(s for _, _, s in ranked) / len(ranked)),
                }
            )

        # Sort back to original order
        result.sort(key=lambda x: x["original_index"])

        return result

    def preprocess_for_llm(
        self, text: str, max_length: int = 50000, preserve_structure: bool = True
    ) -> str:
        """
        Preprocess text for LLM by extracting essential content
        Optimizes token usage while preserving quality

        Args:
            text: Input text
            max_length: Maximum output length
            preserve_structure: Try to preserve document structure

        Returns:
            Preprocessed text ready for LLM
        """
        if len(text) <= max_length:
            return text

        # Calculate target ratio
        target_ratio = max_length / len(text)

        if preserve_structure:
            # Try to preserve structure by extracting from sections
            chunks = []
            current_chunk = []
            current_size = 0

            for line in text.split("\n"):
                # Detect headers (markdown style)
                is_header = line.strip().startswith("#") or len(line.strip()) < 50

                if is_header and current_chunk:
                    # Save current chunk
                    chunks.append("\n".join(current_chunk))
                    current_chunk = [line]
                    current_size = len(line)
                else:
                    current_chunk.append(line)
                    current_size += len(line)

            if current_chunk:
                chunks.append("\n".join(current_chunk))

            # Extract from each chunk proportionally
            processed_chunks = []
            for chunk in chunks:
                chunk_ratio = min(
                    target_ratio * 1.2, 1.0
                )  # Slightly more to compensate
                processed = self.analyzer.extract_and_compress(chunk, chunk_ratio)
                processed_chunks.append(processed)

            result = "\n\n".join(processed_chunks)

            # Trim if still too long
            if len(result) > max_length:
                result = result[:max_length]

            return result
        else:
            # Simple extraction
            return self.analyzer.get_essential_content(text, max_length)

    @staticmethod
    def get_recommended_ratio(text_length: int) -> float:
        """
        Get recommended compression ratio based on text length

        Args:
            text_length: Length of input text

        Returns:
            Recommended compression ratio
        """
        if text_length < 10000:
            return 1.0  # No compression
        elif text_length < 50000:
            return 0.7  # Light compression
        elif text_length < 100000:
            return 0.5  # Medium compression
        elif text_length < 200000:
            return 0.3  # Heavy compression
        else:
            return 0.2  # Maximum compression for very large texts
