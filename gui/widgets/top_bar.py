import qt_core as qt
from gui.widgets.ui_button import UiButton


class TopBar(qt.QFrame):
    def __init__(self, theme, parent=None):
        super().__init__(parent)

        bg_color = theme['colors'].get('bar')

        self.setMinimumHeight(25)
        self.setMaximumHeight(25)
        self.setStyleSheet(f"background-color: {bg_color};")

        self.layout = qt.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.button_close = UiButton(
            theme,
            text="MManager",
            tooltip="Close",
            icon_path="shield-plus.svg",
            icon_bg=theme['colors'].get('bar'),
            margin=0,
            icon_size=18,
            height=25
        )

        self.spacer = qt.QSpacerItem(0, 0, qt.QSizePolicy.Policy.Expanding, qt.QSizePolicy.Policy.Minimum)

        self.button_toggle_right_column = UiButton(
            theme,
            tooltip="Settings",
            icon_path="settings.svg",
            icon_bg=theme['colors'].get('bar'),
            margin=0,
            icon_size=18,
            height=25
        )

        self.add_layout()

    def add_layout(self):
        self.layout.addWidget(self.button_close)
        self.layout.addSpacerItem(self.spacer)
        self.layout.addWidget(self.button_toggle_right_column)
