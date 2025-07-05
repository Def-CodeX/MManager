import qt_core as qt
from gui.widgets.content import Content
from gui.widgets.left_column import LeftColumn
from gui.widgets.right_column import RightColumn


class FrameContent(qt.QFrame):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.layout = qt.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.left_column = LeftColumn(theme)
        self.content = Content(theme)
        self.right_column = RightColumn(theme)

        self.add_layout()

    def add_layout(self):
        self.layout.addWidget(self.left_column)
        self.layout.addWidget(self.content)
        self.layout.addWidget(self.right_column)
