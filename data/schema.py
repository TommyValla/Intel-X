from contextlib import closing
import sqlite3
from pathlib import Path


def initialize_database(database_path):
    database_path = Path(database_path)
    database_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with closing(sqlite3.connect(database_path)) as con:
        con.execute("PRAGMA foreign_keys = ON")

        con.execute("""
            CREATE TABLE people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                surname TEXT,
                yob INTEGER,
                yod INTEGER
            )
        """)

        con.execute("""
            CREATE TABLE organizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_full TEXT,
                acronym TEXT,
                type TEXT,
                start_date TEXT,
                end_date TEXT
            )
        """)

        con.execute("""
            CREATE TABLE person_organization (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER NOT NULL,
                organization_id INTEGER NOT NULL,
                relationship TEXT,
                role TEXT,
                start_date TEXT,
                end_date TEXT,
                notes TEXT,
                FOREIGN KEY (person_id)
                    REFERENCES people(id),
                FOREIGN KEY (organization_id)
                    REFERENCES organizations(id),
                UNIQUE (
                    person_id,
                    organization_id,
                    relationship
                )
            )
        """)

        con.execute("""
            CREATE TABLE person_person (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person1_id INTEGER NOT NULL,
                person2_id INTEGER NOT NULL,
                relationship TEXT,
                role TEXT,
                start_date TEXT,
                end_date TEXT,
                notes TEXT,
                FOREIGN KEY (person1_id)
                    REFERENCES people(id),
                FOREIGN KEY (person2_id)
                    REFERENCES people(id),
                UNIQUE (
                    person1_id,
                    person2_id,
                    relationship
                )
            )
        """)

        con.execute("""
            CREATE TABLE organization_organization (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization1_id INTEGER NOT NULL,
                organization2_id INTEGER NOT NULL,
                relationship TEXT,
                role TEXT,
                start_date TEXT,
                end_date TEXT,
                notes TEXT,
                FOREIGN KEY (organization1_id)
                    REFERENCES organizations(id),
                FOREIGN KEY (organization2_id)
                    REFERENCES organizations(id),
                UNIQUE (
                    organization1_id,
                    organization2_id,
                    relationship
                )
            )
        """)

        con.commit()
