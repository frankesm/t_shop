import re

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import (
    QDateEdit,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from shared.exceptions import GENERAL, ValidacionError


# ------------------------------------------------------------ fila producto
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

            label.setText(" ".join(messages))
            label.show()

    def data(self) -> dict:
        return {
            "code": self.code.text(),
            "name": self.name.text(),
            "unit": self.unit.text(),
            "amount": self.amount.text(),
            "buy_cost": self.cost.text(),
        }


# ------------------------------------------------------------- panel lateral
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
        self.other_cost.setPlaceholderText("0.00")

        self.transport = QLineEdit()
        self.transport.setPlaceholderText("0.00")

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
            "Transporte",
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

                label.setText(" ".join(messages))
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
                "\n".join(general_messages),
            )

    def _show_product_errors(
        self,
        messages,
        general_messages,
    ):

        if isinstance(messages, str):
            messages = [messages]

        if isinstance(messages, dict):
            self._show_product_errors_dict(
                messages,
                general_messages,
            )
            return

        for message in messages:
            if not isinstance(message, str):
                general_messages.append(str(message))
                continue

            match = re.match(
                r"Producto\s+(\d+):Elemento\s+\d+\s+" r"([a-zA-Z_]+):\s*(.+)",
                message,
            )

            if not match:
                general_messages.append(message)
                continue

            product_number = int(match.group(1))
            field = match.group(2)
            error_message = match.group(3).strip()

            row_index = product_number - 1

            if not 0 <= row_index < len(self.rows):
                general_messages.append(message)
                continue

            self.rows[row_index].show_errors(
                {
                    field: [error_message],
                }
            )

    def _show_product_errors_dict(
        self,
        messages,
        general_messages,
    ):
        for product_key, product_errors in messages.items():
            try:
                row_index = int(product_key) - 1
            except (TypeError, ValueError):
                general_messages.append(f"{product_key}: {product_errors}")
                continue

            if not 0 <= row_index < len(self.rows):
                general_messages.append(f"{product_key}: {product_errors}")
                continue

            if not isinstance(product_errors, dict):
                general_messages.append(str(product_errors))
                continue

            self.rows[row_index].show_errors(product_errors)

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


# --------------------------------------------------------------------- vista
class BuyView(QWidget):
    def __init__(self, controller):
        super().__init__()

        self.controller = controller

        self.tree = QTreeWidget()
        self.tree.setColumnCount(7)

        self.tree.setHeaderLabels(
            [
                "Código",
                "Fecha",
                "Cantidad de productos",
                "Costo productos",
                "Otros costos",
                "Transporte",
                "Costo total",
            ]
        )

        self.tree.setAlternatingRowColors(True)

        header = self.tree.header()
        header.setStretchLastSection(False)

        for col in range(7):
            header.setSectionResizeMode(
                col,
                QHeaderView.Stretch,
            )

        self.btn_new = QPushButton("+ Nueva compra")
        self.btn_new.clicked.connect(self.open_panel)

        top = QHBoxLayout()
        top.addWidget(QLabel(f"<h2>{controller.title}</h2>"))
        top.addStretch()
        top.addWidget(self.btn_new)

        left = QVBoxLayout()
        left.addLayout(top)
        left.addWidget(self.tree)

        self.panel = NewBuyPanel(controller)
        self.panel.hide()

        self.panel.saved.connect(self._on_saved)
        self.panel.closed.connect(self.close_panel)

        root = QHBoxLayout(self)
        root.addLayout(left, 1)
        root.addWidget(self.panel)

        self.refresh()

    def open_panel(self):
        self.panel.reset()
        self.panel.show()
        self.btn_new.setEnabled(False)

    def close_panel(self):
        self.panel.hide()
        self.btn_new.setEnabled(True)

    def _on_saved(self):
        self.close_panel()
        self.refresh()

        QMessageBox.information(
            self,
            "Listo",
            "Compra registrada correctamente.",
        )

    def refresh(self):
        # Recordar qué compras estaban desplegadas.
        expanded = {
            self.tree.topLevelItem(i).data(
                0,
                Qt.UserRole,
            )
            for i in range(self.tree.topLevelItemCount())
            if self.tree.topLevelItem(i).isExpanded()
        }

        self.tree.clear()

        try:
            buys = self.controller.list()
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo cargar el listado:\n{exc}",
            )
            return

        right = Qt.AlignRight | Qt.AlignVCenter

        for buy in buys:
            products = buy["products"]

            product_cost = sum(product["buy_cost"] for product in products)

            other_cost = buy["other_cost"]
            transportation_cost = buy["transportation_cost"]

            total_cost = product_cost + other_cost + transportation_cost

            item = QTreeWidgetItem(
                [
                    buy["code"],
                    buy["date"].strftime("%d/%m/%Y"),
                    f"{len(products)} productos",
                    f"{product_cost:,.2f}",
                    f"{other_cost:,.2f}",
                    f"{transportation_cost:,.2f}",
                    f"{total_cost:,.2f}",
                ]
            )

            item.setData(
                0,
                Qt.UserRole,
                buy["id"],
            )

            for product in products:
                child = QTreeWidgetItem(
                    [
                        f"{product['code']} - {product['name']}",
                        "",
                        f"{product['amount']} {product['unit']}",
                        f"{product['buy_cost']:,.2f}",
                        "",
                        "",
                        "",
                    ]
                )

                for col in range(2, 7):
                    child.setTextAlignment(
                        col,
                        right,
                    )

                item.addChild(child)

            for col in range(2, 7):
                item.setTextAlignment(
                    col,
                    right,
                )

            self.tree.addTopLevelItem(item)

            item.setExpanded(buy["id"] in expanded)
