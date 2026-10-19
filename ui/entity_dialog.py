from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QComboBox,
    QLineEdit,
    QLabel,
    QDialogButtonBox,
    QMessageBox
)

import re

class NewEntityDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("New Entity")

        layout = QFormLayout(self)

        # -------------------------
        # Entity type
        # -------------------------

        self.type_combo = QComboBox()

        self.type_combo.addItems([
            "Person",
            "Organization"
        ])

        layout.addRow(
            "Entity type:",
            self.type_combo
        )

        # -------------------------
        # Person fields
        # -------------------------

        self.name_label = QLabel("Name:")
        self.name = QLineEdit()

        layout.addRow(
            self.name_label,
            self.name
        )

        self.surname_label = QLabel("Surname:")
        self.surname = QLineEdit()

        layout.addRow(
            self.surname_label,
            self.surname
        )

        self.yob_label = QLabel("Year of birth:")
        self.yob = QLineEdit()

        layout.addRow(
            self.yob_label,
            self.yob
        )

        self.yod_label = QLabel("Year of death:")
        self.yod = QLineEdit()

        layout.addRow(
            self.yod_label,
            self.yod
        )        

        # -------------------------
        # Organization fields
        # -------------------------

        self.name_full_label = QLabel("Full name:")
        self.name_full = QLineEdit()

        layout.addRow(
            self.name_full_label,
            self.name_full
        )

        self.acronym_label = QLabel("Acronym:")
        self.acronym = QLineEdit()

        layout.addRow(
            self.acronym_label,
            self.acronym
        )

        self.org_type_label = QLabel("Type:")
        self.org_type = QComboBox()

        self.org_type.addItems([
            "",
            "government body",
            "intel agency",
            "law enforcement agency",
            "criminal organization",
            "company",
            "NGO",
            "political party",
            "media",
            "research institute",
            "international organization",
            "other"
        ])

        layout.addRow(
            self.org_type_label,
            self.org_type
        )

        self.start_date_label = QLabel("Start date:")
        self.start_date = QLineEdit()

        layout.addRow(
            self.start_date_label,
            self.start_date
        )

        self.end_date_label = QLabel("End date:")
        self.end_date = QLineEdit()

        layout.addRow(
            self.end_date_label,
            self.end_date
        )

        # -------------------------
        # Buttons
        # -------------------------

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok |
            QDialogButtonBox.Cancel
        )

        buttons.accepted.connect(
            self.validate
        )

        buttons.rejected.connect(
            self.reject
        )

        layout.addRow(buttons)

        # -------------------------
        # Entity type changed
        # -------------------------

        self.type_combo.currentIndexChanged.connect(
            self.update_fields
        )

        self.update_fields()

    def update_fields(self):

        is_person = (
            self.type_combo.currentText()
            == "Person"
        )

        # Person fields
        self.name_label.setVisible(is_person)
        self.name.setVisible(is_person)

        self.surname_label.setVisible(is_person)
        self.surname.setVisible(is_person)

        self.yob_label.setVisible(is_person)
        self.yob.setVisible(is_person)

        self.yod_label.setVisible(is_person)
        self.yod.setVisible(is_person)

        # Organization fields
        self.name_full_label.setVisible(not is_person)
        self.name_full.setVisible(not is_person)

        self.acronym_label.setVisible(not is_person)
        self.acronym.setVisible(not is_person)

        self.org_type_label.setVisible(not is_person)
        self.org_type.setVisible(not is_person)

        self.start_date_label.setVisible(not is_person)
        self.start_date.setVisible(not is_person)

        self.end_date_label.setVisible(not is_person)
        self.end_date.setVisible(not is_person)

        self.adjustSize()

    def validate(self):

        if self.type_combo.currentText() == "Person":

            if not self.name.text().strip():
                QMessageBox.warning(
                    self,
                    "Invalid entity",
                    "Name is required."
                )
                return

            if not self.surname.text().strip():
                QMessageBox.warning(
                    self,
                    "Invalid entity",
                    "Surname is required."
                )
                return

            yob = self.yob.text().strip()

            if yob:

                try:
                    yob = int(yob)

                except ValueError:
                    QMessageBox.warning(
                        self,
                        "Invalid entity",
                        "Year of birth must be a number."
                    )
                    return

                if yob < 1 or yob > 2100:
                    QMessageBox.warning(
                        self,
                        "Invalid entity",
                        "Year of birth must be between 1 and 2100."
                    )
                    return

            yod = self.yod.text().strip()

            if yod:

                try:
                    yod = int(yod)

                except ValueError:
                    QMessageBox.warning(
                        self,
                        "Invalid entity",
                        "Year of death must be a number."
                    )
                    return

                if yod < 1 or yod > 2100:
                    QMessageBox.warning(
                        self,
                        "Invalid entity",
                        "Year of death must be between 1 and 2100."
                    )
                    return

            if yod and yob and yod < yob:
                QMessageBox.warning(
                    self,
                    "Invalid entity",
                    "Year of death cannot be earlier than year of birth."
                )
                return

        else:

            if not self.name_full.text().strip():
                QMessageBox.warning(
                    self,
                    "Invalid entity",
                    "Organization name is required."
                )
                return

            start_date = self.start_date.text().strip()
            end_date = self.end_date.text().strip()

            if start_date:

                if not re.fullmatch(
                    r"(0[1-9]|1[0-2])/\d{4}",
                    start_date
                ):
                    QMessageBox.warning(
                        self,
                        "Invalid entity",
                        "Start date must use MM/YYYY format."
                    )
                    return

            if end_date:

                if not re.fullmatch(
                    r"(0[1-9]|1[0-2])/\d{4}",
                    end_date
                ):
                    QMessageBox.warning(
                        self,
                        "Invalid entity",
                        "End date must use MM/YYYY format."
                    )
                    return

            if start_date and end_date:

                start_month, start_year = map(
                    int,
                    start_date.split("/")
                )

                end_month, end_year = map(
                    int,
                    end_date.split("/")
                )

                start_value = (
                    start_year * 12
                    + start_month
                )

                end_value = (
                    end_year * 12
                    + end_month
                )

                if end_value < start_value:
                    QMessageBox.warning(
                        self,
                        "Invalid entity",
                        "End date cannot be earlier than start date."
                    )
                    return

        self.accept()