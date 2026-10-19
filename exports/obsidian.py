
import json
import re
from pathlib import Path

from exports.data_collector import collect_export_data
from data.project import (
    get_project_root,
    get_dossier_path,
)


def make_filename(node):
    """Create a readable, unique Markdown filename for an entity."""

    label = node["label"].strip().lower()
    slug = re.sub(r"[^\w-]+", "_", label, flags=re.UNICODE)
    slug = slug.strip("_") or "unnamed"

    return f'{node["entity_type"]}_{node["record_id"]}_{slug}.md'


def yaml_value(value):
    """Format a value as a YAML-compatible scalar."""

    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)

    if value is None:
        return "null"

    return str(value)


def export_obsidian(output_dir=None):
    """Export Intel-X entities and relationships as Obsidian notes."""

    data = collect_export_data()

    if output_dir is None:
        output_dir = (
            get_project_root()
            / "exports"
            / "obsidian"
        )

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    nodes = data["nodes"]
    edges = data["edges"]

    # Map each entity ID to its data and Markdown filename.
    node_lookup = {
        node["id"]: node
        for node in nodes
    }

    filenames = {
        node["id"]: make_filename(node)
        for node in nodes
    }

    # Store each relationship against both connected entities.
    relationships = {
        node["id"]: []
        for node in nodes
    }

    for edge in edges:
        source = edge["source"]
        target = edge["target"]

        if source not in node_lookup or target not in node_lookup:
            continue

        relationships[source].append((edge, target))

        if source != target:
            relationships[target].append((edge, source))

    # Create one Markdown note per entity.
    for node in nodes:
        lines = ["---"]

        # Include all available node attributes as properties.
        for key, value in node.items():
            if key == "id" or value is None:
                continue

            lines.append(f"{key}: {yaml_value(value)}")

        lines.extend(["---", "", "# " + node["label"], ""])

        connected = relationships[node["id"]]

        lines.extend([
            "## Relationships",
            "",
        ])

        if not connected:
            lines.append("No recorded relationships.")
        else:
            for edge, other_id in connected:
                other = node_lookup[other_id]
                link_name = Path(filenames[other_id]).stem

                lines.append(
                    f"- **{edge.get('relationship') or 'unspecified'}** "
                    f"→ [[{link_name}|{other['label']}]]"
                )

                if edge.get("role"):
                    lines.append(
                        f"  - **Role:** {edge['role']}"
                    )

                if edge.get("start_date"):
                    lines.append(
                        f"  - **Start date:** {edge['start_date']}"
                    )

                if edge.get("end_date"):
                    lines.append(
                        f"  - **End date:** {edge['end_date']}"
                    )

                if edge.get("notes"):
                    notes = " ".join(
                        str(edge["notes"]).split()
                    )
                    lines.append(f"  - **Notes:** {notes}")

        lines.append("")

        
        # Append the existing dossier, if one exists.
        table = (
            "people"
            if node["entity_type"] == "person"
            else "organizations"
        )

        dossier_path = get_dossier_path(
            table,
            node["record_id"],
        )

        if dossier_path.is_file():
            dossier_content = dossier_path.read_text(
                encoding="utf-8"
            ).strip()

            if dossier_content:
                lines.extend([
                    "",
                    "---",
                    "",
                    "## Dossier",
                    "",
                    dossier_content,
                    "",
                ])


        output_path = output_dir / filenames[node["id"]]
        output_path.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )

    # Create an index note linking to all exported entities.
    index_lines = [
        "# Intel-X Network",
        "",
        f"Entities: {len(nodes)}",
        f"Relationships: {len(edges)}",
        "",
        "## People",
        "",
    ]

    for node in sorted(
        (n for n in nodes if n["entity_type"] == "person"),
        key=lambda n: n["label"].casefold(),
    ):
        stem = Path(filenames[node["id"]]).stem
        index_lines.append(f"- [[{stem}|{node['label']}]]")

    index_lines.extend(["", "## Organizations", ""])

    for node in sorted(
        (n for n in nodes if n["entity_type"] == "organization"),
        key=lambda n: n["label"].casefold(),
    ):
        stem = Path(filenames[node["id"]]).stem
        index_lines.append(f"- [[{stem}|{node['label']}]]")

    (output_dir / "Intel-X Network.md").write_text(
        "\n".join(index_lines) + "\n",
        encoding="utf-8",
    )

    return output_dir
