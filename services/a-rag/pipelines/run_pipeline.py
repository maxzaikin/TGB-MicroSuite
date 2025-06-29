"""
file: services/a-rag/pipelines/run_pipeline.py

# --- [ISSUE-26] Implement ZenML for MLOps Pipeline Management ---

Command-Line Interface (CLI) to run MLOps pipelines.

This script serves as the single entry point for triggering all ZenML
pipelines defined in this project. It ensures that pipelines are run
with the correct parameters and configurations.
"""
import argparse
import logging
from pathlib import Path

# Import the pipeline definition
from .feature_pipeline import feature_ingestion_pipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Constants ---
# We can still define a default collection name here.
DEFAULT_COLLECTION_NAME = "rag_documentation_v2" # v2 to avoid conflicts


def main():
    """Parses CLI arguments and runs the specified ZenML pipeline."""
    parser = argparse.ArgumentParser(
        description="Run MLOps pipelines for the a-rag service.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    
    # We can add sub-parsers later if we have more pipelines
    parser.add_argument(
        "--pipeline-name",
        type=str,
        default="feature_ingestion",
        choices=["feature_ingestion"], # Add more as we create them
        help="The name of the pipeline to run.",
    )
    
    # Arguments specific to the feature_ingestion_pipeline
    parser.add_argument(
        "--source-dir",
        type=Path,
        required=True,
        help="Path to the source directory for the ingestion pipeline.",
    )
    parser.add_argument(
        "--collection",
        type=str,
        default=DEFAULT_COLLECTION_NAME,
        help=f"ChromaDB collection name (Default: {DEFAULT_COLLECTION_NAME}).",
    )

    args = parser.parse_args()

    if args.pipeline_name == "feature_ingestion":
        logger.info(f"Triggering pipeline: '{feature_ingestion_pipeline.name}'...")
        # Here we call the pipeline function. ZenML takes over from here.
        feature_ingestion_pipeline(
            source_dir=args.source_dir,
            collection_name=args.collection,
        )
        logger.info("Pipeline run has been triggered successfully.")
        logger.info("Check your ZenML dashboard to monitor the execution.")
    else:
        logger.error(f"Unknown pipeline name: {args.pipeline_name}")


if __name__ == "__main__":
    main()