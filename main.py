from gui.central_widget import CentralWidget
from core import Func
import qt_core as qt
import sys


class MainWindow(qt.QMainWindow):
    def __init__(self, core: Func):
        super().__init__()

        self.logger = core.logger
        self.proxy = core.proxy
        self.connector = core.connector
        self.commander = core.commander
        self.gui = CentralWidget(self)

    def closeEvent(self, event):
        stoped = self.proxy.stop()
        if stoped:
            self.logger.info("Closing window")
            event.accept()
        else:
            self.logger.critical("Failed to close window")
            event.ignore()


if __name__ == '__main__':
    app = qt.QApplication(sys.argv)
    func = Func()
    window = MainWindow(func)
    window.show()

    sys.exit(app.exec())
