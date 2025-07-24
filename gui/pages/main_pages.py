import qt_core as qt
from gui.pages.build_page import BuildPage
from gui.pages.command_page import CommandPage
from gui.pages.home_page import HomePage
from gui.pages.logs_page import LogsPage
from gui.pages.obfuscate_page import ObfuscatePage
from gui.pages.source_page import SourcePage


class MainPages(qt.QStackedWidget):
    class NonePage(qt.QWidget):
        def __init__(self, theme, parent = None):
            super().__init__(parent)
            self.theme = theme
            self.setObjectName("none_pg")

            self.layout = qt.QVBoxLayout(self)
            self.setContentsMargins(10, 10, 10, 10)
            self.layout.setSpacing(0)

            self.label = qt.QLabel(self)
            self.label.setAlignment(qt.Qt.AlignmentFlag.AlignCenter)
            self.label.setPixmap(qt.QPixmap("gui/icons/logo.jpg").scaledToWidth(300))

            self.layout.addWidget(self.label)

    def __init__(self, theme, parent):
        super().__init__(parent)
        self.theme = theme

        self.none_page = self.NonePage(theme, self)
        self.home_page = HomePage(theme, self)
        self.command_page = CommandPage(theme, self)
        self.build_page = BuildPage(theme, self)
        self.obfuscate_page = ObfuscatePage(theme, self)
        self.source_page = SourcePage(theme, self)
        self.logs_page = LogsPage(theme, self)

        self.add_widgets()

    def add_widgets(self):
        self.addWidget(self.none_page)
        self.addWidget(self.home_page)
        self.addWidget(self.command_page)
        self.addWidget(self.build_page)
        self.addWidget(self.obfuscate_page)
        self.addWidget(self.source_page)
        self.addWidget(self.logs_page)

        self.setCurrentWidget(self.none_page)
