from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QTreeWidgetItem,
    QMessageBox,
    QTableWidgetItem,
    QHeaderView,
    QTableWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTreeWidget,
    QWidget,
    QSizePolicy,
)

from apps.shop.ui.buy.new_buy_panel import NewBuyPanel


class BuyView(QWidget):
    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        self.product_tables = {}

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
                "Costo Unitario",
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

        self.tree.itemExpanded.connect(
            self._on_item_expanded,
        )

        self.tree.itemCollapsed.connect(
            self._on_item_collapsed,
        )

        self.tree.verticalScrollBar().valueChanged.connect(
            self._position_product_tables,
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

    def _build_products_table(self, products):
        table = QTableWidget(
            len(products),
            6,
            self.tree.viewport(),
        )

        table.setHorizontalHeaderLabels(
            [
                "Código",
                "Nombre",
                "Unidad",
                "Cantidad",
                "Costo unitario",
                "Costo total",
            ]
        )

        table.setAlternatingRowColors(True)

        table.setEditTriggers(
            QTableWidget.NoEditTriggers,
        )

        table.setSelectionMode(
            QTableWidget.NoSelection,
        )

        table.setFocusPolicy(
            Qt.NoFocus,
        )

        table.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff,
        )

        table.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff,
        )

        table.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )

        header = table.horizontalHeader()
        header.setStretchLastSection(False)

        for col in range(6):
            header.setSectionResizeMode(
                col,
                QHeaderView.Stretch,
            )

        right = Qt.AlignRight | Qt.AlignVCenter

        for row, product in enumerate(products):
            values = [
                product["code"],
                product["name"],
                product["unit"],
                str(product["amount"]),
                f'{product["unit_cost"]:,.2f}',
                f'{product["buy_cost"]:,.2f}',
            ]

            for col, value in enumerate(values):
                item = QTableWidgetItem(value)

                if col >= 3:
                    item.setTextAlignment(right)

                table.setItem(
                    row,
                    col,
                    item,
                )

        table.resizeRowsToContents()

        height = table.horizontalHeader().height()

        for row in range(table.rowCount()):
            height += table.rowHeight(row)

        table.setFixedHeight(height + 2)

        return table

    def _position_product_tables(self):
        viewport = self.tree.viewport()

        for item, table in self.product_tables.items():
            if not item.isExpanded():
                table.hide()
                continue

            child = item.child(0)

            if child is None:
                table.hide()
                continue

            rect = self.tree.visualItemRect(child)

            if not rect.isValid():
                table.hide()
                continue

            table.setGeometry(
                0,
                rect.top(),
                viewport.width(),
                table.height(),
            )

            table.raise_()
            table.show()

    def _on_item_expanded(self, item):
        self._position_product_tables()

    def _on_item_collapsed(self, item):
        table = self.product_tables.get(item)

        if table:
            table.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)

        self._position_product_tables()

    def refresh(self):
        expanded = {
            self.tree.topLevelItem(i).data(
                0,
                Qt.UserRole,
            )
            for i in range(self.tree.topLevelItemCount())
            if self.tree.topLevelItem(i).isExpanded()
        }

        for table in self.product_tables.values():
            table.deleteLater()

        self.product_tables.clear()

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

            for col in range(2, 7):
                item.setTextAlignment(
                    col,
                    right,
                )

            products_item = QTreeWidgetItem(item)

            products_table = self._build_products_table(
                buy["products"],
            )

            self.product_tables[item] = products_table

            products_item.setSizeHint(
                0,
                QSize(
                    0,
                    products_table.height(),
                ),
            )

            self.tree.addTopLevelItem(item)

            item.setExpanded(
                buy["id"] in expanded,
            )

        self._position_product_tables()
