import sqlite3

con = sqlite3.connect("data/practice.db")
# The returned Connection object con represents the connection to the on-disk database

# In order to execute SQL statements and fetch results from SQL queries, we will need to use a database cursor. 
# Call con.cursor() to create the Cursor:
cur = con.cursor()

# now you can call the .execute method on cur and execute SQL commands strings
cur.execute("CREATE TABLE IF NOT EXISTS people(id INTEGER PRIMARY KEY AUTOINCREMENT, name, surname, yob INTEGER)")
cur.execute("CREATE TABLE IF NOT EXISTS organizations(id INTEGER PRIMARY KEY AUTOINCREMENT, name_full, acronym, type)")
cur.execute("""
    CREATE TABLE IF NOT EXISTS person_organization (
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

        UNIQUE (person_id, organization_id, relationship)
    )
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS person_person (
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

        UNIQUE (person1_id, person2_id, relationship)
    )
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS organization_organization (
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

        UNIQUE (organization1_id, organization2_id, relationship)
    )
""")

cur.execute("ALTER TABLE organizations ADD COLUMN start_date TEXT")
cur.execute("ALTER TABLE organizations ADD COLUMN end_date TEXT")
con.commit() # this saves the changes
