from PySide6.QtCore import Qt
from PySide6.QtGui import QTextDocument
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QPlainTextEdit,
    QTextBrowser,
    QSplitter,
    QMessageBox
)

from dossier.manager import (
    load_dossier,
    save_dossier
)


class DossierEditor(QFrame):

    def __init__(
        self,
        table,
        record_id,
        name,
        parent=None
    ):
        super().__init__(parent)

        self.table = table
        self.record_id = record_id
        self.name = name

        self.setWindowTitle(
            f"Dossier — {name}"
        )

        self.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #cccccc;
            }

            QLabel#title {
                font-size: 20px;
                font-weight: bold;
                border: none;
            }

            QPushButton {
                padding: 6px 12px;
            }

            QPlainTextEdit {
                border: 1px solid #cccccc;
                padding: 8px;
                font-family: Consolas;
                font-size: 14px;
            }

            QTextBrowser {
                border: 1px solid #cccccc;
                padding: 12px;
                font-size: 14px;
            }
        """)

        # -------------------------------------------------
        # Main layout
        # -------------------------------------------------

        layout = QVBoxLayout(self)

        # -------------------------------------------------
        # Header
        # -------------------------------------------------

        header = QHBoxLayout()

        self.title = QLabel(
            f"Dossier — {name}"
        )
        self.title.setObjectName("title")

        header.addWidget(self.title)
        header.addStretch()

        self.close_button = QPushButton("×")
        self.close_button.setFixedWidth(35)

        header.addWidget(
            self.close_button
        )

        layout.addLayout(header)

        # -------------------------------------------------
        # Editor + Preview
        # -------------------------------------------------

        splitter = QSplitter(
            Qt.Horizontal
        )

        self.editor = QPlainTextEdit()

        self.preview = QTextBrowser()

        splitter.addWidget(
            self.editor
        )

        splitter.addWidget(
            self.preview
        )

        splitter.setStretchFactor(
            0,
            1
        )

        splitter.setStretchFactor(
            1,
            1
        )

        layout.addWidget(
            splitter
        )

        # -------------------------------------------------
        # Bottom buttons
        # -------------------------------------------------

        button_layout = QHBoxLayout()

        self.save_button = QPushButton(
            "Save"
        )

        self.preview_button = QPushButton(
            "Edit / Preview"
        )

        button_layout.addWidget(
            self.save_button
        )

        button_layout.addWidget(
            self.preview_button
        )

        button_layout.addStretch()

        self.close_bottom_button = QPushButton(
            "Close"
        )

        button_layout.addWidget(
            self.close_bottom_button
        )

        layout.addLayout(
            button_layout
        )

        # -------------------------------------------------
        # Connections
        # -------------------------------------------------

        self.close_button.clicked.connect(
            self.close
        )

        self.close_bottom_button.clicked.connect(
            self.close
        )

        self.save_button.clicked.connect(
            self.save
        )

        self.preview_button.clicked.connect(
            self.update_preview
        )

        self.editor.textChanged.connect(
            self.on_text_changed
        )

        # -------------------------------------------------
        # Load dossier
        # -------------------------------------------------

        self.load()

    # -----------------------------------------------------
    # Load
    # -----------------------------------------------------

    def load(self):
        try:
            content = load_dossier(
                self.table,
                self.record_id,
                self.name
            )

            self.editor.setPlainText(content)
            self.editor.document().setModified(False)

            self.save_button.setText("Save")
            self.update_preview()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Dossier error",
                f"Could not load dossier:\n\n{error}"
            )


    # -----------------------------------------------------
    # Text changes
    # -----------------------------------------------------

    def on_text_changed(self):
        self.editor.document().setModified(True)
        self.save_button.setText("Save")
        self.update_preview()

    # -----------------------------------------------------
    # Preview
    # -----------------------------------------------------

    def update_preview(self):

        markdown = self.editor.toPlainText()

        document = QTextDocument()

        document.setMarkdown(
            markdown
        )

        self.preview.setDocument(
            document
        )

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    def save(self):
        content = self.editor.toPlainText()

        try:
            save_dossier(
                self.table,
                self.record_id,
                content
            )

            self.editor.document().setModified(False)
            self.save_button.setText("Saved")
            return True

        except Exception as error:
            QMessageBox.critical(
                self,
                "Dossier error",
                f"Could not save dossier:\n\n{error}"
            )
            return False

    def maybe_save_changes(self):
        if not self.editor.document().isModified():
            return True

        answer = QMessageBox.question(
            self,
            "Unsaved Changes",
            "This dossier has unsaved changes. Do you want to save them?",
            QMessageBox.Save
            | QMessageBox.Discard
            | QMessageBox.Cancel,
            QMessageBox.Save
        )

        if answer == QMessageBox.Save:
            return self.save()

        if answer == QMessageBox.Discard:
            self.editor.document().setModified(False)
            return True

        return False


    def closeEvent(self, event):
        if self.maybe_save_changes():
            event.accept()
        else:
            event.ignore()