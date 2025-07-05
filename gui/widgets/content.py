import qt_core as qt
from gui.widgets.top_bar import TopBar
from gui.widgets.bottom_bar import BottomBar


class Content(qt.QFrame):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        bg_color = theme['colors'].get('background')
        self.setStyleSheet(f"background-color: {bg_color};")

        self.layout = qt.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.top_bar = TopBar(theme)
        self.pages = qt.QStackedWidget()
        self.bottom_bar = BottomBar(theme)

        self.add_layout()

    def add_layout(self):
        self.layout.addWidget(self.top_bar)
        self.layout.addWidget(self.pages)
        self.layout.addWidget(self.bottom_bar)
