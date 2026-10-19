import networkx as nx

from datetime import datetime
import re

from data.database import get_people, get_organizations, get_edges




def parse_date(value, default):

    if not value:
        return default

    match = re.fullmatch(
        r"(\d{2})/(\d{4})",
        str(value).strip()
    )

    if not match:
        return default

    month = int(match.group(1))
    year = int(match.group(2))

    if month < 1 or month > 12:
        return default

    return year * 12 + month


def current_month():

    today = datetime.now()

    return (
        today.year * 12
        + today.month
    )


def person_is_alive(yob, yod, selected_month):

    if yob is not None:

        birth_month = (
            int(yob) * 12
            + 1
        )

        if selected_month < birth_month:
            return False

    if yod is not None:

        death_month = (
            int(yod) * 12
            + 12
        )

        if selected_month > death_month:
            return False

    return True


def is_active_between(
    start_date,
    end_date,
    selected_month
):

    start = parse_date(
        start_date,
        float("-inf")
    )

    end = parse_date(
        end_date,
        float("inf")
    )

    return (
        start <= selected_month
        and selected_month <= end
    )

def build_graph(selected_month=None):

    if selected_month is None:
        selected_month = current_month()

    graph = nx.Graph()

    # --------------------------------------------------
    # PEOPLE
    # --------------------------------------------------

    people = get_people()

    for person_id, name, surname, yob, yod in people:

        if not person_is_alive(
            yob,
            yod,
            selected_month
        ):
            continue

        node_id = (
            "people",
            person_id
        )

        graph.add_node(
            node_id,
            table="people",
            record_id=person_id,
            type="Person",
            name=f"{name} {surname}",
            yob=yob,
            yod=yod
        )

    # --------------------------------------------------
    # ORGANIZATIONS
    # --------------------------------------------------

    organizations = get_organizations()

    for (
        org_id,
        name_full,
        acronym,
        org_type,
        start_date,
        end_date
    ) in organizations:

        if not is_active_between(
            start_date,
            end_date,
            selected_month
        ):
            continue

        node_id = (
            "organizations",
            org_id
        )

        graph.add_node(
            node_id,
            table="organizations",
            record_id=org_id,
            type="Organization",
            name=f"{name_full} ({acronym})",
            start_date=start_date,
            end_date=end_date
        )

    # --------------------------------------------------
    # EDGES
    # --------------------------------------------------

    for node_id in list(graph.nodes):

        table = graph.nodes[node_id]["table"]

        record_id = graph.nodes[node_id]["record_id"]

        edges = get_edges(
            table,
            record_id
        )

        for edge in edges:

            if not is_active_between(
                edge["start_date"],
                edge["end_date"],
                selected_month
            ):
                continue

            other_node_id = (
                "people"
                if edge["type"] == "Person"
                else "organizations",
                edge["record_id"]
            )

            # Other entity may have been excluded because
            # the person was not alive at this date.
            if other_node_id not in graph:
                continue

            if graph.has_edge(
                node_id,
                other_node_id
            ):
                continue

            graph.add_edge(
                node_id,
                other_node_id,
                relationship=edge["relationship"],
                edge_id=edge["id"],
                table=edge["table"]
            )

    return graph