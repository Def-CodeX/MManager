import qt_core as qt
from core import Func
from gui.widgets.form_input import FormInput
from gui.widgets.ui_push_button import UiPushButton
from gui.widgets.ui_toggle_button import UiToggleButton


class RightColumn(qt.QFrame):
    def __init__(self, theme, parent=None):
        super().__init__(parent)

        # noinspection PyTypeChecker
        self.core: Func = self.window()
        self.connector = self.core.connector
        self.proxy = self.core.proxy

        bg_color = theme['colors'].get('column')
        border_color = theme['colors'].get('shadow')

        self.setMinimumWidth(0)
        self.setMaximumWidth(0)
        self.setStyleSheet(f"background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 10px;")

        self.layout = qt.QFormLayout(self)
        self.layout.setContentsMargins(0, 10, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setVerticalSpacing(10)

        # Proxy Info
        self.proxy_host_line = qt.QLineEdit(self, placeholderText="Host")
        self.proxy_host_line.setStyleSheet(f"background-color: {theme['colors'].get('background')}; ")

        self.proxy_port_line = qt.QLineEdit(self, placeholderText="Port")
        self.proxy_port_line.setStyleSheet(f"background-color: {theme['colors'].get('background')}; ")
        self.proxy_port_line.setValidator(qt.QIntValidator(1, 65535))

        self.proxy_info_input = FormInput(
            theme, inputs_form=[self.proxy_host_line, self.proxy_port_line], parent=self, text='Proxy'
        )

        # Proxy connect
        self.button_proxy = UiToggleButton(theme, parent=self)
        self.button_proxy.stateChanged.connect(self.proxy_start_stop)

        self.button_connect = UiPushButton(
            theme,
            text="Connect",
            icon_path="signal-stream.svg",
            margin=0,
            icon_size=18,
            height=25,
            width=50
        )
        self.button_connect.clicked.connect(self.connect_proxy)

        self.proxy_on_input = FormInput(
            theme, inputs_form=[self.button_proxy, self.button_connect], parent=self, text='Local Proxy'
        )

        # Label Disconnect
        self.label_disconnect = qt.QLabel("Proxies Connected", parent=self)
        self.label_disconnect.setAlignment(qt.Qt.AlignmentFlag.AlignCenter)
        self.label_disconnect.setStyleSheet(f"border: none; ")

        # Proxies connected
        self.proxy_hosts_combo = qt.QComboBox(self)
        self.proxy_hosts_combo.setPlaceholderText("Proxy Host")
        self.proxy_hosts_combo.setMinimumWidth(150)
        self.proxy_hosts_combo.setStyleSheet(f"background-color: {theme['colors'].get('background')}; ")

        self.button_disconnect = UiPushButton(
            theme,
            text="Disconnect",
            icon_path="signal-stream-slash.svg",
            margin=0,
            icon_size=18,
            height=25,
            width=50
        )
        self.button_disconnect.clicked.connect(self.disconnect_proxy)

        self.proxy_off_input = FormInput(
            theme, inputs_form=[self.proxy_hosts_combo, self.button_disconnect], parent=self,
        )

        self.add_layout()
        self.connector.connected.connect(self.on_proxy_connect)
        self.connector.disconnected.connect(self.on_proxy_disconnect)

    def add_layout(self):
        self.layout.addWidget(self.proxy_info_input)
        self.layout.addWidget(self.proxy_on_input)
        self.layout.addWidget(self.label_disconnect)
        self.layout.addWidget(self.proxy_off_input)

    @qt.Slot()
    def proxy_start_stop(self):
        if self.button_proxy.isChecked():
            self.proxy.start()
        else:
            self.proxy.stop()

    @qt.Slot()
    def connect_proxy(self):
        host = self.proxy_host_line.text()
        port = self.proxy_port_line.text()
        port = int(port) if port else 1

        connector = self.core.connector
        connector.connect_proxy(host, port)

        self.proxy_host_line.setText('')
        self.proxy_port_line.setText('')

    @qt.Slot()
    def disconnect_proxy(self):
        host = self.proxy_hosts_combo.currentText()

        connector = self.core.connector
        connector.disconnect_proxy(host)

    @qt.Slot(str)
    def on_proxy_connect(self, host):
        self.proxy_hosts_combo.addItem(host)

    @qt.Slot(str)
    def on_proxy_disconnect(self, host):
        index = self.proxy_hosts_combo.findText(host)

        if index >= 0:
            self.proxy_hosts_combo.removeItem(index)

        self.proxy_hosts_combo.setCurrentIndex(-1)
