from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from apps.shop.ui.buy.new_buy_panel import NewBuyPanel


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
                "Costo de productos",
                "Otros costos",
                "Costo de Transporte",
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
        expanded = {
            self.tree.topLevelItem(i).data(0, Qt.UserRole)
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
            item = QTreeWidgetItem(
                [
                    buy["code"],
                    buy["date"].strftime("%d/%m/%Y"),
                    f'{buy["product_count"]} productos',
                    f'{buy["product_cost"]:,.2f}',
                    f'{buy["other_cost"]:,.2f}',
                    f'{buy["transportation_cost"]:,.2f}',
                    f'{buy["total_cost"]:,.2f}',
                ]
            )

            item.setData(
                0,
                Qt.UserRole,
                buy["id"],
            )

            for product in buy["products"]:
                child = QTreeWidgetItem(
                    [
                        f'{product["code"]} - {product["name"]}',
                        "",
                        f'{product["amount"]} {product["unit"]}',
                        f'{product["buy_cost"]:,.2f}',
                        "",
                        "",
                        "",
                    ]
                )

                for col in range(2, 7):
                    child.setTextAlignment(col, right)

                item.addChild(child)

            for col in range(2, 7):
                item.setTextAlignment(col, right)

            self.tree.addTopLevelItem(item)

            item.setExpanded(buy["id"] in expanded)
