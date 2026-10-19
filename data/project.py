from contextlib import contextmanager
from pathlib import Path
import sqlite3
import json
import shutil
from data.schema import initialize_database

# ---------------------------------------------------------
# Active project
# ---------------------------------------------------------

APP_ROOT = Path(__file__).resolve().parent.parent

_active_project_root = APP_ROOT
_active_database_path = APP_ROOT / "data" / "practice.db"


def set_project_root(root, database_relative_path="database.db"):
    """Set the root folder and database for the active project."""
    global _active_project_root, _active_database_path

    _active_project_root = Path(root).resolve()
    _active_database_path = (
        _active_project_root / database_relative_path
    ).resolve()


def get_project_root():
    return _active_project_root


def set_database_path(path):
    """Set only the database path."""
    global _active_database_path
    _active_database_path = Path(path).resolve()


def get_database_path():
    return _active_database_path


@contextmanager
def get_connection():
    database_path = get_database_path()

    if not database_path.is_file():
        raise FileNotFoundError(
            f"Database not found: {database_path}"
        )

    con = sqlite3.connect(database_path)

    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

@contextmanager
def database_connection():
    with get_connection() as con:
        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise

# ---------------------------------------------------------
# Project file paths
# ---------------------------------------------------------

def get_dossier_path(table, record_id):
    folders = {
        "people": "people",
        "organizations": "organizations",
    }

    if table not in folders:
        raise ValueError(f"Unknown entity table: {table}")

    return (
        _active_project_root
        / "dossiers"
        / folders[table]
        / f"{record_id}.md"
    )


def get_asset_directory(table, record_id):
    folders = {
        "people": "people",
        "organizations": "organizations",
    }

    if table not in folders:
        raise ValueError(f"Unknown entity table: {table}")

    return (
        _active_project_root
        / "assets"
        / "dossiers"
        / folders[table]
        / str(record_id)
    )


def validate_project(root):
    root = Path(root).expanduser().resolve()

    if not root.is_dir():
        raise ValueError(
            f"Project folder does not exist:\n{root}"
        )

    # Read project metadata.
    config_path = root / "project.json"

    if not config_path.is_file():
        raise ValueError(
            "This folder does not contain project.json."
        )

    try:
        with open(config_path, "r", encoding="utf-8") as file:
            metadata = json.load(file)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError(
            f"Could not read project.json:\n{error}"
        ) from error

    if not isinstance(metadata, dict):
        raise ValueError(
            "project.json must contain a JSON object."
        )

    database_relative_path = metadata.get("database")

    if (
        not isinstance(database_relative_path, str)
        or not database_relative_path.strip()
    ):
        raise ValueError(
            "project.json must specify a database path."
        )

    # Resolve the database path and prevent paths outside the project.
    database_path = (
        root / database_relative_path
    ).resolve()

    if not database_path.is_relative_to(root):
        raise ValueError(
            "The database must be located inside the project folder."
        )

    if not database_path.is_file():
        raise ValueError(
            f"Database file not found:\n{database_path}"
        )

    # Ensure the dossiers directory exists.
    if not (root / "dossiers").is_dir():
        raise ValueError(
            "The project is missing its dossiers directory."
        )

    # Define the minimum schema required by Intel-X.
    required_columns = {
        "people": {
            "id", "name", "surname", "yob", "yod"
        },
        "organizations": {
            "id", "name_full", "acronym", "type",
            "start_date", "end_date"
        },
        "person_person": {
            "id", "person1_id", "person2_id",
            "relationship", "role", "start_date",
            "end_date", "notes"
        },
        "person_organization": {
            "id", "person_id", "organization_id",
            "relationship", "role", "start_date",
            "end_date", "notes"
        },
        "organization_organization": {
            "id", "organization1_id", "organization2_id",
            "relationship", "role", "start_date",
            "end_date", "notes"
        },
    }

    con = None

    try:
        con = sqlite3.connect(database_path)

        existing_tables = {
            row[0]
            for row in con.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
            """).fetchall()
        }

        for table, expected_columns in required_columns.items():
            if table not in existing_tables:
                raise ValueError(
                    f"The project database is missing "
                    f"the '{table}' table."
                )

            actual_columns = {
                row[1]
                for row in con.execute(
                    f"PRAGMA table_info({table})"
                ).fetchall()
            }

            missing_columns = (
                expected_columns - actual_columns
            )

            if missing_columns:
                missing = ", ".join(sorted(missing_columns))

                raise ValueError(
                    f"The '{table}' table is missing "
                    f"these columns: {missing}"
                )

    except sqlite3.DatabaseError as error:
        raise ValueError(
            f"The project database is invalid or corrupted:\n{error}"
        ) from error

    finally:
        if con is not None:
            con.close()

    return root, database_relative_path, metadata

def create_project(parent_folder, name):
    parent = Path(parent_folder).expanduser().resolve()
    name = name.strip()

    if not parent.is_dir():
        raise ValueError(
            "The selected parent folder does not exist."
        )

    if not name:
        raise ValueError("Project name cannot be empty.")

    invalid_characters = '<>:"/\\|?*'

    if any(character in name for character in invalid_characters):
        raise ValueError(
            'Project name cannot contain these characters: '
            '< > : " / \\ | ? *'
        )

    if name.endswith((" ", ".")):
        raise ValueError(
            "Project name cannot end with a space or period."
        )

    project_root = parent / name

    if project_root.exists():
        raise FileExistsError(
            f"The folder already exists:\n{project_root}"
        )

    project_root.mkdir()

    try:
        # Create project directories.
        (project_root / "dossiers" / "people").mkdir(
            parents=True
        )
        (project_root / "dossiers" / "organizations").mkdir()

        (project_root / "assets" / "dossiers" / "people").mkdir(
            parents=True
        )
        (
            project_root
            / "assets"
            / "dossiers"
            / "organizations"
        ).mkdir()

        (project_root / "exports").mkdir()

        # Initialize the SQLite database.
        initialize_database(
            project_root / "database.db"
        )

        # Write project metadata.
        metadata = {
            "name": name,
            "version": 1,
            "database": "database.db",
        }

        with open(
            project_root / "project.json",
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(metadata, file, indent=4)

        # Activate the newly created project.
        return open_project(project_root)

    except Exception:
        # Remove the newly created folder if initialization fails.
        shutil.rmtree(project_root)
        raise

def open_project(root):
    root, database_relative_path, metadata = validate_project(root)

    set_project_root(
        root,
        database_relative_path=database_relative_path,
    )

    return metadata

