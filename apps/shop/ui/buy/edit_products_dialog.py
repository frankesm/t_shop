from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from shared.exceptions import ValidacionError, GENERAL


# Ajusta estos imports a tu proyecto
# from shared.exceptions import ValidacionError
# from shared.serializers import GENERAL


class EditProductsDialog(QDialog):
    FIELDS = [
        ("code", "Código"),
        ("name", "Nombre"),
        ("unit", "Unidad"),
        ("amount", "Cantidad"),
        ("buy_cost", "Costo total"),
    ]

    def __init__(self, controller, buy, parent=None):
        super().__init__(parent)

        self.controller = controller
        self.buy_id = buy["id"]
        self.buy_deleted = False
        self.action_col = len(self.FIELDS)

        self.setWindowTitle(f"Productos de la compra {buy['code']}")
        self.setModal(True)
        self.resize(900, 400)

        self.table = QTableWidget(len(buy["products"]), len(self.FIELDS) + 1)
        self.table.setHorizontalHeaderLabels([label for _, label in self.FIELDS] + [""])
        self.table.setAlternatingRowColors(True)

        header = self.table.horizontalHeader()
        for col in range(len(self.FIELDS)):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        header.setSectionResizeMode(self.action_col, QHeaderView.ResizeToContents)

        for row, product in enumerate(buy["products"]):
            self._fill_row(row, product)

        btn_cancel = QPushButton("Cancelar")
        btn_save = QPushButton("Guardar")
        btn_save.setDefault(True)

        btn_cancel.clicked.connect(self.reject)
        btn_save.clicked.connect(self.accept)

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(btn_cancel)
        buttons.addWidget(btn_save)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addLayout(buttons)

    # -- filas
    def _fill_row(self, row, product):
        for col, (field, _) in enumerate(self.FIELDS):
            item = QTableWidgetItem(str(product[field]))
            if col == 0:
                item.setData(Qt.UserRole, product["id"])
            self.table.setItem(row, col, item)

        btn = QPushButton("Eliminar")
        btn.clicked.connect(lambda _=False, b=btn: self._remove_row(b))
        self.table.setCellWidget(row, self.action_col, btn)

    def _remove_row(self, button):
        for row in range(self.table.rowCount()):
            if self.table.cellWidget(row, self.action_col) is button:
                self.table.removeRow(row)
                return

    def _get_rows(self):
        return [
            {
                "id": self.table.item(row, 0).data(Qt.UserRole),
                **{
                    field: self.table.item(row, col).text()
                    for col, (field, _) in enumerate(self.FIELDS)
                },
            }
            for row in range(self.table.rowCount())
        ]

    # -- errores
    def _clear_errors(self):
        for row in range(self.table.rowCount()):
            for col in range(len(self.FIELDS)):
                item = self.table.item(row, col)
                item.setData(Qt.BackgroundRole, None)
                item.setToolTip("")

    @staticmethod
    def _as_text(messages):
        if not isinstance(messages, (list, tuple)):
            messages = [messages]
        return " ".join(str(m) for m in messages)

    def _mark_repeated_codes(self):
        code_col = 0
        codes = [
            self.table.item(row, code_col).text().strip()
            for row in range(self.table.rowCount())
        ]

        for row, code in enumerate(codes):
            if codes.count(code) > 1:
                item = self.table.item(row, code_col)
                item.setBackground(Qt.red)
                item.setToolTip("Código repetido en la tabla.")

    def _show_validation_error(self, exc):
        if not isinstance(exc, ValidacionError):
            QMessageBox.critical(self, "Error", str(exc))
            return

        errors = getattr(exc, "errors", None) or exc.args[0]
        columns = {field: col for col, (field, _) in enumerate(self.FIELDS)}
        general = []
        cell_errors = False

        for field, messages in errors.items():
            if field == GENERAL:
                general.append(self._as_text(messages))
                self._mark_repeated_codes()
                continue

            if field != "products":
                general.append(self._as_text(messages))
                continue

            if not isinstance(messages, (list, tuple)):
                general.append(self._as_text(messages))
                continue

            for row, row_errors in enumerate(messages):
                if not row_errors:
                    continue

                if not isinstance(row_errors, dict):
                    general.append(f"Fila {row + 1}: {self._as_text(row_errors)}")
                    continue

                for name, msgs in row_errors.items():
                    text = self._as_text(msgs)
                    if name in columns and row < self.table.rowCount():
                        item = self.table.item(row, columns[name])
                        item.setBackground(Qt.red)
                        item.setToolTip(text)
                        cell_errors = True
                    else:
                        general.append(f"Fila {row + 1}: {text}")

        if general:
            QMessageBox.warning(self, "Revisa los datos", "\n".join(general))
        elif cell_errors:
            QMessageBox.warning(
                self,
                "Revisa los datos",
                "Hay celdas con errores. Pasa el mouse sobre las celdas en rojo.",
            )

    # -- guardar
    def _confirm_delete_buy(self):
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Question)
        box.setWindowTitle("Compra sin productos")
        box.setText(
            "Se eliminaron todos los productos, por lo que la compra "
            "también se eliminará.\n\n¿Continuar?"
        )
        btn_yes = box.addButton("Sí", QMessageBox.YesRole)
        btn_no = box.addButton("No", QMessageBox.NoRole)
        box.setDefaultButton(btn_no)
        box.exec()
        return box.clickedButton() == btn_yes

    def accept(self):
        self._clear_errors()

        if self.table.rowCount() == 0 and not self._confirm_delete_buy():
            return

        try:
            self.buy_deleted = self.controller.update_products(
                self.buy_id, self._get_rows()
            )
        except Exception as exc:
            self._show_validation_error(exc)
            return

        super().accept()
