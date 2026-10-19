import sys

from PySide6.QtGui import QAction

from datetime import datetime

from data.project import open_project

from data.database import (
    get_people,
    get_organizations,
    get_record,
    update_record,
    create_person,
    create_organization,
    get_edges
)

from ui.entity_dialog import NewEntityDialog
from ui.edge_dialog import EdgeDialog
from ui.edge_inspector import EdgeInspector
from ui.dossier_editor import DossierEditor
from network.view import NetworkView
from network.graph import build_graph

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTreeWidget,
    QTreeWidgetItem,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
    QInputDialog,
    QTextEdit,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QLabel,
    QDialog,
    QComboBox,
    QSlider
)


class MainWindow(QMainWindow):
    
    def __init__(self, project_metadata=None):
        super().__init__()

        self.project_metadata = project_metadata or {}
        self.update_window_title()
        self.create_menu_bar()


        # Currently selected database record
        self.current_id = None
        self.current_table = None
        self.dossier_editor = None

        # --------------------------------------------------
        # MAIN LAYOUT
        # --------------------------------------------------

        layout1 = QHBoxLayout()
        layout2 = QVBoxLayout()

        # --------------------------------------------------
        # SEARCH
        # --------------------------------------------------

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search...")
        layout2.addWidget(self.search)

        # --------------------------------------------------
        # TREE
        # --------------------------------------------------

        tree_header = QHBoxLayout()

        tree_label = QLabel("Tree View")

        self.new_entity_button = QPushButton("New Entity")

        tree_header.addWidget(tree_label)
        tree_header.addStretch()
        tree_header.addWidget(self.new_entity_button)

        layout2.addLayout(tree_header)

        self.new_entity_button.clicked.connect(
            self.new_entity
        )

        self.tree = QTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderLabels(["Tree view"])

        layout2.addWidget(self.tree)

        self.search.textChanged.connect(
            self.filter_tree
        )

        self.tree.itemClicked.connect(
            self.select_element
        )

        # --------------------------------------------------
        # ATTRIBUTES
        # --------------------------------------------------

        self.edit_button = QPushButton("Edit")
        self.cancel_button = QPushButton("Cancel")

        self.cancel_button.setVisible(False)

        layout2.addWidget(self.edit_button)
        layout2.addWidget(self.cancel_button)

        self.edit_button.clicked.connect(
            self.edit_element
        )

        self.cancel_button.clicked.connect(
            self.cancel_edit
        )

        self.original_values = {}

        self.attributes_table = QTableWidget()
        self.attributes_table.setColumnCount(2)
        self.attributes_table.setHorizontalHeaderLabels(
            ["Field", "Value"]
        )

        # Values are read-only initially
        self.attributes_table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        layout2.addWidget(
            self.attributes_table
        )


        # show edges
        self.edges_button = QPushButton("Show Edges")
        layout2.addWidget(self.edges_button)

        self.edges_button.clicked.connect(
            self.show_edges
        )


        # dossier button
        self.dossier_button = QPushButton("Show Dossier")
        self.dossier_button.setVisible(False)
        layout2.addWidget(self.dossier_button)
        self.dossier_button.clicked.connect(self.show_dossier)

        # --------------------------------------------------
        # NETWORK
        # --------------------------------------------------

        layout1.addLayout(layout2)

        self.network_view = NetworkView(
            on_node_selected=self.network_node_selected
        )

        network_layout = QVBoxLayout()

        network_header = QHBoxLayout()

        network_label = QLabel(
            "Network View"
        )

        focus_button = QPushButton(
            "Focus"
        )

        show_all_button = QPushButton(
            "Show All"
        )

        network_header.addWidget(
            network_label
        )

        network_header.addStretch()

        network_header.addWidget(
            QLabel("Radius:")
        )

        self.hop_combo = QComboBox()

        self.hop_combo.addItems([
            "1 hop",
            "2 hops",
            "3 hops"
        ])

        network_header.addWidget(
            self.hop_combo
        )

        network_header.addWidget(
            focus_button
        )

        network_header.addWidget(
            show_all_button
        )

        network_layout.addLayout(
            network_header
        )

        network_layout.addWidget(
            self.network_view
        )

        # --------------------------------------------------
        # TIME FILTER
        # --------------------------------------------------

        time_layout = QHBoxLayout()

        time_label = QLabel(
            "Date:"
        )

        self.time_slider = QSlider(
            Qt.Horizontal
        )

        current_date = datetime.now()

        current_month = (
            current_date.year * 12
            + current_date.month
        )

        minimum_month = (
            1900 * 12
            + 1
        )

        self.time_slider.setMinimum(
            minimum_month
        )

        self.time_slider.setMaximum(
            current_month
        )

        self.time_slider.setValue(
            current_month
        )

        self.time_value = QLabel(
            "09/2026"
        )

        time_layout.addWidget(
            time_label
        )

        time_layout.addWidget(
            self.time_slider
        )

        time_layout.addWidget(
            self.time_value
        )

        network_layout.addLayout(
            time_layout
        )

        layout1.addLayout(
            network_layout
        )

        focus_button.clicked.connect(
            self.focus_network
        )

        show_all_button.clicked.connect(
            self.network_view.show_all
        )

        self.network_graph = build_graph(
            self.time_slider.value()
        )

        self.network_view.load_graph(
            self.network_graph
        )

        self.time_slider.valueChanged.connect(
            self.update_time_label
        )

        self.time_slider.valueChanged.connect(
            self.update_network_time
        )

        self.update_time_label(
            self.time_slider.value()
        )

        # --------------------------------------------------
        # CENTRAL WIDGET
        # --------------------------------------------------

        widget = QWidget()
        widget.setLayout(layout1)
        self.setCentralWidget(widget)

        self.edge_inspector = EdgeInspector(
            widget,
            on_network_changed=self.refresh_network
        )
        self.edge_inspector.hide()

        # --------------------------------------------------
        # LOAD DATABASE
        # --------------------------------------------------

        self.load_tree()


    # ======================================================
    # PROJECT AND MENU BAR
    # ======================================================

    def update_window_title(self):
        project_name = self.project_metadata.get(
            "name", "Untitled Project"
        )
        self.setWindowTitle(f"Intel-X — {project_name}")

    def create_menu_bar(self):
        file_menu = self.menuBar().addMenu("File")

        self.new_project_action = QAction("New Project...", self)
        self.new_project_action.triggered.connect(self.new_project)
        file_menu.addAction(self.new_project_action)

        self.open_project_action = QAction(
            "Open Project...", self
        )
        self.open_project_action.triggered.connect(
            self.switch_project
        )
        file_menu.addAction(self.open_project_action)

        self.project_info_action = QAction(
            "Project Information", self
        )
        self.project_info_action.triggered.connect(
            self.show_project_info
        )
        file_menu.addAction(self.project_info_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def show_project_info(self):
        project_name = self.project_metadata.get(
            "name", "Untitled Project"
        )
        project_version = self.project_metadata.get(
            "version", "Unknown"
        )

        from data.project import get_project_root, get_database_path

        QMessageBox.information(
            self,
            "Project Information",
            f"Name: {project_name}\n"
            f"Version: {project_version}\n"
            f"Folder: {get_project_root()}\n"
            f"Database: {get_database_path()}",
        )

    def switch_project(self):
        project_folder = QFileDialog.getExistingDirectory(
            self,
            "Open Intel-X Project",
            "",
        )

        if not project_folder:
            return

        # Validate before changing the active project.
        try:
            from data.project import validate_project

            validate_project(project_folder)

        except (ValueError, OSError) as error:
            QMessageBox.critical(
                self,
                "Could Not Open Project",
                str(error),
            )
            return

        # Warn if a dossier editor is currently open.
        if (
            self.dossier_editor is not None
            and self.dossier_editor.isVisible()
        ):
            answer = QMessageBox.question(
                self,
                "Switch Project",
                "Close the open dossier editor and switch "
                "projects? Save any unsaved dossier changes first.",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if answer != QMessageBox.StandardButton.Yes:
                return

        # Activate the new project.
        try:
            metadata = open_project(project_folder)
        except (ValueError, OSError) as error:
            QMessageBox.critical(
                self,
                "Could Not Open Project",
                str(error),
            )
            return

        self.project_metadata = metadata

        # Close overlays from the previous project.
        if self.dossier_editor is not None:
            self.dossier_editor.close()
            self.dossier_editor = None

        self.edge_inspector.hide()

        # Clear selection and attribute display.
        self.current_id = None
        self.current_table = None
        self.original_values = {}

        self.attributes_table.clearContents()
        self.attributes_table.setRowCount(0)

        self.dossier_button.setVisible(False)

        # Reset the network to show the new project's data.
        self.network_view.show_all()

        self.load_tree()
        self.refresh_network()
        self.update_window_title()

    def new_project(self):
        # Choose the parent directory.
        parent_folder = QFileDialog.getExistingDirectory(
            self,
            "Choose Location for New Project",
            "",
        )

        if not parent_folder:
            return

        # Ask for the project name.
        project_name, accepted = QInputDialog.getText(
            self,
            "New Project",
            "Project name:",
        )

        if not accepted:
            return

        project_name = project_name.strip()

        if not project_name:
            QMessageBox.warning(
                self,
                "Invalid Project Name",
                "Please enter a project name.",
            )
            return

        # Warn about an open dossier editor before switching.
        if (
            self.dossier_editor is not None
            and self.dossier_editor.isVisible()
        ):
            if not self.dossier_editor.maybe_save_changes():
                return

        # Create and activate the project.
        try:
            from data.project import create_project

            metadata = create_project(
                parent_folder,
                project_name,
            )

        except (ValueError, OSError) as error:
            QMessageBox.critical(
                self,
                "Could Not Create Project",
                str(error),
            )
            return

        # Update the window's project information.
        self.project_metadata = metadata

        # Close the old dossier editor.
        if self.dossier_editor is not None:
            self.dossier_editor.close()
            self.dossier_editor = None

        self.edge_inspector.hide()

        # Reset the current selection and attributes.
        self.current_id = None
        self.current_table = None
        self.original_values = {}

        self.attributes_table.clearContents()
        self.attributes_table.setRowCount(0)
        self.dossier_button.setVisible(False)

        # Refresh the interface for the new project.
        self.network_view.show_all()
        self.load_tree()
        self.refresh_network()
        self.update_window_title()

        QMessageBox.information(
            self,
            "Project Created",
            f"Project '{metadata['name']}' was created successfully.",
        )

    def show_edges(self):

        if self.current_id is None:
            return

        edges = get_edges(
            self.current_table,
            self.current_id
        )

        self.edge_inspector.load_edges(
            edges,
            self.current_table,
            self.current_id
        )

        rect = self.centralWidget().rect()

        margin = 30

        self.edge_inspector.setGeometry(
            margin,
            margin,
            rect.width() - 2 * margin,
            rect.height() - 2 * margin
        )

        self.edge_inspector.raise_()
        self.edge_inspector.show()

    # ======================================================
    # LOAD TREE
    # ======================================================

    def load_tree(self):

        self.tree.clear()

        # -------------------------
        # People
        # -------------------------

        people_item = QTreeWidgetItem(
            self.tree,
            ["People"]
        )

        people = get_people()

        for person_id, name, surname, yob, yod in people:

            full_name = f"{name} {surname}"

            person_item = QTreeWidgetItem(
                people_item,
                [full_name]
            )

            # Store database ID
            person_item.setData(
                0,
                Qt.UserRole,
                person_id
            )

            # Store database table
            person_item.setData(
                0,
                Qt.UserRole + 1,
                "people"
            )

        people_item.setExpanded(True)

        # -------------------------
        # Organizations
        # -------------------------

        orgs_item = QTreeWidgetItem(
            self.tree,
            ["Organizations"]
        )

        organizations = get_organizations()

        for org_id, name_full, acronym, org_type, start_date, end_date in organizations:

            full_name = f"{name_full} ({acronym})"

            org_item = QTreeWidgetItem(
                orgs_item,
                [full_name]
            )

            # Store database ID
            org_item.setData(
                0,
                Qt.UserRole,
                org_id
            )

            # Store database table
            org_item.setData(
                0,
                Qt.UserRole + 1,
                "organizations"
            )

        orgs_item.setExpanded(True)

    # new entity

    def new_entity(self):

        dialog = NewEntityDialog(
            parent=self
        )

        if dialog.exec() != QDialog.Accepted:
            return

        entity_type = dialog.type_combo.currentText()

        if entity_type == "Person":

            name = dialog.name.text().strip()
            surname = dialog.surname.text().strip()

            yob_text = dialog.yob.text().strip()
            yod_text = dialog.yod.text().strip()

            if yob_text:
                yob = int(yob_text)
            else:
                yob = None

            if yod_text:
                yod = int(yod_text)
            else:
                yod = None

            create_person(
                name,
                surname,
                yob,
                yod
            )

            self.refresh_network()

        elif entity_type == "Organization":

            name_full = dialog.name_full.text().strip()
            acronym = dialog.acronym.text().strip()
            org_type = dialog.org_type.currentText()

            start_date = dialog.start_date.text().strip()
            end_date = dialog.end_date.text().strip()

            if not start_date:
                start_date = None

            if not end_date:
                end_date = None

            create_organization(
                name_full,
                acronym,
                org_type,
                start_date,
                end_date
            )

            self.refresh_network()

        self.load_tree()

    # ======================================================
    # SEARCH
    # ======================================================

    def filter_tree(self, text):

        text = text.lower().strip()

        root = self.tree.invisibleRootItem()

        for i in range(root.childCount()):

            category = root.child(i)

            visible_children = 0

            for j in range(category.childCount()):

                item = category.child(j)

                item_text = item.text(0).lower()

                matches = text in item_text

                item.setHidden(not matches)

                if matches:
                    visible_children += 1

            # Hide category if none of its children match
            category.setHidden(
                visible_children == 0
            )


    ### Dossier
    def show_dossier(self):

        if self.current_id is None:
            return

        if self.current_table is None:
            return

        # Get the current entity's display name
        columns, record = get_record(
            self.current_table,
            self.current_id
        )

        record_data = dict(
            zip(columns, record)
        )

        if self.current_table == "people":

            name = (
                f'{record_data["name"]} '
                f'{record_data["surname"]}'
            )

        elif self.current_table == "organizations":

            name_full = record_data["name_full"]
            acronym = record_data["acronym"]

            if acronym:
                name = f"{name_full} ({acronym})"
            else:
                name = name_full

        else:
            return

        # Create editor
        self.dossier_editor = DossierEditor(
            self.current_table,
            self.current_id,
            name,
            parent=self.centralWidget()
        )

        # Make it almost full-screen
        central = self.centralWidget()

        margin = 30

        self.dossier_editor.setGeometry(
            margin,
            margin,
            central.width() - 2 * margin,
            central.height() - 2 * margin
        )

        self.dossier_editor.raise_()
        self.dossier_editor.show()
    
    # ======================================================
    # SELECT ELEMENT
    # ======================================================

    def select_element(self, item, column):

        record_id = item.data(
            0,
            Qt.UserRole
        )

        table = item.data(
            0,
            Qt.UserRole + 1
        )

        # Category item was clicked
        if table is None:
            return

        self.select_entity(
            table,
            record_id
        )

        self.network_view.select_node(
            (table, record_id)
        )

    def select_entity(self, table, record_id):

        self.current_id = record_id
        self.current_table = table
        self.dossier_button.setVisible(True)

        columns, record = get_record(
            table,
            record_id
        )

        self.show_attributes(
            columns,
            record
        )
      

    def select_tree_item(self, table, record_id):

        root = self.tree.invisibleRootItem()

        for i in range(root.childCount()):

            category = root.child(i)

            for j in range(category.childCount()):

                item = category.child(j)

                item_id = item.data(
                    0,
                    Qt.UserRole
                )

                item_table = item.data(
                    0,
                    Qt.UserRole + 1
                )

                if (
                    item_id == record_id
                    and item_table == table
                ):

                    self.tree.setCurrentItem(item)
                    return

    # ======================================================
    # SHOW ATTRIBUTES
    # ======================================================

    def show_attributes(self, columns, record):

        self.attributes_table.clearContents()

        fields = [
            (column, value)
            for column, value in zip(columns, record)
            if column != "id"
        ]

        self.attributes_table.setRowCount(
            len(fields)
        )

        self.original_values = {}

        for row, (field, value) in enumerate(fields):

            value = "" if value is None else str(value)

            field_item = QTableWidgetItem(field)
            value_item = QTableWidgetItem(value)

            field_item.setFlags(
                field_item.flags()
                & ~Qt.ItemIsEditable
            )

            self.attributes_table.setItem(
                row,
                0,
                field_item
            )

            self.attributes_table.setItem(
                row,
                1,
                value_item
            )

            self.original_values[field] = value

        self.attributes_table.resizeColumnsToContents()

    # ======================================================
    # EDIT
    # ======================================================

    def edit_element(self):

        if self.current_id is None:
            return

        self.attributes_table.setEditTriggers(
            QTableWidget.DoubleClicked |
            QTableWidget.EditKeyPressed
        )

        self.edit_button.setText("Save")
        self.cancel_button.setVisible(True)

        self.edit_button.clicked.disconnect(
            self.edit_element
        )

        self.edit_button.clicked.connect(
            self.save_element
        )


    # ======================================================
    # CANCEL
    # ======================================================

    def cancel_edit(self):

        for row in range(
            self.attributes_table.rowCount()
        ):

            field = self.attributes_table.item(
                row,
                0
            ).text()

            self.attributes_table.item(
                row,
                1
            ).setText(
                self.original_values[field]
            )

        self.finish_editing()

    def finish_editing(self):

        self.attributes_table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.edit_button.setText("Edit")
        self.cancel_button.setVisible(False)

        self.edit_button.clicked.disconnect(
            self.save_element
        )

        self.edit_button.clicked.connect(
            self.edit_element
        )

    # ======================================================
    # SAVE
    # ======================================================

    def save_element(self):

        values = {}

        for row in range(
            self.attributes_table.rowCount()
        ):

            field = self.attributes_table.item(
                row,
                0
            ).text()

            value = self.attributes_table.item(
                row,
                1
            ).text()

            values[field] = value

        # Find what actually changed
        changes = {
            field: value
            for field, value in values.items()
            if value != self.original_values[field]
        }

        # Nothing changed
        if not changes:
            self.finish_editing()
            return

        # Validate before saving
        if not self.validate_values(values):
            return

        update_record(
            self.current_table,
            self.current_id,
            changes
        )

        self.finish_editing()

        # Refresh current record
        columns, record = get_record(
            self.current_table,
            self.current_id
        )

        self.show_attributes(
            columns,
            record
        )

        # Refresh tree display
        self.load_tree()

    # validate
    def validate_values(self, values):

        # People
        if self.current_table == "people":

            yob = values.get("yob", "")

            if yob == "":
                return True

            try:
                yob = int(yob)
            except ValueError:
                self.show_error(
                    "Year of birth must be a number."
                )
                return False

            if yob < 1 or yob > 2100:
                self.show_error(
                    "Year of birth must be between 1 and 2100."
                )
                return False

        return True

    def show_error(self, message):

        QMessageBox.warning(
            self,
            "Invalid value",
            message
        )

    def network_node_selected(self, node_id):

        table, record_id = node_id

        self.select_entity(
            table,
            record_id
        )

        self.select_tree_item(
            table,
            record_id
        )

    def focus_network(self):

        if self.current_table is None:
            return

        node_id = (
            self.current_table,
            self.current_id
        )

        radius = self.hop_combo.currentIndex() + 1

        self.network_view.focus_node(
            node_id,
            radius
        )

    def refresh_network(self):

        self.network_graph = build_graph(
            self.time_slider.value()
        )

        self.network_view.load_graph(
            self.network_graph
        )

    def update_time_label(self, value):

        year = value // 12
        month = value % 12

        if month == 0:
            month = 12
            year -= 1

        self.time_value.setText(
            f"{month:02d}/{year}"
        )

    def update_network_time(self, value):

        self.network_graph = build_graph(
            value
        )

        self.network_view.load_graph(
            self.network_graph
        )

# ==========================================================
# APPLICATION
# ==========================================================


app = QApplication(sys.argv)

while True:
    project_folder = QFileDialog.getExistingDirectory(
        None,
        "Open Intel-X Project",
        "",
    )

    # User cancelled the dialog.
    if not project_folder:
        sys.exit(0)

    try:
        project_metadata = open_project(project_folder)
        break

    except (ValueError, OSError) as error:
        QMessageBox.critical(
            None,
            "Could Not Open Project",
            str(error),
        )

window = MainWindow(project_metadata)
window.show()

app.exec()
