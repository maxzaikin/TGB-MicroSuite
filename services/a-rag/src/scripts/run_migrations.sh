#!/bin/bash
# file: services/a-rag/scripts/run-migrations.sh

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- Running Database Migrations ---"

# Alembic needs to be able to import the source code.
# We ensure the script is run from the service's root and that `src` is in PYTHONPATH.
# Примечание: Эта строка нужна, если вы запускаете скрипт не из Docker-контейнера.
# В Docker-контейнере рабочая директория и так будет правильной.
export PYTHONPATH=${PYTHONPATH}:$(pwd)/src

# Run the alembic upgrade command.
# The --sql flag is useful for dry-runs to see what SQL will be executed.
# Уберите --sql для реального выполнения.
alembic -c src/storage/rel_db/alembic.ini upgrade head

echo "--- Migrations applied successfully ---"