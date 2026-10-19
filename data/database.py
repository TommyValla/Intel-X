import sqlite3


def get_people():

    con = sqlite3.connect("data/practice.db")
    cur = con.cursor()

    cur.execute("""
        SELECT id, name, surname, yob, yod
        FROM people
    """)

    people = cur.fetchall()

    con.close()

    return people


def get_organizations():

    con = sqlite3.connect("data/practice.db")
    cur = con.cursor()

    cur.execute("""
        SELECT id, name_full, acronym, type, start_date, end_date
        FROM organizations
    """)

    organizations = cur.fetchall()

    con.close()

    return organizations


def get_record(table, record_id):

    con = sqlite3.connect("data/practice.db")
    cur = con.cursor()

    cur.execute(
        f"""
        SELECT *
        FROM {table}
        WHERE id = ?
        """,
        (record_id,)
    )

    record = cur.fetchone()

    columns = [
        description[0]
        for description in cur.description
    ]

    con.close()

    return columns, record


def update_record(table, record_id, values):

    con = sqlite3.connect("data/practice.db")
    cur = con.cursor()

    fields = ", ".join(
        f"{field} = ?"
        for field in values
    )

    sql = f"""
        UPDATE {table}
        SET {fields}
        WHERE id = ?
    """

    cur.execute(
        sql,
        list(values.values()) + [record_id]
    )

    con.commit()
    con.close()


def create_person(name, surname, yob, yod=None):
    con = sqlite3.connect("data/practice.db")
    cur = con.cursor()

    cur.execute("""
        INSERT INTO people (
            name,
            surname,
            yob,
            yod
        )
        VALUES (?, ?, ?, ?)
    """, (
        name,
        surname,
        yob,
        yod
    ))

    con.commit()
    con.close()


