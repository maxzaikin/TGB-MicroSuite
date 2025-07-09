# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-06-29

### Added
- **Introduced MLOps Orchestration with ZenML:** Integrated a self-hosted ZenML server into the core infrastructure (`docker-compose.infra.yml`) to manage and track ML workflows.
- **New Reproducible Data Ingestion Pipeline:** Implemented the `feature_ingestion_pipeline`, a formal, multi-step ZenML pipeline to replace the previous manual script. This provides full reproducibility and observability for our RAG data processing.
- **Persistent MLOps Metadata:** Added a dedicated Docker volume (`zenml-db`) to ensure all pipeline run history, artifacts, and metadata are persisted across container restarts.
- **Detailed MLOps Documentation:** Created a new `MLOPS_README.md` file with a complete guide on the pipeline architecture and usage instructions.

### Changed
- **Data Ingestion Workflow:** The process for ingesting documents into the RAG knowledge base has been fundamentally changed. It is now exclusively managed by the new ZenML pipeline, ensuring all data operations are versioned and tracked.

### Fixed
- **Documentation Rendering:** Corrected Mermaid diagram syntax in `MLOPS_README.md` to prevent `Unsupported markdown` warnings on GitHub.

### Removed
- **Legacy Ingestion Script:** Deleted the old `scripts/ingest.py` script and its associated `README-ingest.md` to eliminate redundancy and create a single source of truth for data ingestion.