import networkx as nx

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene
)

from network.node import NetworkNode
from network.edge import NetworkEdge


class NetworkView(QGraphicsView):

    def __init__(self, parent=None, on_node_selected=None):

        super().__init__(parent)

        self.on_node_selected = on_node_selected

        self.network_graph = None
        self.full_graph = None

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.setInteractive(True)

        self.setRenderHint(
            QPainter.Antialiasing
        )

        self.setDragMode(
            QGraphicsView.ScrollHandDrag
        )

        self.setTransformationAnchor(
            QGraphicsView.AnchorUnderMouse
        )
        self.scene.setSelectionArea

        self.scene.setItemIndexMethod(
            QGraphicsScene.NoIndex
        )

        self.nodes = {}
        self.edges = []

    def wheelEvent(self, event):

        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            factor = zoom_in_factor
        else:
            factor = zoom_out_factor

        self.scale(
            factor,
            factor
        )

    def load_graph(self, graph, update_full_graph=True):

        if update_full_graph:
            self.full_graph = graph

        self.network_graph = graph

        self.scene.clear()

        self.nodes.clear()
        self.edges.clear()

        if graph.number_of_nodes() == 0:
            return

        positions = nx.spring_layout(
            graph,
            seed=42
        )

        scale = 300

        # Create nodes

        for node_id, data in graph.nodes(data=True):

            node = NetworkNode(
                node_id,
                data,
                self.on_node_selected
            )

            x, y = positions[node_id]

            node.set_position(
                x * scale,
                y * scale
            )

            self.nodes[node_id] = node

            self.scene.addItem(
                node.item
            )


        # Resolve visual overlaps before creating edges
        self.resolve_overlaps()


        for source_id, target_id, data in graph.edges(data=True):

            source = self.nodes[source_id]
            target = self.nodes[target_id]

            edge = NetworkEdge(
                source,
                target,
                data
            )

            self.edges.append(edge)

            self.scene.addItem(
                edge.item
            )

            edge.item.setZValue(-1)

        self.fitInView(
            self.scene.itemsBoundingRect(),
            Qt.KeepAspectRatio
        )

    def select_node(self, node_id):

        node = self.nodes.get(node_id)

        if node is None:
            return

        self.scene.clearSelection()

        node.item.setSelected(True)

        self.centerOn(node.item)

    def focus_node(self, node_id, radius=1):

        if self.full_graph is None:
            return

        if node_id not in self.full_graph:
            return

        focused_graph = nx.ego_graph(
            self.full_graph,
            node_id,
            radius=radius
        )

        self.load_graph(
            focused_graph,
            update_full_graph=False
        )

        self.select_node(
            node_id
        )

        print("FOCUS NODE:", node_id)
        print("RADIUS:", radius)

        focused_graph = nx.ego_graph(
            self.full_graph,
            node_id,
            radius=radius
        )

        print("FOCUSED NODES:")

        for node in focused_graph.nodes:
            print(node, focused_graph.nodes[node]["name"])

    def show_all(self):

        if self.full_graph is None:
            return

        self.load_graph(
            self.full_graph,
            update_full_graph=False
        )

    def resolve_overlaps(
        self,
        iterations=100,
        padding=20
    ):

        nodes = list(
            self.nodes.values()
        )

        for _ in range(iterations):

            moved = False

            for i in range(len(nodes)):

                node_a = nodes[i]

                rect_a = (
                    node_a.item
                    .mapToScene(
                        node_a.item.childrenBoundingRect()
                    )
                    .boundingRect()
                    .adjusted(
                        -padding,
                        -padding,
                        padding,
                        padding
                    )
                )

                for j in range(i + 1, len(nodes)):

                    node_b = nodes[j]

                    rect_b = (
                        node_b.item
                        .mapToScene(
                            node_b.item.childrenBoundingRect()
                        )
                        .boundingRect()
                        .adjusted(
                            -padding,
                            -padding,
                            padding,
                            padding
                        )
                    )

                    if not rect_a.intersects(rect_b):
                        continue

                    moved = True

                    overlap_x = min(
                        rect_a.right(),
                        rect_b.right()
                    ) - max(
                        rect_a.left(),
                        rect_b.left()
                    )

                    overlap_y = min(
                        rect_a.bottom(),
                        rect_b.bottom()
                    ) - max(
                        rect_a.top(),
                        rect_b.top()
                    )

                    if overlap_x < overlap_y:

                        if (
                            rect_a.center().x()
                            <
                            rect_b.center().x()
                        ):

                            dx = -overlap_x / 2
                        else:

                            dx = overlap_x / 2

                        node_a.item.moveBy(
                            dx,
                            0
                        )

                        node_b.item.moveBy(
                            -dx,
                            0
                        )

                    else:

                        if (
                            rect_a.center().y()
                            <
                            rect_b.center().y()
                        ):

                            dy = -overlap_y / 2
                        else:

                            dy = overlap_y / 2

                        node_a.item.moveBy(
                            0,
                            dy
                        )

                        node_b.item.moveBy(
                            0,
                            -dy
                        )

                    # Recalculate A because it may have moved
                    rect_a = (
                        node_a.item
                        .mapToScene(
                            node_a.item.childrenBoundingRect()
                        )
                        .boundingRect()
                        .adjusted(
                            -padding,
                            -padding,
                            padding,
                            padding
                        )
                    )

            if not moved:
                break