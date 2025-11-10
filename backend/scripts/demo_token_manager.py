"""
Demo script for TokenManager functionality
Run this to see token counting and truncation in action
"""

from app.services.token_manager import TokenManager


def demo_basic_counting():
    """Demo 1: Basic token counting"""
    print("=" * 70)
    print("DEMO 1: Basic Token Counting")
    print("=" * 70)

    manager = TokenManager(model="claude-3-5-sonnet-20241022")

    texts = [
        "Hello world!",
        "This is a longer sentence with more words and tokens.",
        "The quick brown fox jumps over the lazy dog. " * 10,
    ]

    for i, text in enumerate(texts, 1):
        token_count = manager.count_tokens(text)
        char_count = len(text)
        ratio = token_count / char_count if char_count > 0 else 0

        print(f"\nText {i}:")
        print(f"  Characters: {char_count}")
        print(f"  Tokens: {token_count}")
        print(f"  Ratio: {ratio:.3f} tokens/char")
        print(f"  Preview: {text[:60]}...")


def demo_token_info():
    """Demo 2: Detailed token information"""
    print("\n\n" + "=" * 70)
    print("DEMO 2: Detailed Token Information")
    print("=" * 70)

    manager = TokenManager(model="claude-3-5-sonnet-20241022")

    # Create a medium-sized text
    text = "Lorem ipsum dolor sit amet. " * 1000

    info = manager.get_token_info(text)

    print(f"\nModel: {info['model']}")
    print(f"Token Count: {info['token_count']:,}")
    print(f"Character Count: {info['character_count']:,}")
    print(f"Max Tokens: {info['max_tokens']:,}")
    print(f"Safe Max: {info['safe_max_tokens']:,}")
    print(f"Within Limit: {info['within_limit']}")
    print(f"Usage: {info['usage_percentage']}%")
    print(f"Needs Truncation: {info['needs_truncation']}")


def demo_truncation():
    """Demo 3: Text truncation"""
    print("\n\n" + "=" * 70)
    print("DEMO 3: Text Truncation")
    print("=" * 70)

    manager = TokenManager(model="gpt-4")  # Small limit for demo

    # Create text that exceeds limit
    text = "This is sentence number {}. " * 500
    text = "".join([text.format(i) for i in range(500)])

    print(f"\nOriginal text:")
    print(f"  Length: {len(text):,} characters")
    print(f"  Tokens: {manager.count_tokens(text):,}")
    print(f"  Model limit: {manager.max_tokens:,} tokens")

    # Truncate
    truncated = manager.truncate_to_limit(text, max_tokens=500)

    print(f"\nTruncated text:")
    print(f"  Length: {len(truncated):,} characters")
    print(f"  Tokens: {manager.count_tokens(truncated):,}")
    print(f"  Preview: {truncated[:200]}...")


def demo_chunking():
    """Demo 4: Token-based chunking"""
    print("\n\n" + "=" * 70)
    print("DEMO 4: Token-Based Chunking")
    print("=" * 70)

    manager = TokenManager()

    # Create a large text
    text = "This is paragraph {}. It contains multiple sentences. " * 200
    text = "".join([text.format(i) for i in range(200)])

    print(f"\nOriginal text:")
    print(f"  Characters: {len(text):,}")
    print(f"  Tokens: {manager.count_tokens(text):,}")

    # Chunk by tokens
    chunks = manager.chunk_by_tokens(text, chunk_size=1000, overlap=100)

    print(f"\nChunks created: {len(chunks)}")

    for i, chunk in enumerate(chunks[:3], 1):  # Show first 3
        tokens = manager.count_tokens(chunk)
        print(f"\nChunk {i}:")
        print(f"  Tokens: {tokens}")
        print(f"  Characters: {len(chunk)}")
        print(f"  Preview: {chunk[:100]}...")


def demo_model_comparison():
    """Demo 5: Compare different models"""
    print("\n\n" + "=" * 70)
    print("DEMO 5: Model Comparison")
    print("=" * 70)

    text = "This is a test sentence. " * 100

    models = [
        "claude-3-5-sonnet-20241022",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
        "gemini-1.5-pro",
    ]

    print(f"\nText: {len(text):,} characters\n")

    for model in models:
        manager = TokenManager(model=model)
        token_count = manager.count_tokens(text)

        print(f"{model}:")
        print(f"  Tokens: {token_count:,}")
        print(f"  Max limit: {manager.max_tokens:,}")
        print(f"  Safe limit: {manager.safe_max_tokens:,}")
        print(f"  Within limit: {token_count <= manager.safe_max_tokens}")
        print()


def demo_validate():
    """Demo 6: Text validation"""
    print("\n\n" + "=" * 70)
    print("DEMO 6: Text Validation")
    print("=" * 70)

    # Test with different text sizes
    test_cases = [
        ("Small text", "Hello world! " * 10),
        ("Medium text", "Lorem ipsum. " * 1000),
        ("Large text", "Testing validation. " * 10000),
    ]

    for name, text in test_cases:
        is_valid, error = TokenManager.validate_text_length(text, "gpt-4-turbo")

        print(f"\n{name}:")
        print(f"  Characters: {len(text):,}")
        print(f"  Valid: {is_valid}")
        if error:
            print(f"  Message: {error[:100]}...")


def main():
    """Run all demos"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "TOKEN MANAGER DEMO" + " " * 31 + "║")
    print("╚" + "═" * 68 + "╝")

    try:
        demo_basic_counting()
        demo_token_info()
        demo_truncation()
        demo_chunking()
        demo_model_comparison()
        demo_validate()

        print("\n\n" + "=" * 70)
        print("✓ All demos completed successfully!")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
