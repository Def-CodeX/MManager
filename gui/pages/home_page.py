from core import Func
import qt_core as qt


class HomePage(qt.QWidget):
    class Form(qt.QFrame):
        def __init__(self, parent):
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

            self.button_add = qt.QPushButton("Add", parent=parent)
            self.button_add.setMaximumWidth(100)

            self.layout_form.addWidget(self.host_input)
            self.layout_form.addWidget(self.port_input)
            self.layout_form.addWidget(self.button_add)

    class Table(qt.QTableWidget):
        def __init__(self, parent):
            super().__init__(0, 5, parent=parent)

            self.setHorizontalHeaderLabels(["ID", "Host", "Port", "Status", "Action"])
            self.horizontalHeader().setMinimumSectionSize(150)
            self.horizontalHeader().setStretchLastSection(True)
            self.setEditTriggers(qt.QAbstractItemView.EditTrigger.NoEditTriggers)

        def add_row(self, id_, host, port, status, remove_callback):
            row = self.rowCount()
            self.insertRow(row)

            self.setItem(row, 0, qt.QTableWidgetItem(str(id_)))
            self.setItem(row, 1, qt.QTableWidgetItem(host))
            self.setItem(row, 2, qt.QTableWidgetItem(str(port)))
            self.setItem(row, 3, qt.QTableWidgetItem(status))

            btn = qt.QPushButton("🗑️ Remove", parent=self)
            btn.clicked.connect(lambda: remove_callback(host, id_))
            self.setCellWidget(row, 4, btn)

        def remove_row(self, id_):
            for row in range(self.rowCount()):
                id_item = self.item(row, 0)
                if id_item and id_item.text() == id_:
                    self.removeRow(row)
                    break

        def update_status(self, id_, new_status):
            for row in range(self.rowCount()):
                id_item = self.item(row, 0)
                if id_item and id_item.text() == id_:
                    self.setItem(row, 3, qt.QTableWidgetItem(new_status))
                    break

    def __init__(self, parent=None):
        super().__init__(parent)
        if not self.objectName():
            self.setObjectName("HomePage")

        self.connections: dict = {}

        # noinspection PyTypeChecker
        self.core: Func = self.window()
        self.connector = self.core.connector

        self.layout = qt.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.label = qt.QLabel("Home")
        self.label.setAlignment(qt.Qt.AlignmentFlag.AlignCenter)

        self.frame_form = self.Form(self)
        self.table_connections = self.Table(self)

        self.frame_form.button_add.clicked.connect(self.add_connection)

        self.connector.connected.connect(self.on_proxy_connected)
        self.connector.disconnected.connect(self.on_proxy_disconnected)
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

    @qt.Slot(str, str)
    def remove_connection(self, host, conn_id: str):
        self.connector.send_remove_port(host, conn_id)

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
        self.connections[conn_id] = {
            "host": host,
            "port": port,
            "status": status
        }
        self.table_connections.add_row(conn_id, host, port, status, self.remove_connection)

    @qt.Slot(str)
    def on_port_removed(self, conn_id: str):
        if conn_id in self.connections:
            del self.connections[conn_id]
        self.table_connections.remove_row(conn_id)

    @qt.Slot(str, str, str)
    def on_target_connected(self, conn_id: str, ip: str, status: str):
        if conn_id in self.connections:
            self.connections[conn_id]["status"] = status
            self.table_connections.update_status(conn_id, status)

    @qt.Slot(str, str)
    def on_target_disconnected(self, conn_id: str, status: str):
        self.connections[conn_id]["status"] = status
        self.table_connections.update_status(conn_id, status)

