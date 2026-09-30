from PySide6.QtWidgets import (
    QFrame,
    QLineEdit,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QFormLayout,
    QVBoxLayout,
    QWidget,
)


class ProductRow(QFrame):
    def __init__(self, on_remove):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)

        self.code = QLineEdit()
        self.name = QLineEdit()
        self.unit = QLineEdit("Unidades")
        self.amount = QLineEdit("1")
        self.cost = QLineEdit()
        self.cost.setPlaceholderText("0.00")

        self.code_error = QLabel()
        self.name_error = QLabel()
        self.unit_error = QLabel()
        self.amount_error = QLabel()
        self.cost_error = QLabel()

        for label in (
            self.code_error,
            self.name_error,
            self.unit_error,
            self.amount_error,
            self.cost_error,
        ):
            self._configure_error_label(label)

        remove = QPushButton("✕")
        remove.setFixedWidth(28)
        remove.setToolTip("Quitar producto")
        remove.clicked.connect(lambda: on_remove(self))

        header = QHBoxLayout()
        header.addWidget(QLabel("<b>Producto</b>"))
        header.addStretch()
        header.addWidget(remove)

        form = QFormLayout()

        form.addRow(
            "Código",
            self._field_container(
                self.code,
                self.code_error,
            ),
        )

        form.addRow(
            "Nombre",
            self._field_container(
                self.name,
                self.name_error,
            ),
        )

        form.addRow(
            "Unidad",
            self._field_container(
                self.unit,
                self.unit_error,
            ),
        )

        form.addRow(
            "Cantidad",
            self._field_container(
                self.amount,
                self.amount_error,
            ),
        )

        form.addRow(
            "Costo",
            self._field_container(
                self.cost,
                self.cost_error,
            ),
        )

        layout = QVBoxLayout(self)
        layout.addLayout(header)
        layout.addLayout(form)

    @staticmethod
    def _configure_error_label(label: QLabel):
        label.setStyleSheet("color: #dc3545; font-size: 11px;")
        label.setWordWrap(True)
        label.hide()

    @staticmethod
    def _field_container(
        field: QWidget,
        error_label: QLabel,
    ) -> QWidget:
        container = QWidget()

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # El error aparece SOBRE el campo.
        layout.addWidget(error_label)
        layout.addWidget(field)

        return container

    def clear_errors(self):
        for label in (
            self.code_error,
            self.name_error,
            self.unit_error,
            self.amount_error,
            self.cost_error,
        ):
            label.clear()
            label.hide()

    def show_errors(self, errors: dict):
        field_labels = {
            "code": self.code_error,
            "name": self.name_error,
            "unit": self.unit_error,
            "amount": self.amount_error,
            "buy_cost": self.cost_error,
            "cost": self.cost_error,
        }

        for field, messages in errors.items():
            label = field_labels.get(field)

            if label is None:
                continue

            if isinstance(messages, str):
                messages = [messages]

            label.setText(" ".join(str(message) for message in messages))
            label.show()

    def data(self) -> dict:
        return {
            "code": self.code.text(),
            "name": self.name.text(),
            "unit": self.unit.text(),
            "amount": self.amount.text(),
            "buy_cost": self.cost.text(),
        }
