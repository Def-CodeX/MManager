import qt_core as qt
from gui.core.settings import Settings
from gui.widgets.frame_content import FrameContent
from gui.widgets.left_menu import LeftMenu


class CentralWidget(object):
    def __init__(self, parent: qt.QMainWindow):
        super().__init__()
        self.settings = Settings()
        self.theme = self.settings.get_theme("DefCodeX Dark")
        self.font = qt.QFont(self.theme['font'].get('family'), self.theme['font'].get('size'))

        parent.setWindowTitle('MManager')
        parent.setMinimumSize(qt.QSize(1370, 800))
        parent.setWindowIcon(qt.QIcon('iconn.ico'))

        self.central_widget = qt.QFrame(parent)
        self.central_widget.setStyleSheet(f"background-color: {self.theme['colors'].get('black')}")
        self.main_layout = qt.QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.left_menu = LeftMenu(self.theme)
        self.frame_content = FrameContent(self.theme, self.central_widget)

        self.add_layout()
        self.apply_fonts()
        self.setup_collapse()
        self.toogle_pages()
        parent.setCentralWidget(self.central_widget)

    def add_layout(self):
        self.main_layout.addWidget(self.left_menu)
        self.main_layout.addWidget(self.frame_content)

    def apply_fonts(self):
        for child in self.central_widget.findChildren(qt.QWidget):
            child.setFont(self.font)

    def setup_collapse(self):
        self.left_menu.button_toggle_menu.clicked.connect(
            lambda: self.toogle_block(self.left_menu)
        )

        self.left_menu.button_toggle_left_column.clicked.connect(
            lambda: self.toogle_block(self.frame_content.content.right_column, 0, 0)
        )
        self.left_menu.button_toggle_left_column.clicked.connect(
            lambda: self.toogle_block(self.frame_content.left_column, 0)
        )

        self.frame_content.top_bar.button_toggle_right_column.clicked.connect(
            lambda: self.toogle_block(self.frame_content.left_column, 0, 0)
        )
        self.frame_content.top_bar.button_toggle_right_column.clicked.connect(
            lambda: self.toogle_block(self.frame_content.content.right_column, 0, 350)
        )

    @staticmethod
    @qt.Slot(qt.QObject, int, int)
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

    @qt.Slot()
    def toogle_pages(self):
        pages = self.frame_content.content.pages
        set_current = self.frame_content.content.pages.setCurrentWidget

        self.frame_content.top_bar.button_close.clicked.connect(
            lambda : set_current(pages.none_page)
        )

        self.left_menu.button_home.clicked.connect(
            lambda : set_current(pages.home_page)
        )

        self.left_menu.button_command.clicked.connect(
            lambda : set_current(pages.command_page)
        )

        self.left_menu.button_build.clicked.connect(
            lambda : set_current(pages.build_page)
        )

        self.left_menu.button_obfuscate.clicked.connect(
            lambda : set_current(pages.obfuscate_page)
        )

        self.left_menu.button_source.clicked.connect(
            lambda : set_current(pages.source_page)
        )

        self.left_menu.button_logs.clicked.connect(
            lambda : set_current(pages.logs_page)
        )
