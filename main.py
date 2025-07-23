import sys
import qt_core as qt
from gui.central_widget import CentralWidget
from core import Func
from core.logger import Logger


class MainWindow(qt.QMainWindow, Func):
    def __init__(self):
        super().__init__()

        self.gui = CentralWidget(self)


if __name__ == '__main__':
    app = qt.QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
