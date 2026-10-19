from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QComboBox,
    QLineEdit,
    QTextEdit,
    QDialogButtonBox
)

from data.database import (
    get_people,
    get_organizations
)


class EdgeDialog(QDialog):

    def __init__(
        self,
        current_table,
        current_id,
        edge=None,
        parent=None
    ):
        super().__init__(parent)

        self.current_table = current_table
        self.current_id = current_id
        self.edge = edge

        self.setWindowTitle(
            "Edit Edge" if edge else "Add Edge"
        )

        layout = QFormLayout(self)

        # --------------------------------------------------
        # EDGE TYPE
        # --------------------------------------------------

        self.type_combo = QComboBox()

        if current_table == "people":
            self.type_combo.addItems([
                "Person → Person",
                "Person → Organization"
            ])

        elif current_table == "organizations":
            self.type_combo.addItems([
                "Organization → Person",
                "Organization → Organization"
            ])

        layout.addRow(
            "Connection type:",
            self.type_combo
        )

        # --------------------------------------------------
        # OTHER ENTITY
        # --------------------------------------------------

        self.entity_combo = QComboBox()

        layout.addRow(
            "Connected to:",
            self.entity_combo
        )

        self.type_combo.currentIndexChanged.connect(
            self.load_entities
        )

        # --------------------------------------------------
        # RELATIONSHIP
        # --------------------------------------------------

        self.relationship = QLineEdit()

        layout.addRow(
            "Relationship:",
            self.relationship
        )

        # --------------------------------------------------
        # ROLE
        # --------------------------------------------------

        self.role = QLineEdit()

        layout.addRow(
            "Role:",
            self.role
        )

        # --------------------------------------------------
        # DATES
        # --------------------------------------------------

        self.start_date = QLineEdit()
        self.end_date = QLineEdit()

        layout.addRow(
            "Start date:",
            self.start_date
        )

        layout.addRow(
            "End date:",
            self.end_date
        )

        # --------------------------------------------------
        # NOTES
        # --------------------------------------------------

        self.notes = QTextEdit()

        layout.addRow(
            "Notes:",
            self.notes
        )

        # --------------------------------------------------
        # BUTTONS
        # --------------------------------------------------

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok |
            QDialogButtonBox.Cancel
        )

        buttons.accepted.connect(
            self.accept
        )

        buttons.rejected.connect(
            self.reject
        )

        layout.addRow(buttons)

        self.load_entities()

        if edge:
            self.load_edge()

            self.type_combo.setEnabled(False)
            self.entity_combo.setEnabled(False)

    def load_entities(self):

        self.entity_combo.clear()

        edge_type = self.type_combo.currentText()

        if edge_type == "Person → Person":
            entities = get_people()

            for entity_id, name, surname, yob, yod in entities:

                if entity_id == self.current_id:
                    continue

                self.entity_combo.addItem(
                    f"{name} {surname}",
                    entity_id
                )

        elif edge_type == "Person → Organization":
            entities = get_organizations()

            for entity_id, name, acronym, org_type, start_date, end_date in entities:

                self.entity_combo.addItem(
                    f"{name} ({acronym})",
                    entity_id
                )

        elif edge_type == "Organization → Person":
            entities = get_people()

            for entity_id, name, surname, yob, yod in entities:

                self.entity_combo.addItem(
                    f"{name} {surname}",
                    entity_id
                )

        elif edge_type == "Organization → Organization":
            entities = get_organizations()

            for entity_id, name, acronym, org_type, start_date, end_date in entities:

                if entity_id == self.current_id:
                    continue

                self.entity_combo.addItem(
                    f"{name} ({acronym})",
                    entity_id
                )

    def load_edge(self):

        self.relationship.setText(
            self.edge["relationship"] or ""
        )

        self.role.setText(
            self.edge["role"] or ""
        )

        self.start_date.setText(
            self.edge["start_date"] or ""
        )

        self.end_date.setText(
            self.edge["end_date"] or ""
        )

        self.notes.setPlainText(
            self.edge["notes"] or ""
        )

