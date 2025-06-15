def run_database_migrations():
    """
    Run Alembic migrations to initialize or update the database schema.
  
    """
  

    try:
        db_url = settings.get_db_path()

        if not db_url:
            logging.error("ASYNCSQLITE_DB_URL not set in settings. Migrations canceled.")
            raise ValueError("ASYNCSQLITE_DB_URL is not configured")

        logging.info("Database URL: %s", db_url)

        if db_url.startswith("sqlite"):
            path_part = db_url.split("///")[-1]

            if path_part and path_part != ":memory:":
                db_file = Path(path_part)
                db_dir = db_file.parent
                db_dir.mkdir(parents=True, exist_ok=True)

                logging.info("DB folder has been created: %s", db_dir.resolve())

        os.environ["DATABASE_URL_ALEMBIC"] = db_url
        logging.info("DATABASE_URL_ALEMBIC: %s", db_url)
        logging.info("alembic upgrade head...")

        project_root_dir = Path(__file__).resolve().parent
        alembic_ini_path = project_root_dir / "alembic.ini"

        if not alembic_ini_path.exists():
            logging.warning("alembic.ini not found at: %s. \
                Attempting to run without explicit -c.", alembic_ini_path)
            alembic_command = ["alembic", "upgrade", "head"]
            cwd_for_alembic = project_root_dir
        else:
            logging.info("Using Alembic configuration: %s", alembic_ini_path)
            alembic_command = ["alembic", "-c", str(alembic_ini_path), "upgrade", "head"]
            cwd_for_alembic = project_root_dir

        process = subprocess.run(
            alembic_command,
            capture_output=True,
            text=True,
            check=False,
            cwd=str(cwd_for_alembic)
        )

        if process.returncode != 0:
            logging.error("Alembic migration error. Exit code: %s", process.returncode)
            logging.error("Stdout: %s", process.stdout)
            logging.error("Stderr: %s", process.stderr)
            raise RuntimeError(f"Alembic migration error: {process.stderr}")
        else:
            logging.info("Alembic migration successfully completed. Stdout: %s", process.stdout)

    except FileNotFoundError:
        logging.error("'alembic' command not found. Make sure Alembic is installed.")
        raise
    except Exception as e:
        logging.error("Error during DB initialization: %s", e, exc_info=True)
        raise
