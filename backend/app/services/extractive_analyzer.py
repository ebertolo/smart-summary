"""
Extractive summarization service using Sumy
Fast, lightweight, no GPU required
Supports multiple algorithms: TextRank, LexRank, LSA, Luhn
"""

import re
from typing import Dict, List, Tuple

import nltk
from sumy.nlp.stemmers import Stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.utils import get_stop_words


class ExtractiveAnalyzer:
    """
    Extractive summarization using graph-based and statistical algorithms
    All algorithms are fast and don't require GPU
    """

    # Download required NLTK data on first import
    _nltk_initialized = False

    def __init__(self, language: str = "english", algorithm: str = "textrank"):
        """
        Initialize extractive analyzer

        Args:
            language: Language for tokenization (default: english)
            algorithm: Algorithm to use (textrank, lexrank, lsa, luhn)
        """
        self.language = language
        self.algorithm = algorithm.lower()

        # Initialize NLTK data if needed
        if not ExtractiveAnalyzer._nltk_initialized:
            self._initialize_nltk()
            ExtractiveAnalyzer._nltk_initialized = True

        # Initialize stemmer and stop words
        self.stemmer = Stemmer(language)
        self.stop_words = get_stop_words(language)

        # Initialize summarizer
        self.summarizer = self._get_summarizer()

    def _initialize_nltk(self):
        """Download required NLTK data"""
        import os

        # Set NLTK data path to include user's home directory
        nltk_data_paths = [
            os.path.expanduser("~/nltk_data"),
            os.path.expanduser("~\\nltk_data"),  # Windows
            "/usr/local/share/nltk_data",
            "/usr/share/nltk_data",
        ]

        for path in nltk_data_paths:
            if path not in nltk.data.path:
                nltk.data.path.append(path)

        # Download punkt tokenizer
        required_packages = ["punkt", "punkt_tab"]

        for package in required_packages:
            try:
                nltk.data.find(f"tokenizers/{package}")
            except LookupError:
                try:
                    print(f"Downloading NLTK package: {package}")
                    nltk.download(package, quiet=False)
                    print(f"✓ Successfully downloaded {package}")
                except Exception as e:
                    print(f"Warning: Failed to download {package}: {e}")
                    print(f"Trying alternative download method...")
                    try:
                        # Try downloading to specific directory
                        download_dir = os.path.expanduser("~/nltk_data")
                        os.makedirs(download_dir, exist_ok=True)
                        nltk.download(package, download_dir=download_dir, quiet=False)
                        print(f"✓ Downloaded {package} to {download_dir}")
                    except Exception as e2:
                        print(f"Error: Could not download {package}: {e2}")
                        # Continue anyway, will use fallback tokenizer

    def _get_summarizer(self):
        """Get summarizer instance based on algorithm"""
        if self.algorithm == "textrank":
            return TextRankSummarizer(self.stemmer)
        elif self.algorithm == "lexrank":
            return LexRankSummarizer(self.stemmer)
        elif self.algorithm == "lsa":
            return LsaSummarizer(self.stemmer)
        elif self.algorithm == "luhn":
            return LuhnSummarizer(self.stemmer)
        else:
            # Default to TextRank
            return TextRankSummarizer(self.stemmer)

    def extract_sentences(
        self, text: str, sentence_count: int = 10, compression_ratio: float = None
    ) -> List[str]:
        """
        Extract most important sentences from text

        Args:
            text: Input text
            sentence_count: Number of sentences to extract
            compression_ratio: Alternative to sentence_count (0.0-1.0)

        Returns:
            List of extracted sentences
        """
        if not text or not text.strip():
            return []

        # Clean text
        text = self._clean_text(text)

        # Try to parse text with NLTK tokenizer
        try:
            parser = PlaintextParser.from_string(text, Tokenizer(self.language))

            # Calculate sentence count if compression ratio provided
            if compression_ratio is not None:
                total_sentences = len(list(parser.document.sentences))
                sentence_count = max(1, int(total_sentences * compression_ratio))

            # Extract sentences
            sentences = self.summarizer(parser.document, sentence_count)
            return [str(sentence) for sentence in sentences]

        except LookupError as e:
            # NLTK tokenizers missing - use fallback
            print(
                f"Warning: NLTK tokenizers not available, using fallback extraction: {e}"
            )
            return self._fallback_extraction(text, sentence_count)
        except Exception as e:
            print(f"Warning: Extractive summarization failed: {e}")
            # Fallback: return first sentences
            return self._fallback_extraction(text, sentence_count)

    def extract_from_chunks(
        self, chunks: List[str], sentences_per_chunk: int = 5
    ) -> List[str]:
        """
        Extract key sentences from multiple chunks

        Args:
            chunks: List of text chunks
            sentences_per_chunk: Sentences to extract per chunk

        Returns:
            Combined list of extracted sentences
        """
        all_sentences = []

        for chunk in chunks:
            sentences = self.extract_sentences(chunk, sentences_per_chunk)
            all_sentences.extend(sentences)

        return all_sentences

    def extract_and_compress(self, text: str, target_ratio: float = 0.3) -> str:
        """
        Extract and compress text to target ratio

        Args:
            text: Input text
            target_ratio: Target compression ratio (0.0-1.0)

        Returns:
            Compressed text as string
        """
        sentences = self.extract_sentences(text, compression_ratio=target_ratio)
        return " ".join(sentences)

    def get_essential_content(self, text: str, max_length: int = 50000) -> str:
        """
        Extract essential content up to max length
        Useful for pre-processing before LLM

        Args:
            text: Input text
            max_length: Maximum output length in characters

        Returns:
            Essential content within max_length
        """
        if len(text) <= max_length:
            return text

        # Calculate target ratio to fit max_length
        target_ratio = max_length / len(text)

        # Extract sentences
        compressed = self.extract_and_compress(text, target_ratio)

        # Ensure within limit
        if len(compressed) > max_length:
            compressed = compressed[:max_length]

        return compressed

    def analyze_content_importance(
        self, text: str, num_sections: int = 10
    ) -> List[Dict[str, any]]:
        """
        Analyze and rank text sections by importance

        Args:
            text: Input text
            num_sections: Number of sections to return

        Returns:
            List of dicts with sentence and score
        """
        if not text or not text.strip():
            return []

        text = self._clean_text(text)

        try:
            parser = PlaintextParser.from_string(text, Tokenizer(self.language))

            # Get sentences with scores using TextRank
            summarizer = TextRankSummarizer(self.stemmer)
            summarizer.stop_words = self.stop_words

            # Get rated sentences
            ratings = summarizer.rate_sentences(parser.document)

            # Sort by rating
            sorted_sentences = sorted(
                ratings.items(), key=lambda x: x[1], reverse=True
            )[:num_sections]

            return [
                {"sentence": str(sentence), "score": float(score), "rank": i + 1}
                for i, (sentence, score) in enumerate(sorted_sentences)
            ]
        except (LookupError, AttributeError) as e:
            # NLTK tokenizers missing or numpy issue - use fallback
            print(f"Warning: NLTK/numpy not available for content analysis: {e}")
            sentences = self._fallback_extraction(text, num_sections)
            return [
                {
                    "sentence": sent,
                    "score": 1.0 - (i * 0.1),  # Decreasing scores
                    "rank": i + 1,
                }
                for i, sent in enumerate(sentences)
            ]
        except Exception as e:
            # Any other error - use fallback instead of returning empty
            print(f"Warning: Content analysis failed: {e}, using fallback")
            sentences = self._fallback_extraction(text, num_sections)
            return [
                {"sentence": sent, "score": 1.0 - (i * 0.1), "rank": i + 1}
                for i, sent in enumerate(sentences)
            ]

    def _clean_text(self, text: str) -> str:
        """Clean text for processing"""
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove special characters that might cause issues
        text = text.strip()

        return text

    def _fallback_extraction(self, text: str, count: int) -> List[str]:
        """
        Fallback extraction method if main algorithm fails
        Uses simple heuristics: sentence length and position
        """
        # Split by sentence terminators
        sentences = re.split(r"(?<=[.!?])\s+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) <= count:
            return sentences

        # Score sentences by length (prefer medium-length sentences)
        # and position (prefer beginning)
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            word_count = len(sentence.split())
            # Prefer 10-30 word sentences
            length_score = (
                min(word_count / 30.0, 1.0)
                if word_count < 30
                else max(1.0 - (word_count - 30) / 50.0, 0.5)
            )
            # Prefer earlier sentences (but not too much)
            position_score = 1.0 - (i / len(sentences)) * 0.3
            # Combined score
            score = length_score * position_score
            scored_sentences.append((score, sentence))

        # Sort by score and return top N
        scored_sentences.sort(reverse=True, key=lambda x: x[0])
        return [sent for _, sent in scored_sentences[:count]]

    @staticmethod
    def get_available_algorithms() -> List[str]:
        """Get list of available algorithms"""
        return ["textrank", "lexrank", "lsa", "luhn"]

    @staticmethod
    def get_algorithm_info() -> Dict[str, str]:
        """Get information about each algorithm"""
        return {
            "textrank": (
                "Graph-based ranking using sentence similarity. "
                "Fast, works well for most texts. "
                "Speed: ⚡⚡⚡ Quality: ⭐⭐⭐"
            ),
            "lexrank": (
                "Graph-based similar to TextRank but uses different similarity metric. "
                "Good for formal documents. "
                "Speed: ⚡⚡⚡ Quality: ⭐⭐⭐"
            ),
            "lsa": (
                "Latent Semantic Analysis using SVD. "
                "Good for topical content. "
                "Speed: ⚡⚡ Quality: ⭐⭐⭐"
            ),
            "luhn": (
                "Statistical method based on word frequency. "
                "Very fast, good for simple texts. "
                "Speed: ⚡⚡⚡⚡ Quality: ⭐⭐"
            ),
        }
