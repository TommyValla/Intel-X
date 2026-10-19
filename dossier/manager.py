from pathlib import Path


# ---------------------------------------------------------
# Base directories
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DOSSIERS_DIR = BASE_DIR / "dossiers"
ASSETS_DIR = BASE_DIR / "assets" / "dossiers"


# ---------------------------------------------------------
# Dossier paths
# ---------------------------------------------------------

def get_dossier_path(table, record_id):
    """
    Return the Markdown file path for an entity.
    """

    if table == "people":
        folder = DOSSIERS_DIR / "people"

    elif table == "organizations":
        folder = DOSSIERS_DIR / "organizations"

    else:
        raise ValueError(
            f"Unknown entity table: {table}"
        )

    return folder / f"{record_id}.md"


def get_asset_directory(table, record_id):
    """
    Return the asset directory for an entity.
    """

    if table == "people":
        folder = ASSETS_DIR / "people"

    elif table == "organizations":
        folder = ASSETS_DIR / "organizations"

    else:
        raise ValueError(
            f"Unknown entity table: {table}"
        )

    return folder / str(record_id)


# ---------------------------------------------------------
# Templates
# ---------------------------------------------------------

def get_template(table, name):
    """
    Return the default Markdown template for an entity.
    """

    if table == "people":

        return f"""# {name}

## Summary

## Biography

## Career

## Political activity

## Organizations

## Personal relationships

## Timeline

## Sources

## Notes
"""

    elif table == "organizations":

        return f"""# {name}

## Summary

## History

## Ownership and governance

## Leadership

## Political relationships

## Corporate relationships

## Timeline

## Sources

## Notes
"""

    else:
        raise ValueError(
            f"Unknown entity table: {table}"
        )


# ---------------------------------------------------------
# Create dossier
# ---------------------------------------------------------

def create_dossier(table, record_id, name):
    """
    Create a dossier if it does not already exist.

    Returns the dossier path.
    """

    dossier_path = get_dossier_path(
        table,
        record_id
    )

    asset_directory = get_asset_directory(
        table,
        record_id
    )

    # Make sure directories exist
    dossier_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    asset_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    # Create Markdown file only if it doesn't exist
    if not dossier_path.exists():

        content = get_template(
            table,
            name
        )

        dossier_path.write_text(
            content,
            encoding="utf-8"
        )

    return dossier_path


# ---------------------------------------------------------
# Load dossier
# ---------------------------------------------------------

def load_dossier(table, record_id, name):
    """
    Make sure the dossier exists and return its contents.
    """

    dossier_path = create_dossier(
        table,
        record_id,
        name
    )

    return dossier_path.read_text(
        encoding="utf-8"
    )


# ---------------------------------------------------------
# Save dossier
# ---------------------------------------------------------

def save_dossier(table, record_id, content):
    """
    Save Markdown content to the entity's dossier.
    """

    dossier_path = get_dossier_path(
        table,
        record_id
    )

    dossier_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    dossier_path.write_text(
        content,
        encoding="utf-8"
    )

    return dossier_path
