from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsTextItem
)

from PySide6.QtCore import Qt

from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtSvg import QSvgRenderer

from PySide6.QtGui import (
    QBrush,
    QColor,
    QPen
)

ICON_PATHS = {
    "person": "assets/icons/person.svg",
    "organization": "assets/icons/organization.svg",
}
ICON_SIZE = 50

class MovableNodeItem(QGraphicsRectItem):

    def itemChange(self, change, value):

        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if hasattr(self, "node"):
                self.node.update_edges()

        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            if hasattr(self, "node"):
                self.node.selection_changed(value)

        return super().itemChange(change, value)

class NetworkNode:

    def __init__(self, node_id, data, on_selected=None):

        self.node_id = node_id
        self.data = data
        self.on_selected = on_selected

        self.edges = []

        entity_type = data["type"].lower()
        icon_path = ICON_PATHS[entity_type]

        # Create an invisible parent item with a 50x50 hitbox
        self.item = MovableNodeItem(-25, -25, 50, 50)

        self.item.setPen(QPen(Qt.NoPen))
        self.item.setBrush(QBrush(Qt.NoBrush))

        # Create the SVG icon as a child
        self.icon = QGraphicsSvgItem(icon_path, self.item)

        # Scale the icon independently
        bounds = self.icon.boundingRect()
        scale = ICON_SIZE / max(bounds.width(), bounds.height())
        self.icon.setScale(scale)

        # Center the icon inside the parent
        scaled_width = bounds.width() * scale
        scaled_height = bounds.height() * scale

        self.icon.setPos(
            -scaled_width / 2,
            -scaled_height / 2
        )

        # Configure node interaction
        self.item.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )

        self.item.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        )

        self.item.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        self.item.node = self
        
        # Create the label as a child of the node
        self.label = self.create_label(data["name"], self.item)

        # Position the label below the node
        self.label.setPos(
            -self.label.rect().width() / 2,
            30
        )

    def set_position(self, x, y):

        self.item.setPos(
            x,
            y
        )

    def add_edge(self, edge):

        self.edges.append(edge)

    def update_edges(self):

        for edge in self.edges:
            edge.update_position()

    def update_style(self, selected=False):

        if selected:
            self.label.setBrush(QBrush(QColor("#4DD99F")))
        else:
            self.label.setBrush(QBrush(QColor("#72AFE9")))

    def selection_changed(self, selected):

        self.update_style(selected)

        if selected:

            self.set_z_value(100)

            if self.on_selected:
                self.on_selected(self.node_id)

        else:

            self.set_z_value(0)


    def create_label(self, name, parent):

        padding_x = 8
        padding_y = 4

        label = QGraphicsRectItem(parent)

        self.label_text = QGraphicsTextItem(name, label)
        self.label_text.document().setDocumentMargin(0)
        self.label_text.setDefaultTextColor(QColor("#000000"))

        text_rect = self.label_text.boundingRect()

        label.setRect(
            0,
            0,
            text_rect.width() + 2 * padding_x,
            text_rect.height() + 2 * padding_y
        )

        self.label_text.setPos(padding_x, padding_y)

        label.setBrush(QBrush(QColor("#72AFE9")))
        label.setPen(QPen(QColor("#607D8B"), 1))

        return label

    def set_z_value(self, z):
        self.item.setZValue(z)