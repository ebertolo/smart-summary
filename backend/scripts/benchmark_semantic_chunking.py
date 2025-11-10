"""
Benchmark script for optimized summarization strategies
Tests performance improvements with semantic chunking and parallelization
"""

import asyncio
import time

from app.core.config import settings
from app.services.summarizer import SummarizerService
from app.services.text_processor import TextProcessor


def generate_test_text(size_kb: int, with_structure: bool = True) -> str:
    """
    Generate test text of specified size

    Args:
        size_kb: Target size in KB
        with_structure: If True, include markdown structure
    """
    target_chars = size_kb * 1024

    if with_structure:
        # Generate structured markdown text
        text = "# Document Title\n\n"
        section = 1

        while len(text) < target_chars:
            text += f"\n## Section {section}\n\n"

            # Add paragraphs
            for para in range(5):
                text += f"This is paragraph {para + 1} in section {section}. "
                text += "It contains multiple sentences with meaningful content. "
                text += "The semantic chunker should respect these natural boundaries. "
                text += "This helps maintain context when splitting large documents. "
                text += "\n\n"

            section += 1

        return text[:target_chars]
    else:
        # Generate plain text
        base = "This is test sentence number {}. "
        text = ""
        i = 0
        while len(text) < target_chars:
            text += base.format(i)
            i += 1

        return text[:target_chars]


async def benchmark_chunking():
    """Benchmark chunking performance"""
    print("\n" + "=" * 70)
    print("BENCHMARK 1: Chunking Performance")
    print("=" * 70)

    processor = TextProcessor()

    sizes = [50, 100, 200, 300]  # KB

    for size_kb in sizes:
        text = generate_test_text(size_kb, with_structure=True)

        # Benchmark semantic chunking
        start = time.time()
        chunks = await processor.split_into_chunks(
            text, max_size=settings.HIERARCHICAL_CHUNK_SIZE, strategy="hierarchical"
        )
        elapsed = time.time() - start

        print(f"\n{size_kb}KB text:")
        print(f"  Time: {elapsed:.3f}s")
        print(f"  Chunks created: {len(chunks)}")
        print(f"  Avg chunk size: {len(text) // len(chunks):,} chars")
        print(f"  Throughput: {size_kb / elapsed:.1f} KB/s")


async def benchmark_token_counting():
    """Benchmark token counting performance"""
    print("\n" + "=" * 70)
    print("BENCHMARK 2: Token Counting Performance")
    print("=" * 70)

    from app.services.token_manager import TokenManager

    manager = TokenManager(model=settings.LLM_MODEL)

    sizes = [50, 100, 200, 300]  # KB

    for size_kb in sizes:
        text = generate_test_text(size_kb, with_structure=False)

        start = time.time()
        token_count = manager.count_tokens(text)
        elapsed = time.time() - start

        print(f"\n{size_kb}KB text:")
        print(f"  Time: {elapsed:.3f}s")
        print(f"  Tokens: {token_count:,}")
        print(f"  Chars/Token ratio: {len(text) / token_count:.2f}")
        print(f"  Throughput: {token_count / elapsed:,.0f} tokens/s")


