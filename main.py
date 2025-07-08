import sys
import qt_core as qt
from gui.central_widget import CentralWidget


class MainWindow(qt.QMainWindow):
    def __init__(self):
        super().__init__()

        self.gui = CentralWidget(self)


if __name__ == '__main__':
    app = qt.QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
