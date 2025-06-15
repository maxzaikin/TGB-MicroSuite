# file: services/a-rag/scripts/cli.py

"""
A command-line interface (CLI) for managing common development tasks
for the a-rag service.

This script provides shortcuts for frequent operations like running database
migrations, starting the development server, and running tests. It acts as a
single entry point defined in `pyproject.toml` under `[project.scripts]`.

Usage:
  arag <command> [args...]

Example:
  arag migrate
  arag dev-server
  arag revision -m "add user table"
"""

import subprocess
import sys
from typing import Dict, List

# A dictionary mapping simple command names to their full shell commands.
# This is the single source of truth for all management commands.
COMMANDS: Dict[str, List[str]] = {
    "migrate": ["alembic", "-c", "src/storage/rel_db/alembic.ini", "upgrade", "head"],
    "revision": [
        "alembic",
        "-c",
        "src/storage/rel_db/alembic.ini",
        "revision",
        "--autogenerate",
    ],
    "test": ["pytest"],
    "dev-server": ["uvicorn", "src.app.main:app", "--reload"],
}


def main() -> None:
    """
    The main entry point for the CLI script.

    Parses command-line arguments, finds the corresponding command from the
    COMMANDS dictionary, and executes it using subprocess.
    """
    # Check if a command was provided.
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("Error: Please specify a valid command.", file=sys.stderr)
        available_commands = ", ".join(COMMANDS.keys())
        print(f"Available commands: {available_commands}", file=sys.stderr)
        sys.exit(1)

    command_name = sys.argv[1]
    command_to_run = COMMANDS[command_name]

    # Append any additional arguments passed to the script (e.g., migration message).
    extra_args = sys.argv[2:]
    command_to_run.extend(extra_args)

    print(f"--- Running command: {' '.join(command_to_run)} ---")

    # Execute the command using subprocess.
    try:
        # `check=True` will raise a CalledProcessError if the command returns a non-zero exit code.
        subprocess.run(command_to_run, check=True)
        print(f"--- Command '{command_name}' finished successfully ---")
    except subprocess.CalledProcessError as e:
        # Handle cases where the command fails.
        print(
            f"--- Command '{command_name}' failed with exit code {e.returncode} ---",
            file=sys.stderr,
        )
        sys.exit(e.returncode)
    except FileNotFoundError:
        # Handle cases where the command itself (e.g., 'alembic') is not found.
        print(
            f"--- Error: Command '{command_to_run[0]}' not found. Is it installed in your venv? ---",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
