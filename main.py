from gui.central_widget import CentralWidget
from core import Func
import qt_core as qt
import sys


class MainWindow(qt.QMainWindow, Func):
    def __init__(self):
        super().__init__()

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
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
