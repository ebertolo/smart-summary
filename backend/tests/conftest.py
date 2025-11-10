"""
Pytest configuration and fixtures
"""

import os
import sys

import pytest

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def pytest_configure(config):
    """
    Configure pytest - runs before any tests
    Setup NLTK data if needed
    """
    # Import here to avoid circular imports
    from tests.setup_nltk import setup_nltk

    # Only setup NLTK if running extractive tests
    if any("extractive" in arg for arg in config.invocation_params.args):
        print("\n" + "=" * 60)
        print("Detected extractive summarization tests - setting up NLTK...")
        print("=" * 60)
        setup_nltk()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Setup test environment before running tests
    This runs once per test session
    """
    # Ensure NLTK data is available for extractive tests
    try:
        import nltk

        nltk.data.find("tokenizers/punkt")
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        # Download if missing
        from tests.setup_nltk import setup_nltk

        setup_nltk()

    yield

    # Cleanup after all tests (if needed)
    pass


@pytest.fixture
def sample_text():
    """Fixture providing sample text for tests"""
    return """
    Artificial intelligence is transforming the world.
    Machine learning enables computers to learn from data.
    Deep learning uses neural networks with multiple layers.
    Natural language processing helps computers understand text.
    Computer vision allows machines to interpret images.
    AI has applications in healthcare, finance, and education.
    """


@pytest.fixture
def large_sample_text():
    """Fixture providing larger sample text for performance tests"""
    base_text = """
    Section about artificial intelligence and its impact on society.
    Machine learning algorithms are becoming more sophisticated.
    Deep learning models require significant computational resources.
    Natural language processing enables human-computer interaction.
    Computer vision systems can recognize objects and faces.
    Robotics combines AI with mechanical engineering.
    """

    # Repeat to create larger text
    return base_text * 50


# Configure pytest output
def pytest_collection_modifyitems(config, items):
    """
    Modify test items after collection
    Add markers or skip tests based on conditions
    """
    # Get registered markers from pytest.ini
    # config.getini("markers") returns a list of strings like "slow: description"
    try:
        markers_config = config.getini("markers")
        registered_markers = {marker.split(":")[0].strip() for marker in markers_config}
    except Exception:
        # If no markers configured, use empty set
        registered_markers = set()

    for item in items:
        # Add slow marker to performance tests (if registered)
        if "performance" in item.nodeid.lower() and "slow" in registered_markers:
            item.add_marker(pytest.mark.slow)

        # Add integration marker to tests that require external services (if registered)
        if (
            "llm" in item.nodeid.lower() or "api" in item.nodeid.lower()
        ) and "integration" in registered_markers:
            item.add_marker(pytest.mark.integration)