def create_organization(name_full, acronym, org_type, start_date=None, end_date=None):
    con = sqlite3.connect("data/practice.db")
    cur = con.cursor()

    cur.execute("""
        INSERT INTO organizations (
            name_full,
            acronym,
            type,
            start_date,
            end_date
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        name_full,
        acronym,
        org_type,
        start_date,
        end_date
    ))

    con.commit()
    con.close()



def get_edges(table, record_id):
    con = sqlite3.connect("data/practice.db")
    cur = con.cursor()

    edges = []

    if table == "people":

        # Person ↔ Person
        cur.execute("""
            SELECT
                pp.id,
                'person_person',
                pp.relationship,
                pp.role,
                pp.start_date,
                pp.end_date,
                pp.notes,
                p.id,
                p.name,
                p.surname
            FROM person_person pp
            JOIN people p
                ON p.id = CASE
                    WHEN pp.person1_id = ? THEN pp.person2_id
                    ELSE pp.person1_id
                END
            WHERE pp.person1_id = ?
               OR pp.person2_id = ?
        """, (record_id, record_id, record_id))

        for row in cur.fetchall():
            (
                edge_id,
                edge_table,
                relationship,
                role,
                start_date,
                end_date,
                notes,
                other_id,
                name,
                surname
            ) = row

            edges.append({
                "id": edge_id,
                "table": edge_table,
                "type": "Person",
                "name": f"{name} {surname}",
                "record_id": other_id,
                "relationship": relationship,
                "role": role,
                "start_date": start_date,
                "end_date": end_date,
                "notes": notes
            })

        # Person ↔ Organization
        cur.execute("""
            SELECT
                po.id,
                'person_organization',
                po.relationship,
                po.role,
                po.start_date,
                po.end_date,
                po.notes,
                o.id,
                o.name_full,
                o.acronym
            FROM person_organization po
            JOIN organizations o
                ON o.id = po.organization_id
            WHERE po.person_id = ?
        """, (record_id,))

        for row in cur.fetchall():
            (
                edge_id,
                edge_table,
                relationship,
                role,
                start_date,
                end_date,
                notes,
                other_id,
                name,
                acronym
            ) = row

            edges.append({
                "id": edge_id,
                "table": edge_table,
                "type": "Organization",
                "name": f"{name} ({acronym})",
                "record_id": other_id,
                "relationship": relationship,
                "role": role,
                "start_date": start_date,
                "end_date": end_date,
                "notes": notes
            })

    elif table == "organizations":

        # Organization ↔ Organization
        cur.execute("""
            SELECT
                oo.id,
                'organization_organization',
                oo.relationship,
                oo.role,
                oo.start_date,
                oo.end_date,
                oo.notes,
                o.id,
                o.name_full,
                o.acronym
            FROM organization_organization oo
            JOIN organizations o
                ON o.id = CASE
                    WHEN oo.organization1_id = ? THEN oo.organization2_id
                    ELSE oo.organization1_id
                END
            WHERE oo.organization1_id = ?
               OR oo.organization2_id = ?
        """, (record_id, record_id, record_id))

        for row in cur.fetchall():
            (
                edge_id,
                edge_table,
                relationship,
                role,
                start_date,
                end_date,
                notes,
                other_id,
                name,
                acronym
            ) = row

            edges.append({
                "id": edge_id,
                "table": edge_table,
                "type": "Organization",
                "name": f"{name} ({acronym})",
                "record_id": other_id,
                "relationship": relationship,
                "role": role,
                "start_date": start_date,
                "end_date": end_date,
                "notes": notes
            })

        # Organization ↔ Person
        cur.execute("""
            SELECT
                po.id,
                'person_organization',
                po.relationship,
                po.role,
                po.start_date,
                po.end_date,
                po.notes,
                p.id,
                p.name,
                p.surname
            FROM person_organization po
            JOIN people p
                ON p.id = po.person_id
            WHERE po.organization_id = ?
        """, (record_id,))

        for row in cur.fetchall():
            (
                edge_id,
                edge_table,
                relationship,
                role,
                start_date,
                end_date,
                notes,
                other_id,
                name,
                surname
            ) = row

            edges.append({
                "id": edge_id,
                "table": edge_table,
                "type": "Person",
                "name": f"{name} {surname}",
                "record_id": other_id,
                "relationship": relationship,
                "role": role,
                "start_date": start_date,
                "end_date": end_date,
                "notes": notes
            })

    con.close()

    return edges

def create_edge(
    table,
    first_id,
    second_id,
    relationship="",
    role="",
    start_date="",
    end_date="",
    notes=""
):
    con = sqlite3.connect("data/practice.db")
    cur = con.cursor()

    if table == "person_person":

        cur.execute("""
            INSERT INTO person_person (
                person1_id,
                person2_id,
                relationship,
                role,
                start_date,
                end_date,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            first_id,
            second_id,
            relationship,
            role,
            start_date,
            end_date,
            notes
        ))

    elif table == "person_organization":

        cur.execute("""
            INSERT INTO person_organization (
                person_id,
                organization_id,
                relationship,
                role,
                start_date,
                end_date,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            first_id,
            second_id,
            relationship,
            role,
            start_date,
            end_date,
            notes
        ))

    elif table == "organization_organization":

        cur.execute("""
            INSERT INTO organization_organization (
                organization1_id,
                organization2_id,
                relationship,
                role,
                start_date,
                end_date,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            first_id,
            second_id,
            relationship,
            role,
            start_date,
            end_date,
            notes
        ))

    con.commit()
    con.close()

def update_edge(table, edge_id, values):

    con = sqlite3.connect("data/practice.db")
    cur = con.cursor()

    fields = ", ".join(
        f"{field} = ?"
        for field in values
    )

    sql = f"""
        UPDATE {table}
        SET {fields}
        WHERE id = ?
    """

    cur.execute(
        sql,
        list(values.values()) + [edge_id]
    )

    con.commit()
    con.close()

def delete_edge(table, edge_id):

    con = sqlite3.connect("data/practice.db")
    cur = con.cursor()

    cur.execute(
        f"""
        DELETE FROM {table}
        WHERE id = ?
        """,
        (edge_id,)
    )

    con.commit()
    con.close()