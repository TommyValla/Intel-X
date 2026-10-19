
import sqlite3
from pathlib import Path

from data.schema import initialize_database


test_database = (
    Path(__file__).resolve().parent
    / "data"
    / "schema_test.db"
)

if test_database.exists():
    test_database.unlink()

initialize_database(test_database)

con = sqlite3.connect(test_database)

try:
    tables = con.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """).fetchall()

    for table in tables:
        print(table[0])

    people_columns = con.execute(
        "PRAGMA table_info(people)"
    ).fetchall()

    print("\nPeople columns:")
    for column in people_columns:
        print(column[1])

finally:
    con.close()

print(f"\nSchema test successful.")
print(f"Test database: {test_database}")