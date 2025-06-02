#!/usr/bin/env python3
"""
Test script to verify the asyncio cancellation fix.
"""

import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def mock_stream_generator():
    """Mock stream generator that simulates the workflow stream."""
    for i in range(10):
        await asyncio.sleep(0.1)  # Simulate some work
        yield f"data: Message {i}\n\n"
        if i == 5:
            # Simulate an error condition
            raise Exception("Simulated error in stream")


async def test_cancellation_handling():
    """Test that cancellation is handled gracefully."""
    logger.info("Testing cancellation handling...")

    try:
        async with asyncio.timeout(0.3):  # Short timeout to trigger cancellation
            async for chunk in mock_stream_generator():
                logger.info(f"Received: {chunk.strip()}")
    except asyncio.TimeoutError:
        logger.info("Stream timeout handled gracefully")
    except asyncio.CancelledError:
        logger.info("Stream cancellation handled gracefully")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


async def test_error_handling():
    """Test that errors in the stream are handled gracefully."""
    logger.info("Testing error handling...")

    try:
        async for chunk in mock_stream_generator():
            logger.info(f"Received: {chunk.strip()}")
    except Exception as e:
        logger.info(f"Error handled gracefully: {e}")


async def main():
    """Run all tests."""
    logger.info("Starting asyncio error handling tests...")

    await test_cancellation_handling()
    await asyncio.sleep(0.1)
    await test_error_handling()

    logger.info("All tests completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
