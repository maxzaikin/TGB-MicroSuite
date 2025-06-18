# Infrastructure: Redis Service

[![Redis](https://img.shields.io/badge/Redis-7.2-DC382D.svg?logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)

This directory contains the configuration and documentation for the **Redis** instance used within the TGB-MicroSuite platform.

## 🎯 Role in the Architecture

Redis serves as a high-performance, in-memory key-value store. In our architecture, its primary responsibility is to provide **short-term conversational memory** for the `a-rag-api` service.

### Key Responsibilities:

1.  **Dialogue History Cache:** For each user session, Redis stores a list of the most recent user messages and assistant responses. This allows the LLM to understand the context of the ongoing conversation.
2.  **Performance:** By storing this frequently accessed data in memory, Redis ensures that retrieving conversation history is nearly instantaneous, preventing it from becoming a bottleneck.
3.  **Scalability:** As a standalone service, our Redis instance can be scaled or configured independently of the services that use it.

## ⚙️ Configuration (`redis.conf`)

The `redis.conf` file in this directory contains our custom settings for the Redis server. The most important configuration is persistence:

```conf
# --- Persistence ---
# Save the DB on disk if at least 1 key has changed in the last 60 seconds.
save 60 1

# The filename for the database dump.
dbfilename dump.rdb
```

This configuration strikes a balance between performance and durability. It ensures that our conversation history is periodically saved to disk, preventing data loss if the container restarts.

## 🐳 WSL2 Docker Environment Setup

For a consistent and high-performance development experience on Windows, it is **highly recommended** to run Docker Engine directly within your WSL2 distribution (e.g., Ubuntu). This avoids common networking issues between Windows and WSL2.

Follow these steps **one time** inside your WSL2 Ubuntu terminal to set up the environment.

1.  **Update Package Lists:**
    Ensure your package manager has the latest list of available software.
    ```bash
    sudo apt-get update
    ```

2.  **Install Prerequisites:**
    Install packages that allow `apt` to use a repository over HTTPS.
    ```bash
    sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
    ```

3.  **Add Docker’s Official GPG Key:**
    This verifies the authenticity of the Docker packages.
    ```bash
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    ```

4.  **Set Up the Docker Repository:**
    Add the stable Docker repository to your system's sources.
    ```bash
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    ```

5.  **Install Docker Engine & Compose Plugin:**
    Install the latest versions of Docker Engine, CLI, containerd, and the Compose plugin.
    ```bash
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    ```

6.  **Add Your User to the `docker` Group (Crucial Step):**
    This allows you to run Docker commands without using `sudo`.
    ```bash
    sudo usermod -aG docker $USER
    ```
    > [!IMPORTANT]
    > After running this command, you **must close and reopen your WSL2 terminal** for the group changes to take effect.

7.  **Verify Installation:**
    In a **new** WSL2 terminal, run the following commands to ensure everything is working correctly:
    ```bash
    docker --version
    docker compose version
    ```
    You should see the versions printed without any permission errors. Your WSL2 environment is now fully prepared for Docker development.
    

🚀 Running the Service

The Redis service is managed by Docker and defined in the root docker-compose.infra.yml file.
Local Development (inside WSL2)

To run Redis as a standalone container for local development, use the following command from the root of the monorepo:

```bash
docker compose -f docker-compose.infra.yml up -d redis
```

-f docker-compose.infra.yml: Specifies the infrastructure-only compose file.

-d: Runs the container in detached (background) mode.

This will start a Redis container named tgb-local-redis, which will be accessible from within the WSL2 environment at redis://localhost:6379.

💾 Data Persistence

The service is configured to persist its data on the host machine to survive container restarts and system reboots.

    Redis Database Files (.rdb) are stored in: volumes/redis-db/

This volume is mounted into the container at the /data path, as defined in docker-compose.infra.yml. This volumes directory is explicitly excluded from Git via the root .gitignore file.
🕵️‍♂️ Inspecting the Cache

During development, it's often useful to inspect the data stored in Redis directly. You can do this by accessing the redis-cli (Command-Line Interface) inside the running container.

Ensure the container is running:

```bash
docker ps
```

You should see tgb-local-redis in the list.

Connect to redis-cli:

```bash
docker exec -it tgb-local-redis redis-cli
```