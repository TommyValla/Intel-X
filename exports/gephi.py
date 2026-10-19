
from pathlib import Path
import xml.etree.ElementTree as ET

from exports.data_collector import collect_export_data
from data.project import get_project_root


GRAPHML_NS = "http://graphml.graphdrawing.org/xmlns"
ET.register_namespace("", GRAPHML_NS)


def qname(tag):
    return f"{{{GRAPHML_NS}}}{tag}"


def export_graphml(output_path=None):
    """Export the active Intel-X network to an undirected GraphML file."""

    data = collect_export_data()

    if output_path is None:
        output_path = (
            get_project_root()
            / "exports"
            / "intelx_network.graphml"
        )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    root = ET.Element(qname("graphml"))

    # -------------------------------------------------
    # Declare node and edge attributes
    # -------------------------------------------------

    node_attributes = [
        "record_id",
        "entity_type",
        "label",
        "name",
        "surname",
        "yob",
        "yod",
        "name_full",
        "acronym",
        "type",
        "start_date",
        "end_date",
    ]

    edge_attributes = [
        "record_id",
        "table",
        "relationship",
        "role",
        "start_date",
        "end_date",
        "notes",
    ]

    for attribute in node_attributes:
        ET.SubElement(
            root,
            qname("key"),
            {
                "id": f"node_{attribute}",
                "for": "node",
                "attr.name": attribute,
                "attr.type": "string",
            },
        )

    for attribute in edge_attributes:
        ET.SubElement(
            root,
            qname("key"),
            {
                "id": f"edge_{attribute}",
                "for": "edge",
                "attr.name": attribute,
                "attr.type": "string",
            },
        )

    # -------------------------------------------------
    # Graph
    # -------------------------------------------------

    graph = ET.SubElement(
        root,
        qname("graph"),
        {
            "id": "IntelX",
            "edgedefault": "undirected",
        },
    )

    # -------------------------------------------------
    # Nodes
    # -------------------------------------------------

    for node_data in data["nodes"]:
        node = ET.SubElement(
            graph,
            qname("node"),
            {"id": node_data["id"]},
        )

        for attribute in node_attributes:
            value = node_data.get(attribute)

            if value is None:
                continue

            data_element = ET.SubElement(
                node,
                qname("data"),
                {"key": f"node_{attribute}"},
            )
            data_element.text = str(value)

    # -------------------------------------------------
    # Edges
    # -------------------------------------------------

    for edge_data in data["edges"]:
        edge = ET.SubElement(
            graph,
            qname("edge"),
            {
                "id": edge_data["id"],
                "source": edge_data["source"],
                "target": edge_data["target"],
            },
        )

        for attribute in edge_attributes:
            value = edge_data.get(attribute)

            if value is None:
                continue

            data_element = ET.SubElement(
                edge,
                qname("data"),
                {"key": f"edge_{attribute}"},
            )
            data_element.text = str(value)

    # -------------------------------------------------
    # Write file
    # -------------------------------------------------

    tree = ET.ElementTree(root)
    ET.indent(tree, space="    ")

    tree.write(
        output_path,
        encoding="utf-8",
        xml_declaration=True,
    )

    return output_path
