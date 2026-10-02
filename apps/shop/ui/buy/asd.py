from decimal import Decimal

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDialog,
    QDateEdit,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class EditBuyDialog(QDialog):
    def __init__(self, controller, buy, parent=None):
        super().__init__(parent)

        self.controller = controller
        self.buy_id = buy["id"]

        self.setWindowTitle("Actualizar compra")
        self.setModal(True)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        d = buy["date"]
        self.date_edit.setDate(QDate(d.year, d.month, d.day))

        self.code_input = QLineEdit(buy["code"] or "")

        self.other_cost = self._money_spin(buy["other_cost"])
        self.transportation_cost = self._money_spin(buy["transportation_cost"])

        form = QFormLayout()
        form.addRow("Fecha", self.date_edit)
        form.addRow("Código", self.code_input)
        form.addRow("Otros costos", self.other_cost)
        form.addRow("Costo de transporte", self.transportation_cost)

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

    @staticmethod
    def _money_spin(value):
        spin = QDoubleSpinBox()
        spin.setDecimals(2)
        spin.setRange(0, 10**12)
        spin.setGroupSeparatorShown(True)
        spin.setValue(float(value))
        return spin

    def _get_data(self):
        return {
            "date": self.date_edit.date().toPython(),
            "code": self.code_input.text().strip(),
            "other_cost": Decimal(f"{self.other_cost.value():.2f}"),
            "transportation_cost": Decimal(f"{self.transportation_cost.value():.2f}"),
        }

    def accept(self):
        try:
            self.controller.update(self.buy_id, self._get_data())
        except Exception as exc:
            QMessageBox.warning(self, "Error", f"No se pudo actualizar:\n{exc}")
            return  # el diálogo sigue abierto para corregir

        super().accept()
