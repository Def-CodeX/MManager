import qt_core as qt
from gui.widgets.ui_button import UiButton


class LeftMenu(qt.QFrame):
    class Line(qt.QFrame):
        def __init__(self):
            super().__init__()
            self.setFrameShape(qt.QFrame.Shape.HLine)
            self.setFrameShadow(qt.QFrame.Shadow.Plain)
            self.setLineWidth(250)
            self.setMaximumHeight(1)


    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.animation = None
        bg_color = theme['colors'].get('panel')
        self.setMinimumWidth(50)
        self.setMaximumWidth(50)
        self.setStyleSheet(f"background-color: {bg_color};")
        self.layout = qt.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.button_toggle_menu = UiButton(theme, text="Menu", icon_path="icon-menu.svg", margin=0)
        self.line1 = self.Line()

        self.button_home = UiButton(theme, text="Home", icon_path="home.svg")
        self.button_command = UiButton(theme, text="Command", icon_path="pulse.svg")
        self.button_build = UiButton(theme, text="Build", icon_path="tools.svg")
        self.button_obfuscate = UiButton(theme, text="Obfuscate", icon_path="key.svg")
        self.button_source = UiButton(theme, text="Source", icon_path="file-edit.svg")
        self.button_logs = UiButton(theme, text="Logs", icon_path="time-past.svg")
        
        self.spacer = qt.QSpacerItem(0, 0, qt.QSizePolicy.Policy.Minimum, qt.QSizePolicy.Policy.Expanding)

        self.line2 = self.Line()
        self.button_toggle_left_column = UiButton(theme, text="Info", icon_path="comment-info.svg", margin=0)

        self.add_layout()

    def add_layout(self):
        self.layout.addWidget(self.button_toggle_menu)
        self.layout.addWidget(self.line1)
        self.layout.addWidget(self.button_home)
        self.layout.addWidget(self.button_command)
        self.layout.addWidget(self.button_build)
        self.layout.addWidget(self.button_obfuscate)
        self.layout.addWidget(self.button_source)
        self.layout.addWidget(self.button_logs)

        self.layout.addSpacerItem(self.spacer)
        self.layout.addWidget(self.line2)
        self.layout.addWidget(self.button_toggle_left_column)
