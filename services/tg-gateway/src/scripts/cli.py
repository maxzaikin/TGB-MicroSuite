# file: services/tg-gateway/scripts/cli.py
"""
A command-line interface (CLI) for managing common development tasks
for the tg-gateway service.
"""

import subprocess
import sys
from typing import Dict, List

COMMANDS: Dict[str, List[str]] = {
    "start": [
        "python",
        "-m",
        "src.app.main",  # We will use direct python call for a non-server app
    ],
    "migrate": ["alembic", "-c", "src/storage/rel_db/alembic.ini", "upgrade", "head"],
    "revision": [
        "alembic",
        "-c",
        "src/storage/rel_db/alembic.ini",
        "revision",
        "--autogenerate",
    ],
}


def main() -> None:
    """The main entry point for the CLI script."""
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("Error: Please specify a valid command.", file=sys.stderr)
        available_commands = ", ".join(COMMANDS.keys())
        print(f"Available commands: {available_commands}", file=sys.stderr)
        sys.exit(1)

    command_name = sys.argv[1]
    command_to_run = COMMANDS[command_name]

    extra_args = sys.argv[2:]
    command_to_run.extend(extra_args)

    print(f"--- Running command: {' '.join(command_to_run)} ---")

    try:
        subprocess.run(command_to_run, check=True)
        print(f"--- Command '{command_name}' finished successfully ---")
    except subprocess.CalledProcessError as e:
        print(
            f"--- Command '{command_name}' failed with exit code {e.returncode} ---",
            file=sys.stderr,
        )
        sys.exit(e.returncode)
    except FileNotFoundError:
        print(
            f"--- Error: Command '{command_to_run[0]}' not found. Is it installed in your venv? ---",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
