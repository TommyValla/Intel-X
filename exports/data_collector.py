
from data.project import database_connection


def collect_export_data():
    """Collect all entities and relationships from the active project."""

    nodes = []
    edges = []

    with database_connection() as con:
        con.row_factory = None
        cur = con.cursor()

        # -------------------------------------------------
        # People
        # -------------------------------------------------

        cur.execute("""
            SELECT id, name, surname, yob, yod
            FROM people
            ORDER BY id
        """)

        for record_id, name, surname, yob, yod in cur.fetchall():
            full_name = " ".join(
                part for part in (name, surname) if part
            )

            nodes.append({
                "id": f"person:{record_id}",
                "record_id": record_id,
                "entity_type": "person",
                "label": full_name or f"Person {record_id}",
                "name": name,
                "surname": surname,
                "yob": yob,
                "yod": yod,
            })

        # -------------------------------------------------
        # Organizations
        # -------------------------------------------------

        cur.execute("""
            SELECT id, name_full, acronym, type, start_date, end_date
            FROM organizations
            ORDER BY id
        """)

        for (
            record_id,
            name_full,
            acronym,
            org_type,
            start_date,
            end_date,
        ) in cur.fetchall():

            nodes.append({
                "id": f"organization:{record_id}",
                "record_id": record_id,
                "entity_type": "organization",
                "label": name_full or acronym or f"Organization {record_id}",
                "name_full": name_full,
                "acronym": acronym,
                "type": org_type,
                "start_date": start_date,
                "end_date": end_date,
            })

        # -------------------------------------------------
        # Person ↔ Person
        # -------------------------------------------------

        cur.execute("""
            SELECT
                id, person1_id, person2_id, relationship,
                role, start_date, end_date, notes
            FROM person_person
            ORDER BY id
        """)

        for (
            edge_id,
            person1_id,
            person2_id,
            relationship,
            role,
            start_date,
            end_date,
            notes,
        ) in cur.fetchall():

            edges.append({
                "id": f"person_person:{edge_id}",
                "record_id": edge_id,
                "table": "person_person",
                "source": f"person:{person1_id}",
                "target": f"person:{person2_id}",
                "relationship": relationship,
                "role": role,
                "start_date": start_date,
                "end_date": end_date,
                "notes": notes,
            })

        # -------------------------------------------------
        # Person ↔ Organization
        # -------------------------------------------------

        cur.execute("""
            SELECT
                id, person_id, organization_id, relationship,
                role, start_date, end_date, notes
            FROM person_organization
            ORDER BY id
        """)

        for (
            edge_id,
            person_id,
            organization_id,
            relationship,
            role,
            start_date,
            end_date,
            notes,
        ) in cur.fetchall():

            edges.append({
                "id": f"person_organization:{edge_id}",
                "record_id": edge_id,
                "table": "person_organization",
                "source": f"person:{person_id}",
                "target": f"organization:{organization_id}",
                "relationship": relationship,
                "role": role,
                "start_date": start_date,
                "end_date": end_date,
                "notes": notes,
            })

        # -------------------------------------------------
        # Organization ↔ Organization
        # -------------------------------------------------

        cur.execute("""
            SELECT
                id, organization1_id, organization2_id, relationship,
                role, start_date, end_date, notes
            FROM organization_organization
            ORDER BY id
        """)

        for (
            edge_id,
            organization1_id,
            organization2_id,
            relationship,
            role,
            start_date,
            end_date,
            notes,
        ) in cur.fetchall():

            edges.append({
                "id": f"organization_organization:{edge_id}",
                "record_id": edge_id,
                "table": "organization_organization",
                "source": f"organization:{organization1_id}",
                "target": f"organization:{organization2_id}",
                "relationship": relationship,
                "role": role,
                "start_date": start_date,
                "end_date": end_date,
                "notes": notes,
            })

    return {
        "nodes": nodes,
        "edges": edges,
    }
