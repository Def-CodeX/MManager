import qt_core as qt
from gui.core.settings import Settings
from gui.widgets.frame_content import FrameContent
from gui.widgets.left_menu import LeftMenu


class CentralWidget(object):
    def __init__(self, parent: qt.QMainWindow):
        super().__init__()
        parent.setWindowTitle('DefCodex')
        parent.setMinimumSize(qt.QSize(1120, 630))
        parent.setWindowIcon(qt.QIcon('iconn.ico'))

        self.settings = Settings()

        self.central_widget = qt.QFrame(parent)
        self.central_widget.setStyleSheet(f"background-color: {self.settings.theme.get('warning')}")
        self.main_layout = qt.QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.left_menu = LeftMenu(self.settings.theme)
        self.frame_content = FrameContent(self.settings.theme)

        self.add_layout()
        self.setup_collapse()
        parent.setCentralWidget(self.central_widget)

    def add_layout(self):
        self.main_layout.addWidget(self.left_menu)
        self.main_layout.addWidget(self.frame_content)

    def setup_collapse(self):
        self.left_menu.button_toggle_menu.clicked.connect(
            lambda: self.toogle_block(self.left_menu)
        )

        self.left_menu.button_toggle_left_column.clicked.connect(
            lambda: self.toogle_block(self.frame_content.right_column, 0, 0)
        )
        self.left_menu.button_toggle_left_column.clicked.connect(
            lambda: self.toogle_block(self.frame_content.left_column, 0)
        )

        self.frame_content.content.top_bar.button_toggle_right_column.clicked.connect(
            lambda: self.toogle_block(self.frame_content.left_column, 0, 0)
        )
        self.frame_content.content.top_bar.button_toggle_right_column.clicked.connect(
            lambda: self.toogle_block(self.frame_content.right_column, 0, 300)
        )

    @staticmethod
    @qt.Slot(qt.QFrame)
    def toogle_block(target, retracted = 50, expanded = 250):
        if hasattr(target, 'minimumWidth') and hasattr(target, 'width'):
            target_width = target.width()
            width = retracted

            if target_width == retracted:
                width = expanded

            target.animation = qt.QPropertyAnimation(target, b"minimumWidth")
            target.animation.setStartValue(target_width)
            target.animation.setEndValue(width)
            target.animation.setDuration(500)
            target.animation.setEasingCurve(qt.QEasingCurve.Type.InOutCirc)
            target.animation.start()
