import qt_core as qt
from core import Func
from gui.widgets.ui_push_button import UiPushButton


class TopBar(qt.QFrame):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(25)
        self.setMaximumHeight(25)
        self.setStyleSheet(f"background-color: {theme['colors'].get('bar')};")

        # noinspection PyTypeChecker
        self.core: Func = self.window()
        self.connector = self.core.connector
        self.commander = self.core.commander

        self.layout = qt.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.button_close = UiPushButton(
            theme,
            text="MManager",
            tooltip="Close",
            icon_path="shield-plus.svg",
            icon_bg=theme['colors'].get('bar'),
            margin=0,
            icon_size=18,
            height=25
        )
        self.spacer1 = qt.QSpacerItem(0, 0, qt.QSizePolicy.Policy.Expanding, qt.QSizePolicy.Policy.Minimum)

        # Connection selected frame
        self.selected_frame = qt.QFrame(self)
        self.selected_frame.setStyleSheet(f"background-color: {theme['colors'].get('column')};")

        self.selected_frame_layout = qt.QHBoxLayout(self.selected_frame)
        self.selected_frame_layout.setContentsMargins(0, 0, 0, 0)
        self.selected_frame_layout.setSpacing(0)

        self.selected_label = qt.QLabel(self, text="Command: BROADCAST")
        self.selected_label.setMinimumWidth(350)
        self.selected_label.setAlignment(qt.Qt.AlignmentFlag.AlignCenter)

        self.button_deselect = UiPushButton(
            theme,
            self,
            text="Deselect",
            icon_path="plug-circle-minus.svg",
            icon_bg=theme['colors'].get('column'),
            margin=0,
            icon_size=18,
            height=25
        )

        self.spacer2 = qt.QSpacerItem(0, 0, qt.QSizePolicy.Policy.Expanding, qt.QSizePolicy.Policy.Minimum)
        self.button_toggle_right_column = UiPushButton(
            theme,
            self,
            tooltip="Settings",
            icon_path="settings.svg",
            icon_bg=theme['colors'].get('bar'),
            margin=0,
            icon_size=18,
            height=25
        )

        self.add_layout()

        self.button_deselect.clicked.connect(self.deselect_connection_commander)

        self.commander.connection_select.connect(self.on_connection_select)
        self.commander.connection_deselect.connect(self.on_connection_deselect)

        self.commander.connection_update.connect(self.on_connection_select)

    def add_layout(self):
        self.selected_frame_layout.addWidget(self.selected_label)
        self.selected_frame_layout.addWidget(self.button_deselect)

        self.layout.addWidget(self.button_close)
        self.layout.addSpacerItem(self.spacer1)
        self.layout.addWidget(self.selected_frame)
        self.layout.addSpacerItem(self.spacer2)
        self.layout.addWidget(self.button_toggle_right_column)

    @qt.Slot()
    def deselect_connection_commander(self):
        self.commander.deselect_connection()

    @qt.Slot(str)
    def on_connection_select(self, conn_id: str):
        connection = self.connector.get_connection(conn_id)
        if not connection:
            self.selected_label.setText("Command: Connection not valid")
            return

        if conn_id != self.commander.selected_connection:
            return

        status = connection.get('status')
        if connection.get('status') == 'Connected':
            status += f" ({connection.get('target')})"

        text = f"Command: {conn_id} [{connection.get('host')}:{connection.get('port')} -> {status}]"
        self.selected_label.setText(text)

    @qt.Slot()
    def on_connection_deselect(self):
        self.selected_label.setText("Command: BROADCAST")
