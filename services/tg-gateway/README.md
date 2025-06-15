# Service: Telegram Gateway (`tg-gateway-service`)

[![Python Version](https://img.shields.io/badge/Python-3.12-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.x-brightgreen.svg?logo=telegram&logoColor=white)](https://aiogram.dev/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-blue.svg)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/Alembic-1.13-orange.svg)](https://alembic.sqlalchemy.org/en/latest/)
[![Ruff](https://img.shields.io/badge/Linter-Ruff-purple.svg)](https://github.com/astral-sh/ruff)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-blue.svg?logo=docker&logoColor=white)](https://www.docker.com/)

This directory contains the source code for the **Telegram Gateway Service**. It is a lightweight, asynchronous Telegram bot built with **Aiogram 3.x** that serves as the primary entry point for all user interactions originating from the Telegram platform.

## 🎯 Service Responsibilities

This service acts as a "thin" gateway, with its responsibilities strictly limited to:

1.  **Handling Telegram API Updates:** Receiving all incoming events from Telegram, such as messages, commands, and callbacks.
2.  **User Onboarding:** Greeting new users and creating a basic client profile in its local database.
3.  **Routing to Backend:** Acting as a proxy by forwarding user text queries to the `a-rag-api` service for processing.
4.  **Delivering Responses:** Returning the processed responses from the A-RAG system back to the user in Telegram.

The service deliberately **avoids** complex business logic, which is delegated entirely to the `a-rag-api`.

---

## 🏛️ Architectural Design

The service follows a clean, domain-driven structure, mirroring the principles of the `a-rag-api` but adapted for an event-driven bot architecture.

### Core Principles

-   **Feature-Sliced Structure:** The core bot logic is organized by business features (e.g., `onboarding`, `rag_chat`) located in `src/bot/features/`. Each feature is a self-contained "slice" with its own router and handlers.
-   **Dependency Injection:** Shared services like the database adapter and localization service are initialized once and injected into handlers via Aiogram's `workflow_data` and middleware, promoting loose coupling and high testability.
-   **Clear Separation of Concerns:** The code is strictly layered. Handlers (`handler.py`) contain business logic, routers (`router.py`) handle event filtering, and the application entry point (`app/main.py`) orchestrates the assembly.

### Internal Component Flow

This diagram illustrates how a Telegram update is processed by the service.

```mermaid
graph TD
    subgraph "External World"
        TelegramAPI["Telegram API"]
        AragAPI["a-rag-api Service"]
    end

    subgraph "Telegram Gateway Service"
        direction LR
        
        subgraph "1. App & Dispatcher"
            Main["app/main.py<br>(Bot Entry Point)"]
            Middleware["bot/middleware/*"]
        end

        subgraph "2. Feature Handlers"
            Onboarding["features/onboarding/*"]
            RagChat["features/rag_chat/*"]
        end

        subgraph "3. Core & Storage"
            Core["core/*<br>(Config, Localization)"]
            Storage["storage/rel_db/*<br>(SQLAlchemy)"]
            DB[("Database<br>(SQLite)")]
        end
    end

    %% Define connections
    TelegramAPI -- "Webhook/Polling Update" --> Main
    Main -- "Passes to Dispatcher" --> Middleware
    Middleware -- "Injects Dependencies" --> Onboarding
    Middleware -- "Injects Dependencies" --> RagChat
    
    RagChat -- "HTTP Request" --> AragAPI
    AragAPI -- "HTTP Response" --> RagChat
    
    Onboarding -- "Uses" --> Storage
    Storage -- "Reads/Writes" --> DB
    
    Onboarding --> Core
    RagChat --> Core
    Storage --> Core

    %% Style definitions
    style Main fill:#cde4ff,stroke:#333,stroke-width:2px
    style Middleware fill:#fdebd0,stroke:#333,stroke-width:2px
    style Onboarding fill:#d5f5e3,stroke:#333,stroke-width:2px
    style RagChat fill:#d5f5e3,stroke:#333,stroke-width:2px
    style Core fill:#e8daef,stroke:#333,stroke-width:2px
    style Storage fill:#e8daef,stroke:#333,stroke-width:2px
    style DB fill:#f5b7b1,stroke:#333,stroke-width:2px
```

🛠️ Local Development

This service is designed to be developed locally in an isolated virtual environment managed by uv.
1. Prerequisites

    Python 3.12+

    uv installed (pip install uv)

2. Environment Setup

All commands should be run from this directory (services/tg-gateway/).

    Create & Activate Virtual Environment:

    uv venv
# For Windows: .\.venv\Scripts\Activate.ps1
# For macOS/Linux: source .venv/bin/activate

Install All Dependencies:
This command installs both production and development (ruff, pytest) dependencies.

uv pip install -e ".[dev]"

    You must provide your BOT_TOKEN in the .env file for the bot to start.

3. Running the Bot

We use a custom CLI tool, gateway, defined in pyproject.toml for all common tasks.

    Start the bot:
    gateway start

        The bot will start polling for updates from Telegram. Press Ctrl+C to stop it gracefully.

4. Database Migrations

Database schema changes are managed by Alembic.

    Apply all migrations:
    This should be done after setting up the environment for the first time or after pulling changes that include new migrations.
    gateway migrate

    Create a new migration:
After changing your SQLAlchemy models in src/storage/rel_db/models.py, generate a new migration script:
gateway revision -m "your_descriptive_migration_message"

    Always review the generated script before applying it.

5. Running Tests & Code Quality

    Run linter and formatter checks:
    ruff check . && ruff format --check .

    Run tests (once implemented):
    gateway test