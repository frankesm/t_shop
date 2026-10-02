from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDialog,
    QDateEdit,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from shared.exceptions import ValidacionError


class EditBuyDialog(QDialog):
    def __init__(self, controller, buy, parent=None):
        super().__init__(parent)

        self.controller = controller
        self.buy_id = buy["id"]

        self.setWindowTitle("Actualizar compra")
        self.setModal(True)
        self.setMinimumWidth(380)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        d = buy["date"]
        self.date_edit.setDate(QDate(d.year, d.month, d.day))

        self.code_input = QLineEdit(buy["code"] or "")
        self.other_cost = QLineEdit(str(buy["other_cost"]))
        self.transportation_cost = QLineEdit(str(buy["transportation_cost"]))

        self.date_error = QLabel()
        self.code_error = QLabel()
        self.other_cost_error = QLabel()
        self.transportation_error = QLabel()

        for label in self._error_labels().values():
            self._configure_error_label(label)

        form = QFormLayout()
        form.addRow(
            "Fecha",
            self._field_container(self.date_edit, self.date_error),
        )
        form.addRow(
            "Código",
            self._field_container(self.code_input, self.code_error),
        )
        form.addRow(
            "Otros costos",
            self._field_container(self.other_cost, self.other_cost_error),
        )
        form.addRow(
            "Costo de transporte",
            self._field_container(self.transportation_cost, self.transportation_error),
        )

        btn_cancel = QPushButton("Cancelar")
        btn_save = QPushButton("Actualizar")
        btn_save.setDefault(True)

        btn_cancel.clicked.connect(self.reject)
        btn_save.clicked.connect(self.accept)

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(btn_cancel)
        buttons.addWidget(btn_save)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(buttons)

    # -- helpers de UI
    def _error_labels(self):
        return {
            "date": self.date_error,
            "code": self.code_error,
            "other_cost": self.other_cost_error,
            "transportation_cost": self.transportation_error,
        }

    @staticmethod
    def _configure_error_label(label: QLabel):
        label.setStyleSheet("color: #dc3545; font-size: 11px;")
        label.setWordWrap(True)
        label.hide()

    @staticmethod
    def _field_container(field: QWidget, error_label: QLabel) -> QWidget:
        container = QWidget()

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # El error aparece SOBRE el campo.
        layout.addWidget(error_label)
        layout.addWidget(field)

        return container

    # -- datos
    def _get_data(self):
        return {
            "date": self.date_edit.date().toPython(),
            "code": self.code_input.text(),
            "other_cost": self.other_cost.text(),
            "transportation_cost": self.transportation_cost.text(),
        }

    # -- errores
    def _clear_field_errors(self):
        for label in self._error_labels().values():
            label.clear()
            label.hide()

    def _show_validation_error(self, exc):
        if not isinstance(exc, ValidacionError):
            QMessageBox.critical(self, "Error", str(exc))
            return

        errors = getattr(exc, "errors", None) or exc.args[0]

        field_labels = self._error_labels()
        general_messages = []

        for field, messages in errors.items():
            if isinstance(messages, str):
                messages = [messages]
            elif not isinstance(messages, (list, tuple)):
                messages = [messages]

            text = " ".join(str(message) for message in messages)

            if field in field_labels:
                label = field_labels[field]
                label.setText(text)
                label.show()
            else:
                # GENERAL u otro campo que el formulario no muestra
                general_messages.append(text)

        if general_messages:
            QMessageBox.warning(
                self,
                "Revisa los datos",
                "\n".join(general_messages),
            )

    def accept(self):
        self._clear_field_errors()

        try:
            self.controller.update(self.buy_id, self._get_data())
        except Exception as exc:
            self._show_validation_error(exc)
            return  # el diálogo sigue abierto para corregir

        super().accept()
