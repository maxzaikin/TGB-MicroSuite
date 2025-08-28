# file: services/a-rag/pipelines/run_pipeline.py

"""
Command-Line Interface (CLI) to run MLOps pipelines.

This script serves as the single entry point for triggering all ZenML
pipelines. It is designed to be extensible and now supports both synchronous
and asynchronous pipeline definitions.
"""
import argparse
import asyncio
import inspect
import logging
from pathlib import Path

from pipelines.feature_ingestion_pipeline import feature_ingestion_pipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def setup_feature_ingestion_parser(parser: argparse.ArgumentParser):
    """Adds arguments specific to the feature_ingestion_pipeline."""
    parser.add_argument(
        "--source-dir",
        type=str,
        required=True,
        help="Path to the source directory containing documents to ingest.",
    )
    parser.add_argument(
        "--collection-name",
        type=str,
        default="main_knowledge_base",
        help="The name of the vector database collection to use.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=512,
        help="The target size for text chunks.",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=50,
        help="The overlap size between consecutive chunks.",
    )


def main():
    """Parses CLI arguments and runs the specified ZenML pipeline."""
    parser = argparse.ArgumentParser(
        description="Run MLOps pipelines for the a-rag service.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="pipeline_name", required=True)

    ingestion_parser = subparsers.add_parser(
        "feature-ingestion", 
        help="Runs the RAG feature ingestion pipeline."
    )
    setup_feature_ingestion_parser(ingestion_parser)
    ingestion_parser.set_defaults(
        func=feature_ingestion_pipeline, 
        pipeline_args=["source_dir", "collection_name", "chunk_size", "chunk_overlap"]
    )
    
    args = parser.parse_args()
    args_dict = vars(args)
    
    pipeline_kwargs = {
        key: args_dict[key] for key in args.pipeline_args if key in args_dict
    }

    pipeline_to_run = args.func

    logger.info(f"Triggering pipeline: '{pipeline_to_run.name}'...")
    logger.info(f"With parameters: {pipeline_kwargs}")

    # --- [FIX] Differentiate between sync and async pipelines ---
    if inspect.iscoroutinefunction(pipeline_to_run.entrypoint):
        # If the pipeline is async, run it within an asyncio event loop.
        logger.info("Detected an asynchronous pipeline. Running with asyncio.")
        asyncio.run(pipeline_to_run(**pipeline_kwargs))
    else:
        # If the pipeline is sync, run it directly.
        logger.info("Detected a synchronous pipeline. Running directly.")
        pipeline_to_run(**pipeline_kwargs)
    
    logger.info("Pipeline run has been triggered successfully.")
    logger.info("Check your ZenML dashboard to monitor the execution.")


if __name__ == "__main__":
    main()