async def benchmark_chunk_strategies():
    """Compare old vs new chunking approach"""
    print("\n" + "=" * 70)
    print("BENCHMARK 3: Chunking Strategy Comparison")
    print("=" * 70)

    processor = TextProcessor()
    text_300k = generate_test_text(300, with_structure=True)

    # New semantic chunking (100K chunks)
    print("\n📊 NEW: Semantic Chunking (100K chunks)")
    start = time.time()
    new_chunks = await processor.split_into_chunks(
        text_300k, max_size=100000, strategy="hierarchical"
    )
    new_time = time.time() - start

    print(f"  Chunks created: {len(new_chunks)}")
    print(f"  Time: {new_time:.3f}s")
    print(
        f"  Estimated LLM calls: {len(new_chunks)} + 1 combine = {len(new_chunks) + 1}"
    )

    # Old approach simulation (2K chunks)
    print("\n📊 OLD: Simple Chunking (2K chunks)")
    start = time.time()
    old_chunks = await processor.split_into_chunks(
        text_300k, max_size=2000, strategy="hierarchical"
    )
    old_time = time.time() - start

    print(f"  Chunks created: {len(old_chunks)}")
    print(f"  Time: {old_time:.3f}s")
    print(
        f"  Estimated LLM calls: {len(old_chunks)} + 1 combine = {len(old_chunks) + 1}"
    )

    # Calculate improvement
    print("\n📈 IMPROVEMENT:")
    print(
        f"  Chunks reduction: {len(old_chunks)} → {len(new_chunks)} ({len(new_chunks)/len(old_chunks)*100:.1f}%)"
    )
    print(f"  LLM calls reduction: {len(old_chunks) + 1} → {len(new_chunks) + 1}")

    # Estimated time savings (assuming 2s per LLM call)
    old_estimated = (len(old_chunks) + 1) * 2  # Sequential
    new_estimated = (
        (len(new_chunks) // settings.MAX_PARALLEL_CHUNKS + 1) * 2
    ) + 2  # Parallel + combine

    print(f"  Estimated time (2s/call):")
    print(f"    Old (sequential): ~{old_estimated}s ({old_estimated/60:.1f} min)")
    print(f"    New (parallel): ~{new_estimated}s")
    print(f"    Speed improvement: {old_estimated/new_estimated:.1f}x faster")


async def benchmark_parallel_simulation():
    """Simulate parallel processing benefit"""
    print("\n" + "=" * 70)
    print("BENCHMARK 4: Parallel Processing Simulation")
    print("=" * 70)

    async def simulate_llm_call(duration: float = 2.0):
        """Simulate a LLM API call"""
        await asyncio.sleep(duration)
        return f"Summary chunk"

    num_chunks = 3
    call_duration = 2.0

    # Sequential processing
    print(f"\n⏱️ Sequential Processing ({num_chunks} chunks):")
    start = time.time()
    for i in range(num_chunks):
        await simulate_llm_call(call_duration)
    sequential_time = time.time() - start
    print(f"  Time: {sequential_time:.1f}s")

    # Parallel processing
    print(f"\n⚡ Parallel Processing ({num_chunks} chunks):")
    start = time.time()
    tasks = [simulate_llm_call(call_duration) for _ in range(num_chunks)]
    await asyncio.gather(*tasks)
    parallel_time = time.time() - start
    print(f"  Time: {parallel_time:.1f}s")

    # Calculate improvement
    print(f"\n📈 IMPROVEMENT:")
    print(f"  Speedup: {sequential_time/parallel_time:.1f}x faster")
    print(f"  Time saved: {sequential_time - parallel_time:.1f}s")


async def benchmark_full_pipeline():
    """Benchmark the full summarization pipeline"""
    print("\n" + "=" * 70)
    print("BENCHMARK 5: Full Pipeline Test (No API)")
    print("=" * 70)

    processor = TextProcessor()
    from app.services.token_manager import TokenManager

    text_300k = generate_test_text(300, with_structure=True)

    print(f"\n📄 Input: 300KB structured text")
    print(f"  Characters: {len(text_300k):,}")

    # Token counting
    print("\n1️⃣ Token Counting...")
    start = time.time()
    manager = TokenManager(model=settings.LLM_MODEL)
    token_info = manager.get_token_info(text_300k)
    token_time = time.time() - start

    print(f"  Tokens: {token_info['token_count']:,}")
    print(f"  Within limit: {token_info['within_limit']}")
    print(f"  Time: {token_time:.3f}s")

    # Semantic chunking
    print("\n2️⃣ Semantic Chunking...")
    start = time.time()
    chunks = await processor.split_into_chunks(
        text_300k, max_size=settings.HIERARCHICAL_CHUNK_SIZE, strategy="hierarchical"
    )
    chunk_time = time.time() - start

    print(f"  Chunks: {len(chunks)}")
    print(f"  Time: {chunk_time:.3f}s")

    # Calculate total pipeline time (excluding LLM calls)
    print("\n⏱️ TOTAL PIPELINE TIME (preprocessing):")
    total_time = token_time + chunk_time
    print(f"  {total_time:.3f}s")

    # Estimate with LLM calls
    print("\n🔮 ESTIMATED WITH LLM CALLS:")
    parallel_batches = (
        len(chunks) + settings.MAX_PARALLEL_CHUNKS - 1
    ) // settings.MAX_PARALLEL_CHUNKS
    estimated_llm_time = (parallel_batches * 2) + 2  # 2s per batch + 2s combine
    estimated_total = total_time + estimated_llm_time

    print(f"  Parallel batches: {parallel_batches}")
    print(f"  LLM time estimate: ~{estimated_llm_time}s")
    print(f"  Total estimate: ~{estimated_total:.1f}s")

    # Compare with old approach
    old_chunks = 150  # 300K / 2K = 150
    old_estimated = old_chunks * 2  # Sequential

    print(f"\n📊 vs OLD APPROACH:")
    print(f"  Old: ~{old_estimated}s ({old_estimated/60:.1f} min)")
    print(f"  New: ~{estimated_total:.1f}s")
    print(f"  Improvement: {old_estimated/estimated_total:.1f}x faster! 🚀")


async def main():
    """Run all benchmarks"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "SEMANTIC CHUNKING BENCHMARKS" + " " * 25 + "║")
    print("╚" + "═" * 68 + "╝")

    try:
        await benchmark_chunking()
        await benchmark_token_counting()
        await benchmark_chunk_strategies()
        await benchmark_parallel_simulation()
        await benchmark_full_pipeline()

        print("\n" + "=" * 70)
        print("✅ All benchmarks completed successfully!")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ Error running benchmarks: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
