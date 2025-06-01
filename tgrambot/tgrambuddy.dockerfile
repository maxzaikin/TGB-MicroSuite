FROM        python:3.12-slim-bookworm

LABEL       key="Maks V. Zaikin"

ENV         PYTHONUNBUFFERED=1

RUN         apt-get update && apt-get install -y \
                libgl1-mesa-glx \
                libglib2.0-0 \
                && rm -rf /var/lib/apt/lists/*

WORKDIR     /app
COPY        pyproject.toml ./
COPY        alembic.ini ./
COPY        migrations/ ./migrations/
RUN         pip install uv
RUN         uv pip install --system --no-cache-dir .

COPY        src ./src
COPY        data/ ./data/
COPY        main.py ./

WORKDIR     /app
ENTRYPOINT  ["python", "main.py"]