import qt_core as qt
from gui.pages.main_pages import MainPages
from gui.widgets.right_column import RightColumn


class Content(qt.QFrame):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        bg_color = theme['colors'].get('background')
        self.setStyleSheet(f"background-color: {bg_color};")

        self.layout = qt.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.pages = MainPages(theme, self)
        self.right_column = RightColumn(theme, self)

        self.add_layout()

    def add_layout(self):
        self.layout.addWidget(self.pages)
        self.layout.addWidget(self.right_column)
