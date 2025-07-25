from core.logger import Logger
import qt_core as qt


class Commander(qt.QObject):
    connection_select = qt.Signal(str)
    connection_deselect = qt.Signal()
    connection_update = qt.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = Logger(name="commander", level="DEBUG").get_logger()
        self.selected_connection = None

    def select_conection(self, conn_id: str):
        self.selected_connection = conn_id
        self.connection_select.emit(conn_id)

    def deselect_connection(self):
        self.selected_connection = None
        self.connection_deselect.emit()
