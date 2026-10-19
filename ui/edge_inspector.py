from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QListWidget,
    QListWidgetItem,
    QTableWidget,
    QTableWidgetItem,
    QDialog,
    QMessageBox
)

from data.database import (
    get_edges,
    create_edge,
    update_edge,
    delete_edge
)

from ui.edge_dialog import EdgeDialog

class EdgeInspector(QFrame):

    def __init__(self, parent=None, on_network_changed=None):
        super().__init__(parent)

        self.on_network_changed = on_network_changed

        self.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #cccccc;
            }
        """)

        layout = QVBoxLayout(self)

        # Top bar
        top_layout = QHBoxLayout()

        title = QLabel("Edges")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
            }
        """)

        self.close_button = QPushButton("×")
        self.close_button.setFixedWidth(30)

        top_layout.addWidget(title)
        top_layout.addStretch()
        top_layout.addWidget(self.close_button)

        layout.addLayout(top_layout)

        # Main split
        splitter = QSplitter(Qt.Horizontal)

        # Left side
        self.edge_list = QListWidget()
        splitter.addWidget(self.edge_list)

        # Right side
        self.edge_table = QTableWidget()
        self.edge_table.setColumnCount(2)
        self.edge_table.setHorizontalHeaderLabels(
            ["Field", "Value"]
        )
        self.edge_table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        splitter.addWidget(self.edge_table)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)

        self.edge_list.currentRowChanged.connect(
            self.show_edge
        )

        self.close_button.clicked.connect(
            self.close
        )

        self.edges = []

        # Buttons
        button_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Edge")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)

        layout.addLayout(button_layout)

        self.add_button.clicked.connect(
            self.add_edge
        )

        self.edit_button.clicked.connect(
            self.edit_edge
        )

        self.delete_button.clicked.connect(
            self.delete_edge
        )

    def load_edges(
        self,
        edges,
        current_table,
        current_id
    ):

        self.edges = edges
        self.current_table = current_table
        self.current_id = current_id

        self.edge_list.clear()
        self.edge_table.clearContents()
        self.edge_table.setRowCount(0)

        for edge in edges:

            relationship = edge["relationship"]

            if relationship:
                text = (
                    f'{edge["name"]} '
                    f'— {relationship}'
                )
            else:
                text = edge["name"]

            item = QListWidgetItem(text)

            self.edge_list.addItem(item)

        if edges:
            self.edge_list.setCurrentRow(0)

    # show edge button function
    def show_edge(self, row):
    
        if row < 0 or row >= len(self.edges):
                return
    
        edge = self.edges[row]
    
        fields = [
            ("Type", edge["type"]),
            ("Relationship", edge["relationship"]),
            ("Role", edge["role"]),
            ("Start date", edge["start_date"]),
            ("End date", edge["end_date"]),
            ("Notes", edge["notes"]),
        ]
    
        self.edge_table.setRowCount(len(fields))
    
        for i, (field, value) in enumerate(fields):
    
            field_item = QTableWidgetItem(field)
    
            value_item = QTableWidgetItem(
                "" if value is None else str(value)
            )
    
            field_item.setFlags(
                field_item.flags() & ~Qt.ItemIsEditable
            )
    
            value_item.setFlags(
                value_item.flags() & ~Qt.ItemIsEditable
            )
    
            self.edge_table.setItem(i, 0, field_item)
            self.edge_table.setItem(i, 1, value_item)
    
        self.edge_table.resizeColumnsToContents()

    # add edge

    def add_edge(self):

        dialog = EdgeDialog(
            self.current_table,
            self.current_id,
            parent=self
        )

        if dialog.exec() != QDialog.Accepted:
            return

        other_id = dialog.entity_combo.currentData()

        relationship = dialog.relationship.text()
        role = dialog.role.text()
        start_date = dialog.start_date.text()
        end_date = dialog.end_date.text()
        notes = dialog.notes.toPlainText()

        edge_type = dialog.type_combo.currentText()

        if edge_type == "Person → Person":

            table = "person_person"

            first_id = self.current_id
            second_id = other_id

        elif edge_type == "Person → Organization":

            table = "person_organization"

            first_id = self.current_id
            second_id = other_id

        elif edge_type == "Organization → Person":

            table = "person_organization"

            first_id = other_id
            second_id = self.current_id

        elif edge_type == "Organization → Organization":

            table = "organization_organization"

            first_id = self.current_id
            second_id = other_id

        create_edge(
            table,
            first_id,
            second_id,
            relationship,
            role,
            start_date,
            end_date,
            notes
        )

        self.refresh_edges()

        if self.on_network_changed:
            self.on_network_changed()

    # refresh
    def refresh_edges(self):

        edges = get_edges(
            self.current_table,
            self.current_id
        )

        self.load_edges(
            edges,
            self.current_table,
            self.current_id
        )

    # delete
    def delete_edge(self):

        row = self.edge_list.currentRow()

        if row < 0:
            return

        edge = self.edges[row]

        answer = QMessageBox.question(
            self,
            "Delete Edge",
            f"Delete the relationship with {edge['name']}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if answer != QMessageBox.Yes:
            return

        delete_edge(
            edge["table"],
            edge["id"]
        )

        self.refresh_edges()

        if self.on_network_changed:
            self.on_network_changed()

    # edeit
    def edit_edge(self):

        row = self.edge_list.currentRow()

        if row < 0:
            return

        edge = self.edges[row]

        dialog = EdgeDialog(
            self.current_table,
            self.current_id,
            edge=edge,
            parent=self
        )

        if dialog.exec() != QDialog.Accepted:
            return

        values = {
            "relationship":
                dialog.relationship.text(),

            "role":
                dialog.role.text(),

            "start_date":
                dialog.start_date.text(),

            "end_date":
                dialog.end_date.text(),

            "notes":
                dialog.notes.toPlainText()
        }

        update_edge(
            edge["table"],
            edge["id"],
            values
        )

        self.refresh_edges()

        if self.on_network_changed:
            self.on_network_changed()
 