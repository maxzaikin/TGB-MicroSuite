"""
file: services/a-rag/src/core/profiling.py

A simple profiling utility for measuring and logging execution time.

This module provides a context manager to easily wrap code blocks and
log how long they take to execute. It's useful for identifying performance
bottlenecks during development without introducing heavy dependencies.
"""

import logging
import time
from contextlib import contextmanager
from typing import Generator


@contextmanager
def log_execution_time(stage_name: str) -> Generator[None, None, None]:
    """
    A context manager to log the execution time of a specific code block.

    Logs a message upon entering the block and another upon exiting, including
    the total duration in seconds.

    Args:
        stage_name: A descriptive name for the code block being profiled,
                    which will be used in the log messages.

    Example:
        with log_execution_time("Database Query"):
            # code to profile...
    """
    logging.info(f"[PROFILE] ==> Entering stage: {stage_name}")
    start_time = time.perf_counter()
    
    try:
        yield
    finally:
        end_time = time.perf_counter()
        duration = end_time - start_time
        logging.info(
            f"[PROFILE] <== Exiting stage: {stage_name}. Duration: {duration:.4f} seconds."
        )
