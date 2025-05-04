FROM        python:3.12-slim-bookworm

LABEL       key="Maks V. Zaikin"

ENV         PYTHONUNBUFFERED=1

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