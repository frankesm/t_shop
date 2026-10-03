from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtWidgets import (
    QFrame,
    QStackedWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QDateEdit,
    QLineEdit,
    QFormLayout,
    QPushButton,
    QScrollArea,
    QWidget,
    QMessageBox,
)

from apps.shop.ui.buy.product_row import ProductRow
from shared.exceptions import GENERAL, ValidacionError


# Ajusta estos imports a tu proyecto
# from shared.exceptions import ValidacionError, GENERAL
# from apps.shop.ui.buy.product_row import ProductRow


class NewBuyPanel(QFrame):
    saved = Signal()
    closed = Signal()

    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        self.rows: list[ProductRow] = []

        self.setFixedWidth(420)
        self.setFrameShape(QFrame.StyledPanel)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_buy_page())
        self.stack.addWidget(self._build_products_page())

        layout = QVBoxLayout(self)
        layout.addWidget(self.stack)

        self.reset()

    # -- paso 1: compra
    def _build_buy_page(self) -> QWidget:
        page = QWidget()

        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("<h3>Nueva compra</h3><i>Paso 1 de 2</i>"))

        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("dd/MM/yyyy")

        self.code = QLineEdit()
        self.code.setPlaceholderText("Código de la compra")

        self.other_cost = QLineEdit()
        self.other_cost.setPlaceholderText("0.00 Opcional")

        self.transport = QLineEdit()
        self.transport.setPlaceholderText("0.00 Opcional")

        self.date_error = QLabel()
        self.code_error = QLabel()
        self.other_cost_error = QLabel()
        self.transport_error = QLabel()

        self._configure_error_label(self.date_error)
        self._configure_error_label(self.code_error)
        self._configure_error_label(self.other_cost_error)
        self._configure_error_label(self.transport_error)

        date_container = self._field_container(
            self.date,
            self.date_error,
        )

        code_container = self._field_container(
            self.code,
            self.code_error,
        )

        other_cost_container = self._field_container(
            self.other_cost,
            self.other_cost_error,
        )

        transport_container = self._field_container(
            self.transport,
            self.transport_error,
        )

        form = QFormLayout()

        form.addRow(
            "Fecha",
            date_container,
        )

        form.addRow(
            "Código",
            code_container,
        )

        form.addRow(
            "Otros costos",
            other_cost_container,
        )

        form.addRow(
            "Costo de Transporte",
            transport_container,
        )

        layout.addLayout(form)
        layout.addStretch()

        cancel = QPushButton("Cancelar")
        cancel.clicked.connect(self.closed.emit)

        next_btn = QPushButton("Siguiente →")
        next_btn.clicked.connect(self._go_products)

        buttons = QHBoxLayout()
        buttons.addWidget(cancel)
        buttons.addStretch()
        buttons.addWidget(next_btn)

        layout.addLayout(buttons)

        return page

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

    def _buy_data(self) -> dict:
        return {
            "date": self.date.date().toPython(),
            "code": self.code.text(),
            "other_cost": self.other_cost.text(),
            "transportation_cost": self.transport.text(),
        }

    def _go_products(self):
        self._clear_field_errors()

        try:
            self.controller.validate(self._buy_data())
        except Exception as exc:
            self._show_validation_error(exc)
            return

        self.stack.setCurrentIndex(1)

    # -- paso 2: productos
    def _build_products_page(self) -> QWidget:
        page = QWidget()

        layout = QVBoxLayout(page)

        layout.addWidget(QLabel("<h3>Productos</h3><i>Paso 2 de 2</i>"))

        self.rows_layout = QVBoxLayout()
        self.rows_layout.setAlignment(Qt.AlignTop)

        container = QWidget()
        container.setLayout(self.rows_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)

        layout.addWidget(scroll, 1)

        add = QPushButton("+ Agregar producto")
        add.clicked.connect(self.add_row)

        layout.addWidget(add)

        back = QPushButton("← Atrás")
        back.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        register = QPushButton("Registrar")
        register.clicked.connect(self._register)

        buttons = QHBoxLayout()
        buttons.addWidget(back)
        buttons.addStretch()
        buttons.addWidget(register)

        layout.addLayout(buttons)

        return page

    def add_row(self):
        row = ProductRow(self.remove_row)

        self.rows.append(row)
        self.rows_layout.addWidget(row)

    def remove_row(self, row):
        if len(self.rows) == 1:
            return

        self.rows.remove(row)
        self.rows_layout.removeWidget(row)
        row.deleteLater()

    def _register(self):
        self._clear_field_errors()

        data = {
            **self._buy_data(),
            "products": [row.data() for row in self.rows],
        }

        try:
            self.controller.create(data)
        except Exception as exc:
            self._show_validation_error(exc)
            return

        self.saved.emit()

    # -- errores
    def _clear_field_errors(self):
        for label in (
            self.date_error,
            self.code_error,
            self.other_cost_error,
            self.transport_error,
        ):
            label.clear()
            label.hide()

        for row in self.rows:
            row.clear_errors()

    def _show_validation_error(self, exc):
        if not isinstance(exc, ValidacionError):
            QMessageBox.critical(
                self,
                "Error",
                str(exc),
            )
            return

        errors = getattr(exc, "errors", None) or exc.args[0]

        general_messages = []

        field_labels = {
            "date": self.date_error,
            "code": self.code_error,
            "other_cost": self.other_cost_error,
            "transportation_cost": self.transport_error,
        }

        for field, messages in errors.items():
            if field in field_labels:
                label = field_labels[field]

                if isinstance(messages, str):
                    messages = [messages]

                label.setText(" ".join(str(message) for message in messages))
                label.show()

            elif field == "products":
                self._show_product_errors(
                    messages,
                    general_messages,
                )

            elif field == GENERAL:
                if isinstance(messages, str):
                    messages = [messages]

                general_messages.extend(messages)

        if general_messages:
            QMessageBox.warning(
                self,
                "Revisa los datos",
                "\n".join(str(message) for message in general_messages),
            )

    def _show_product_errors(
        self,
        messages,
        general_messages,
    ):
        if isinstance(messages, str):
            messages = [messages]

        if not isinstance(messages, (list, tuple)):
            general_messages.append(str(messages))
            return

        for row_index, product_errors in enumerate(messages):
            if not product_errors:
                continue

            # Mensaje a nivel de la lista (no de una fila), p. ej. códigos repetidos
            if isinstance(product_errors, str):
                self._show_repeated_code_error(product_errors, general_messages)
                continue

            if row_index >= len(self.rows):
                general_messages.append(f"Producto {row_index + 1}: {product_errors}")
                continue

            if not isinstance(product_errors, dict):
                general_messages.append(f"Producto {row_index + 1}: {product_errors}")
                continue

            self.rows[row_index].show_errors(product_errors)

    def _show_repeated_code_error(self, message, general_messages):
        codes = [str(row.data().get("code", "")).strip() for row in self.rows]

        marked = False
        for row, code in zip(self.rows, codes):
            if code and codes.count(code) > 1:
                row.show_errors({"code": [message]})
                marked = True

        # Si no se pudo ubicar ninguna fila, el mensaje no se pierde
        if not marked:
            general_messages.append(message)

    def reset(self):
        for row in self.rows:
            self.rows_layout.removeWidget(row)
            row.deleteLater()

        self.rows.clear()

        self.date.setDate(QDate.currentDate())
        self.code.clear()
        self.other_cost.clear()
        self.transport.clear()

        self._clear_field_errors()

        self.add_row()
        self.stack.setCurrentIndex(0)
