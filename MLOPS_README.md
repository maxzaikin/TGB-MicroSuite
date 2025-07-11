# MLOps Pipelines Guide for TGB-MicroSuite

Welcome to the MLOps guide for the `a-rag` service. This document explains the architecture, purpose, and usage of our automated Machine Learning pipelines, orchestrated by **ZenML**.

## 🎯 Philosophy: From Scripts to Pipelines

Our core principle is to treat ML processes not as one-off scripts, but as versioned, reproducible, and automated software components. The previous manual `ingest.py` script was brittle and lacked observability. By migrating to ZenML, we gain:

-   **Reproducibility:** Every pipeline run is tracked, including the code version, parameters, and inputs/outputs (artifacts).
-   **Observability:** A central dashboard (`http://localhost:8237`) provides a complete history of all runs, logs for each step, and visualization of the pipeline structure (DAG).
-   **Automation:** These pipelines are the foundation for our future CI/CD/CT (Continuous Integration/Delivery/Training) workflows.
-   **Modularity & Reusability:** Each step in a pipeline is an independent, reusable function that can be composed into different pipelines.

## 🏗️ MLOps Architecture

Our MLOps capabilities are integrated directly into the `a-rag` microservice and orchestrated by a self-hosted ZenML server managed via `docker-compose.infra.yml`.

```mermaid
graph TD
    subgraph "Developer & CI-CD"
        A["1. Trigger Run: `uv run python pipelines/run_pipeline.py`"]
    end

    subgraph "ZenML Server (Docker Container)"
        B["2. ZenML Orchestrator"]
    end

    subgraph "Execution Logic (within a-rag service)"
        C["@pipeline: feature_ingestion_pipeline"]
        D["@step: load_documents"]
        E["@step: get_vector_store"]
        F["@step: index_documents"]
    end

    subgraph "External Infrastructure"
        G["Source Docs on Disk"]
        H["ChromaDB (Docker Container)"]
    end

    A --> B
    B -->|Executes Pipeline| C
    C --> D
    D -->|Documents| F
    C --> E
    E -->|VectorStore Client| F
    
    D -->|Reads from| G
    E -->|Connects to| H
    F -->|Writes to| H
```

Workflow Explanation:

    A developer or a CI/CD job triggers a pipeline run via the central CLI entry point (pipelines/run_pipeline.py).

    The ZenML client communicates the request to the ZenML Server, which begins orchestrating the pipeline.

    The pipeline definition (feature_ingestion_pipeline) dictates the execution order of the steps.

    Each step (@step) is executed as a tracked job.

        load_documents reads files from the local volume.

        get_vector_store connects to the existing ChromaDB container, reusing connection settings from src/core/config.py.

        index_documents takes the loaded documents and the vector store client, performs embedding, and ingests the data.

    All results, logs, and artifacts are tracked by the ZenML Server and visible in the UI.


## 🛠️ Setup & Configuration

### Step 1: Launch Core Infrastructure

From the project root, ensure all services are running. This command starts ChromaDB, Redis, and our ZenML Server.

```bash
docker-compose -f docker-compose.infra.yml up -d
```

### Step 2: Set Up the a-rag Service Environment

Navigate to the a-rag service directory. All subsequent commands should be run from here. Then, activate its virtual environment and install dependencies.

```bash
cd services/a-rag

# Create/activate virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip sync pyproject.toml
```

### Step 3: Connect Your Local Client to the ZenML Server (One-Time Setup)

**This is a critical one-time setup step**. You must connect your local ZenML client (which you just installed) to the ZenML Server running in Docker. This tells your client where to send all pipeline information.

Once this is done, the configuration is saved locally, and all future pipeline runs will automatically be sent to and tracked by your local server.

```bash
# Ensure your (a-rag) venv is active
(a-rag) $ ды
```
[!NOTE]
The zenml connect command is being deprecated. You might see a warning suggesting to use zenml login. In recent versions, zenml connect might automatically open a browser window for authentication. Simply follow the on-screen instructions. A successful connection is the end goal.

You should see a confirmation message like: ✅ Successfully connected to ZenML server.


## ▶️ Running the Feature Ingestion Pipeline

This pipeline is the replacement for the old ingest.py script. It loads documents from a directory and indexes them into ChromaDB.

To run the pipeline, use the pipelines/run_pipeline.py script from within the services/a-rag directory.

```bash
(a-rag) uv run python -m  pipelines.run_pipeline --source-dir ../../volumes/rag-source-docs  --collection rag_documentation_docker
```

Arguments:

    --source-dir (required): Path to the directory containing your source documents (e.g., .md, .txt files). The path should be relative to the a-rag service root.

    --collection (optional): The name of the ChromaDB collection to create or use. Defaults to rag_documentation_v2.

**Monitoring the Pipeline**

After triggering a run, you can monitor its progress in real-time:

    Open your browser and go to http://localhost:8237.

    Navigate to the Pipelines -> All Runs tab.

    You will see your rag_feature_ingestion_pipeline run. Click on it to see the graph, check the status of each step, and view detailed logs.

This setup provides a robust, professional framework for managing our ML workflows.

```bash
zenml stack describe
zenml artifact-store describe default
```

**Create newartifacts store**
zenml artifact-store register local_store_docker \
  --flavor local \
  --path=/home/zai11972/projects/TGB-MicroSuite/volumes/zenml-db

**Create new Stack with new store**
zenml stack register local_stack_docker \
  --artifact-store=local_store_docker \
  --orchestrator=default

zenml stack set local_stack_docker

docker exec -it tgb-local-zenml /bin/bash

(a-rag) zai11972@Descartes:~/projects/TGB-MicroSuite/services/a-rag$ python -m pipelines.run_pipeline   --source-dir ../../volumes/zenml-db/rag-source-docs   --collection rag_documentation_docker

zenml connect --url http://127.0.0.1:8237 --username default

 # ZenML database and metadata store
      - ./volumes/zenml-db:/zenml/.zenconfig/local_stores/default_zen_store
      - ./volumes/zenml-db:/home/zenml/.config/zenml

      # Folder with documents (must be accessible for ingestion)
      - ./volumes/zenml-db/rag-source-docs:/rag-source-docs

      # 🔥 Critical: absolute path for full compatibility with pipeline host writes
      # Left part is path on a host system (WSL) : Right path is path inside docker
      - /home/[your_user_name]]/projects/TGB-MicroSuite/volumes/zenml-db:/home/[your_user_name]/projects/TGB-MicroSuite/volumes/zenml-db
