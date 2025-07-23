import qt_core as qt
from gui.widgets.bottom_bar import BottomBar
from gui.widgets.content import Content
from gui.widgets.left_column import LeftColumn
from gui.widgets.top_bar import TopBar


class FrameContent(qt.QFrame):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.layout = qt.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.left_column = LeftColumn(theme, self)

        self.subframe = qt.QFrame(self)
        self.subframe_layout = qt.QVBoxLayout(self.subframe)
        self.subframe_layout.setContentsMargins(0, 0, 0, 0)
        self.subframe_layout.setSpacing(0)

        self.top_bar = TopBar(theme, self.subframe)
        self.content = Content(theme, self.subframe)
        self.bottom_bar = BottomBar(theme, self.subframe)


        self.add_layout()

    def add_layout(self):
        self.layout.addWidget(self.left_column)
        self.layout.addWidget(self.subframe)

        self.subframe_layout.addWidget(self.top_bar)
        self.subframe_layout.addWidget(self.content)
        self.subframe_layout.addWidget(self.bottom_bar)
