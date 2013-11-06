from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QSettings, QSize, Qt, QTextStream)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow, QMessageBox, QTextEdit)

from ui_dialog import Ui_MainWindow

class MainWindow(QMainWindow):
    sequenceNumber = 1
    windowList = []

    def __init__(self, fileName=None):
        super(MainWindow, self).__init__()

        # Set up the user interface from Designer.
        self.ui = Ui_MainWindow()

        try:
            self.ui.setupUi(self)
        except Exception as e:
            print(e.message)

        # create menu actions
        self.ui.pushSettings.clicked.connect(self.on_settings)
        self.ui.pushAbout.clicked.connect(self.on_about)

    def on_settings(self):
        # TODO: show settings dialog
        QMessageBox.information(self, "Title", "Settings")

    def on_about(self):
        QMessageBox.information(self, "About PyMangaReader", "MIT License")

if __name__ == '__main__':

    import sys

    try:
        app = QApplication(sys.argv)
        mainWin = MainWindow()
        mainWin.show()
        sys.exit(app.exec_())
    except Exception as ex:
        print(ex.message)