import sqlite3
from pathlib import Path

from data.project import (
    create_project,
    get_database_path,
    get_project_root,
)


test_parent = Path(__file__).resolve().parent / "data"
test_parent.mkdir(exist_ok=True)

test_name = "creation_test_project"
test_root = test_parent / test_name

if test_root.exists():
    raise FileExistsError(
        f"Remove the previous test folder first:\n{test_root}"
    )

metadata = create_project(test_parent, test_name)

project_root = get_project_root()
database_path = get_database_path()

print("Project:", metadata["name"])
print("Root:", project_root)
print("Database:", database_path)

con = sqlite3.connect(database_path)

try:
    tables = con.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """).fetchall()
finally:
    con.close()

print("\nDatabase tables:")
for table in tables:
    print(table[0])

expected_paths = [
    project_root / "project.json",
    project_root / "database.db",
    project_root / "dossiers" / "people",
    project_root / "dossiers" / "organizations",
    project_root / "assets" / "dossiers" / "people",
    project_root / "assets" / "dossiers" / "organizations",
    project_root / "exports",
]

assert all(path.exists() for path in expected_paths)
assert len(tables) == 5

print("\nProject creation test successful.")
print(f"Test project retained at: {project_root}")