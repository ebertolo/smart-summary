"""
Summary routes with streaming support
"""

import asyncio
import json
import time
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.core.security import get_current_user
from app.models.schemas import SummaryRequest, SummaryResponse
from app.services.summarizer import SummarizerService

router = APIRouter()


@router.post("/summarize")
async def summarize_text_streaming(
    request: SummaryRequest, current_user: dict = Depends(get_current_user)
):
    """
    Generate AI-powered text summary with real-time streaming (SSE).

    **Authentication Required:** Yes (Bearer token)

    **Parameters:**
    - `text`: Text to summarize (min: 100 chars, max: 2M chars)
    - `strategy`: Summarization approach
      - `simple`: Fast, single-pass summary
      - `hierarchical`: Multi-level, divide-and-conquer
      - `detailed`: Deep analysis with key points
    - `compression_ratio`: Target summary size (0.05 to 0.50)
      - `0.05`: Brief (5% of original)
      - `0.25`: Balanced (25% of original)
      - `0.50`: Detailed (50% of original)

    **Returns:** Server-Sent Events (SSE) stream
    - Progressive chunks of summary as they're generated
    - Real-time feedback for better UX
    - Completion signal when done

    **Use Case:** Interactive applications, live dashboards
    """

    print(
        f"[SUMMARY] Request received - strategy: {request.strategy}, text_size: {len(request.text)}, user: {current_user.get('username', 'unknown')}"
    )

    async def generate_summary_stream() -> AsyncGenerator[str, None]:
        """Generate summary with SSE streaming"""
        try:
            # Initialize service
            service = SummarizerService(
                strategy=request.strategy, compression_ratio=request.compression_ratio
            )

            # Stream summary chunks
            async for chunk in service.summarize_stream(request.text):
                data = json.dumps({"type": "content", "content": chunk, "done": False})
                yield f"data: {data}\n\n"

            # Send completion message
            final_data = json.dumps({"type": "complete", "done": True})
            yield f"data: {final_data}\n\n"

        except asyncio.CancelledError:
            # Client disconnected or request was cancelled
            # This is normal - just cleanup and exit gracefully
            print("[SUMMARY] Stream cancelled - client disconnected")
            raise  # Re-raise to properly cleanup

        except ValueError as e:
            # Handle input validation errors (e.g., prompt injection)
            error_data = json.dumps({"type": "error", "error": str(e), "done": True})
            yield f"data: {error_data}\n\n"

        except Exception as e:
            # Handle unexpected errors
            print(f"[SUMMARY] Error in stream: {str(e)}")
            error_data = json.dumps({"type": "error", "error": str(e), "done": True})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        generate_summary_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/summarize-sync", response_model=SummaryResponse)
async def summarize_text_sync(
    request: SummaryRequest, current_user: dict = Depends(get_current_user)
):
    """
    Generate AI-powered text summary (synchronous, single response).

    **Authentication Required:** Yes (Bearer token)

    **Parameters:**
    - `text`: Text to summarize (min: 100 chars, max: 2M chars)
    - `strategy`: Summarization approach (`simple`, `hierarchical`, `detailed`)
    - `compression_ratio`: Target summary size (0.05 to 0.50)

    **Returns:** Complete summary with metadata
    - `summary`: Generated summary text
    - `original_length`: Character count of input
    - `summary_length`: Character count of output
    - `compression_ratio`: Reduction percentage
    - `strategy_used`: Applied strategy
    - `processing_time`: Time taken in seconds

    **Use Case:** Batch processing, APIs, scheduled tasks

    **Note:** For texts >500KB, streaming endpoint is recommended.
    """
    print(
        f"[SUMMARY] Sync request received - strategy: {request.strategy}, text_size: {len(request.text)}, user: {current_user.get('username', 'unknown')}"
    )

    start_time = time.time()

    try:
        # Initialize service
        service = SummarizerService(
            strategy=request.strategy, compression_ratio=request.compression_ratio
        )

        # Get complete summary
        summary = await service.summarize(request.text)

        processing_time = time.time() - start_time

        return SummaryResponse(
            summary=summary,
            original_length=len(request.text),
            summary_length=len(summary),
            compression_ratio=len(summary) / len(request.text) if request.text else 0,
            strategy_used=request.strategy,
            processing_time=processing_time,
        )

    except ValueError as e:
        # Handle input validation errors (e.g., prompt injection)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


@router.get("/health")
async def summary_health_check():
    """
    Health check endpoint for summary service.

    **Authentication Required:** No

    **Returns:** Service status indicator

    **Use Case:** Monitoring, load balancers, readiness probes
    """
    return {"status": "healthy", "service": "summary"}
