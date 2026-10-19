from PySide6.QtCore import QLineF
from PySide6.QtWidgets import QGraphicsLineItem


class NetworkEdge:

    def __init__(self, source, target, data):

        self.source = source
        self.target = target
        self.data = data

        self.item = QGraphicsLineItem()

        source.add_edge(self)
        target.add_edge(self)

        self.update_position()

    def update_position(self):

        source_pos = self.source.item.scenePos()
        target_pos = self.target.item.scenePos()

        line = QLineF(
            source_pos,
            target_pos
        )

        self.item.setLine(line)