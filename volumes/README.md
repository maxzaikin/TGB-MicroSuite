# 📁 `volumes/` — Persistent Storage Structure

This directory contains **volume mounts** used by Docker containers across the project.  
It is **ignored by Git** (via `.gitignore`) to avoid committing large or sensitive data, but the folder structure is preserved to help contributors get started quickly.

> ⚠️ **Note:** The contents of these folders are generated automatically by the containers at runtime, or manually populated by the user when needed (e.g., uploading documents for vectorization).

---

## 📦 Folder Overview

volumes/
├── arag-db/ # 🐘 PostgreSQL database volume for A-RAG service
├── gateway-db/ # 🔐 PostgreSQL volume for the Gateway service (Auth, API Keys)
├── models/ # 🤖 LLMs and embeddings stored locally (optional/manual)
├── rag-db/ # 🧠 ChromaDB persistent vector database storage
├── rag-source-docs/ # 📄 Source documents for vector indexing (PDFs, Markdown, etc.)
│ └── test_document_v1.md
└── redis-db/ # ⚡ Redis persistence (dump.rdb and cache state)
└── dump.rdb

## 🛠 How It Works

- Docker containers mount these folders as **persistent volumes**.
- Services like `Chroma`, `Redis`, and `PostgreSQL` automatically write data into their respective folders during runtime.
- The folder `rag-source-docs/` can be populated manually with documents (e.g., `.md`, `.pdf`, `.txt`) that will be **indexed into vectors** by the RAG ingestion pipeline.

---

## 🧾 Usage Tips

- You **do not need to create these folders manually** — they are either created by Docker when volumes mount, or you can run a helper script (see `scripts/init-volumes.sh`).
- To add your own source data for vector search:
  1. Drop documents into `volumes/rag-source-docs/`
  2. Trigger the ingestion pipeline (e.g., via CLI or background service)
- These folders are **excluded from Git tracking**, but the structure is preserved via `.gitkeep` files and this `README`.

---

## 🔒 Why Not Commit the Contents?

- Database dumps and model files can be **very large**, unnecessary, and potentially contain **sensitive data**.
- To avoid polluting the repo and risking credential/data leaks, only **structure is retained** — not the actual files.

🤝 Contributing

Please do not commit real database files or model binaries into this directory.
If you need to share example documents, include them under rag-source-docs/ and keep them lightweight and safe.
