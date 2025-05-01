FROM        python:3.12-slim-bookworm

LABEL       key="Maks V. Zaikin"

ENV         PYTHONUNBUFFERED=1

WORKDIR     /app
COPY        pyproject.toml ./
RUN         pip install uv
RUN         uv pip install --system --no-cache-dir .

COPY        src ./src
COPY        main.py ./

WORKDIR     /app
ENTRYPOINT  ["python", "main.py"]