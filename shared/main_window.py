from PySide6.QtWidgets import QMainWindow, QTabWidget

from config.router import router
from config.settings import APP_NAME, WINDOW_SIZE


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(*WINDOW_SIZE)

        self.tabs = QTabWidget()
        for controller in router.controllers:
            self.tabs.addTab(controller.build_ui(), controller.titulo)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.setCentralWidget(self.tabs)

    def on_tab_changed(self, index):
        widget = self.tabs.widget(index)
        if hasattr(widget, "refresh"):
            widget.refresh()
