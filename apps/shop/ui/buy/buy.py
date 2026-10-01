from PySide6.QtCore import Qt, QSize, QTimer, QDate
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
    QSizePolicy,
    QWidget,
    QLineEdit,
    QMenu,
    QDateEdit,
    QDialog,
)

from apps.shop.ui.buy.new_buy_panel import NewBuyPanel


class BuyView(QWidget):
    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        self.product_tables = {}

        self.code_filter = ""

        self.date_after = None
        self.date_before = None

        self.ordering = None
        self.ordering_desc = False

        self.tree = QTreeWidget()
        self.tree.setColumnCount(7)

        self.tree.setHeaderLabels(
            [
                "Código",
                "Fecha",
                "Cantidad de productos",
                "Costo productos",
                "Otros costos",
                "Costo de Transporte",
                "Costo Total",
            ]
        )

        self.tree.setAlternatingRowColors(True)

        header = self.tree.header()

        header.setStretchLastSection(False)
        header.setSectionsClickable(True)
        header.setSortIndicatorShown(False)

        for col in range(7):
            header.setSectionResizeMode(
                col,
                QHeaderView.Stretch,
            )

        header.sectionClicked.connect(
            self._on_header_clicked,
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

        # -------------------------------------------------
        # Filtros
        # -------------------------------------------------

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Filtrar por código...")
        self.code_input.setClearButtonEnabled(True)
        self.code_input.setFixedWidth(220)

        self.code_input.textChanged.connect(
            self._on_code_changed,
        )

        self.btn_date_filter = QPushButton("Filtrar por fecha")
        self.btn_date_filter.clicked.connect(
            self._show_date_filter_menu,
        )

        self.btn_clear_filters = QPushButton("Limpiar filtros")
        self.btn_clear_filters.clicked.connect(
            self._clear_filters,
        )

        filters = QHBoxLayout()

        filters.addWidget(
            self.code_input,
        )

        filters.addWidget(
            self.btn_date_filter,
        )

        filters.addWidget(
            self.btn_clear_filters,
        )

        filters.addStretch()

        # -------------------------------------------------
        # Layout principal
        # -------------------------------------------------

        left = QVBoxLayout()

        left.addLayout(top)
        left.addLayout(filters)
        left.addWidget(self.tree)

        self.panel = NewBuyPanel(controller)
        self.panel.hide()

        self.panel.saved.connect(self._on_saved)
        self.panel.closed.connect(self.close_panel)

        root = QHBoxLayout(self)
        root.addLayout(left, 1)
        root.addWidget(self.panel)

        self.refresh()

    # -----------------------------------------------------
    # Panel de nueva compra
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Filtros y ordenamiento
    # -----------------------------------------------------

    def _get_filters(self):
        filters = {}

        if self.code_filter:
            filters["code"] = self.code_filter

        if self.date_after is not None:
            filters["date_after"] = self.date_after.toPython()

        if self.date_before is not None:
            filters["date_before"] = self.date_before.toPython()

        if self.ordering is not None:
            filters["ordering"] = self.ordering
            filters["ordering_desc"] = self.ordering_desc

        return filters

    def _on_code_changed(self, value):
        self.code_filter = value.strip()
        self.refresh()

    def _on_header_clicked(self, column):
        ordering_fields = {
            0: "code",
            1: "date",
            2: "product_count",
            3: "product_cost",
            4: "other_cost",
            5: "transportation_cost",
            6: "total_cost",
        }

        ordering = ordering_fields[column]

        if self.ordering == ordering:
            self.ordering_desc = not self.ordering_desc
        else:
            self.ordering = ordering
            self.ordering_desc = False

        self.tree.header().setSortIndicator(
            column,
            (Qt.DescendingOrder if self.ordering_desc else Qt.AscendingOrder),
        )

        self.tree.header().setSortIndicatorShown(True)

        self.refresh()

    # -----------------------------------------------------
    # Filtro por fecha
    # -----------------------------------------------------

    def _show_date_filter_menu(self):
        menu = QMenu(self)

        after_action = menu.addAction("Después de")

        before_action = menu.addAction("Antes de")

        clear_action = menu.addAction("Limpiar filtro de fecha")

        action = menu.exec(
            self.btn_date_filter.mapToGlobal(self.btn_date_filter.rect().bottomLeft())
        )

        if action == after_action:
            self._open_date_dialog(after=True)

        elif action == before_action:
            self._open_date_dialog(after=False)

        elif action == clear_action:
            self.date_after = None
            self.date_before = None

            self._update_date_button()
            self.refresh()

    def _open_date_dialog(self, after):
        dialog = QDialog(self)

        dialog.setWindowTitle("Filtrar por fecha")

        layout = QVBoxLayout(dialog)

        if after:
            label = QLabel("Mostrar compras después de:")

            current_date = (
                self.date_after if self.date_after is not None else QDate.currentDate()
            )

        else:
            label = QLabel("Mostrar compras antes de:")

            current_date = (
                self.date_before
                if self.date_before is not None
                else QDate.currentDate()
            )

        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(current_date)

        btn_apply = QPushButton("Aplicar")
        btn_cancel = QPushButton("Cancelar")

        buttons = QHBoxLayout()

        buttons.addWidget(btn_cancel)
        buttons.addWidget(btn_apply)

        layout.addWidget(label)
        layout.addWidget(date_edit)
        layout.addLayout(buttons)

        btn_cancel.clicked.connect(
            dialog.reject,
        )

        def apply():
            selected_date = date_edit.date()

            if after:
                self.date_after = selected_date
            else:
                self.date_before = selected_date

            self._update_date_button()

            dialog.accept()
            self.refresh()

        btn_apply.clicked.connect(apply)

        dialog.exec()

    def _update_date_button(self):
        if self.date_after is None and self.date_before is None:
            self.btn_date_filter.setText("Filtrar por fecha")
            return

        filters = []

        if self.date_after is not None:
            filters.append("Después de " + self.date_after.toString("dd/MM/yyyy"))

        if self.date_before is not None:
            filters.append("Antes de " + self.date_before.toString("dd/MM/yyyy"))

        self.btn_date_filter.setText(" | ".join(filters))

    def _clear_filters(self):
        self.code_filter = ""

        self.date_after = None
        self.date_before = None

        self.ordering = None
        self.ordering_desc = False

        self.code_input.clear()

        self._update_date_button()

        self.tree.header().setSortIndicatorShown(False)

        self.refresh()

    # -----------------------------------------------------
    # Tabla de productos
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Posicionamiento de tablas de productos
    # -----------------------------------------------------

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

    def _schedule_reposition(self):
        QTimer.singleShot(
            0,
            self._position_product_tables,
        )

    def _on_item_expanded(self, item):
        self._schedule_reposition()

    def _on_item_collapsed(self, item):
        table = self.product_tables.get(item)

        if table:
            table.hide()

        self._schedule_reposition()

    def resizeEvent(self, event):
        super().resizeEvent(event)

        self._position_product_tables()

    # -----------------------------------------------------
    # Carga
    # -----------------------------------------------------

    def refresh(self):
        try:
            buys = self.controller.list(**self._get_filters())

        except Exception as exc:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo cargar el listado:\n{exc}",
            )
            return

        self._populate_tree(buys)

    def _populate_tree(self, buys):
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

            products_item.setFlags(Qt.NoItemFlags)

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

        self._schedule_reposition()
