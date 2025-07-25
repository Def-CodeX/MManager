from core import Func
import qt_core as qt
from gui.widgets.ui_push_button import UiPushButton


class HomePage(qt.QWidget):
    class Form(qt.QFrame):
        def __init__(self, theme, parent):
            super().__init__(parent)

            self.layout_form = qt.QHBoxLayout(self)
            self.layout_form.setContentsMargins(0, 0, 0, 0)
            self.layout_form.setSpacing(0)

            self.host_input = qt.QComboBox(parent)
            self.host_input.setPlaceholderText("Proxy Host")
            self.host_input.setMinimumWidth(300)

            self.port_input = qt.QLineEdit(parent)
            self.port_input.setPlaceholderText("Port to Bind")
            self.port_input.setMaximumWidth(200)
            self.port_input.setValidator(qt.QIntValidator(1, 65535))

            # self.button_add = qt.QPushButton("Add", parent=parent)
            self.button_add = UiPushButton(
                theme,
                self,
                text="Add",
                icon_path="sitemap.svg",
                margin=0,
                gap=10,
                icon_size=18,
                height=25,
                width=50
            )
            self.button_add.setMaximumWidth(120)

            self.button_sync = UiPushButton(
                theme,
                self,
                text="Sync",
                icon_path="refresh.svg",
                margin=0,
                icon_size=18,
                height=25,
                width=50
            )
            self.button_sync.setMaximumWidth(120)

            self.layout_form.addWidget(self.host_input)
            self.layout_form.addWidget(self.port_input)
            self.layout_form.addWidget(self.button_add)
            self.layout_form.addWidget(self.button_sync)

    class Table(qt.QTableWidget):
        def __init__(self, theme, parent):
            super().__init__(0, 5, parent=parent)
            self.theme = theme

            self.setHorizontalHeaderLabels(["ID", "Host", "Port", "Status", "Action"])
            self.horizontalHeader().setMinimumSectionSize(150)
            self.horizontalHeader().setStretchLastSection(True)
            self.setColumnWidth(3, 220)
            self.setEditTriggers(qt.QAbstractItemView.EditTrigger.NoEditTriggers)

        def add_row(self, id_, host, port, status, remove_callback, select_callback):
            for row in range(self.rowCount()):
                if self.item(row, 0) and self.item(row, 0).text() == id_:
                    return

            row = self.rowCount()
            self.insertRow(row)

            self.setItem(row, 0, qt.QTableWidgetItem(str(id_)))
            self.setItem(row, 1, qt.QTableWidgetItem(host))
            self.setItem(row, 2, qt.QTableWidgetItem(str(port)))
            self.setItem(row, 3, qt.QTableWidgetItem(status))

            # Action column
            action_container = qt.QFrame()
            layout = qt.QHBoxLayout(action_container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(10)

            btn_remove = UiPushButton(
                self.theme,
                self,
                text="Remove",
                icon_path="cross-circle.svg",
                margin=0,
                icon_size=18,
                height=25,
                width=50
            )
            btn_remove.clicked.connect(lambda: remove_callback(host, id_))

            btn_select = UiPushButton(
                self.theme,
                self,
                text="Select",
                icon_path="internet-security.svg",
                margin=0,
                icon_size=18,
                height=25,
                width=50
            )
            btn_select.clicked.connect(lambda: select_callback(id_))

            layout.addWidget(btn_remove)
            layout.addWidget(btn_select)
            self.setCellWidget(row, 4, action_container)

        def remove_row(self, column, value):
            for row in reversed(range(self.rowCount())):
                column_item = self.item(row, column)
                if column_item and column_item.text() == value:
                    self.removeRow(row)

        def update_row(self, id_, column, new_value):
            for row in range(self.rowCount()):
                id_item = self.item(row, 0)
                if id_item and id_item.text() == id_:
                    self.setItem(row, column, qt.QTableWidgetItem(new_value))
                    break

    def __init__(self, theme, parent=None):
        super().__init__(parent)
        if not self.objectName():
            self.setObjectName("HomePage")

        # noinspection PyTypeChecker
        self.core: Func = self.window()
        self.connector = self.core.connector
        self.commander = self.core.commander

        self.layout = qt.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.label = qt.QLabel("Home")
        self.label.setAlignment(qt.Qt.AlignmentFlag.AlignCenter)

        self.frame_form = self.Form(theme, self)
        self.table_connections = self.Table(theme, self)

        self.frame_form.button_add.clicked.connect(self.add_connection)
        self.frame_form.button_sync.clicked.connect(self.sync_connections)

        self.connector.connected.connect(self.on_proxy_connected)
        self.connector.disconnected.connect(self.on_proxy_disconnected)

        self.connector.connection_list.connect(self.on_connection_list)
        self.connector.port_added.connect(self.on_port_added)
        self.connector.port_removed.connect(self.on_port_removed)
        self.connector.target_connected.connect(self.on_target_connected)
        self.connector.target_disconnected.connect(self.on_target_disconnected)

        self.add_layout()

    def add_layout(self):
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.frame_form)
        self.layout.addWidget(self.table_connections)

    @qt.Slot()
    def add_connection(self):
        host = self.frame_form.host_input.currentText().strip()
        port_text = self.frame_form.port_input.text().strip()

        if not host or not port_text.isdigit():
            return

        port = int(port_text)
        self.connector.send_add_port(host, port)

        self.frame_form.host_input.setCurrentIndex(-1)
        self.frame_form.port_input.clear()

    @qt.Slot(str)
    def select_connection(self, conn_id: str):
        self.commander.select_conection(conn_id)

    @qt.Slot(str, str)
    def remove_connection(self, host, conn_id: str):
        self.connector.send_remove_port(host, conn_id)

    @qt.Slot()
    def sync_connections(self):
        host = self.frame_form.host_input.currentText()
        to_delete = [conn_id for conn_id, meta in self.connector.connections.items() if meta["host"] == host]

        for conn_id in to_delete:
            del self.connector.connections[conn_id]

        self.table_connections.remove_row(1, host)
        self.connector.send_list(host)

        self.frame_form.host_input.setCurrentIndex(-1)

    @qt.Slot(str)
    def on_proxy_connected(self, host: str):
        self.frame_form.host_input.addItem(host)

    @qt.Slot(str)
    def on_proxy_disconnected(self, host: str):
        index = self.frame_form.host_input.findText(host)

        if index >= 0:
            self.frame_form.host_input.removeItem(index)

    @qt.Slot(str, str, int, str)
    def on_port_added(self, conn_id: str, host: str, port: int, status: str):
        self.connector.connections[conn_id] = {
            "host": host,
            "port": port,
            "status": status,
            "target": "",
        }
        self.table_connections.add_row(conn_id, host, port, status, self.remove_connection, self.select_connection)

    @qt.Slot(str, str, int, str, str)
    def on_connection_list(self, conn_id: str, host: str, port: int, status: str, target: str):
        self.connector.connections[conn_id] = {
            "host": host,
            "port": port,
            "status": status,
            "target": target.replace('(', '').replace(')', ''),
        }
        new_status = f"{status} {target}".replace("()", "")
        self.table_connections.add_row(conn_id, host, port, new_status, self.remove_connection, self.select_connection)

    @qt.Slot(str)
    def on_port_removed(self, conn_id: str):
        if conn_id in self.connector.connections:
            del self.connector.connections[conn_id]
        self.table_connections.remove_row(0, conn_id)

    @qt.Slot(str, str, str)
    def on_target_connected(self, conn_id: str, ip: str, status: str):
        new_status = f"{status} ({ip})"
        if conn_id in self.connector.connections:
            self.connector.connections[conn_id]["status"] = status
            self.connector.connections[conn_id]["target"] = ip
            self.table_connections.update_row(conn_id, 3, new_status)
            self.commander.connection_update.emit(conn_id)

    @qt.Slot(str, str)
    def on_target_disconnected(self, conn_id: str, status: str):
        self.connector.connections[conn_id]["status"] = status
        self.connector.connections[conn_id]["target"] = ""
        self.table_connections.update_row(conn_id, 3, status)
        self.commander.connection_update.emit(conn_id)
