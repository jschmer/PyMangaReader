import sys

from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QSettings, QSize, Qt, QTextStream)
from PyQt5.QtGui import (QIcon, QKeySequence, QImage, QPainter, QPalette, QPixmap, QTransform)
from PyQt5.QtWidgets import (QDialog, QLabel, QScrollArea, QAction, QApplication, QFileDialog, QMainWindow, QMessageBox, QTextEdit, QSizePolicy)

from ui_settings import Ui_SettingsDialog

class SettingsDialog(QDialog):

    def __init__(self, settings = None):
        super(SettingsDialog, self).__init__()

        # Set up the user interface from Designer.
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)

        self.setAttribute(Qt.WA_DeleteOnClose)

        self.settings = dict(settings)

        # insert default settings
        if not "mangadirs" in settings:
            self.settings["mangadirs"] = []
        if not "mangasettingsdir" in settings:
            self.settings["mangasettingsdir"] = "mangadata"
        if not "unrarexepath" in settings:
            self.settings["unrarexepath"] = "unrar"

        # initialitze textboxes with settings
        self.updateData()

        # connect buttons
        self.ui.pushAddMangaDir.clicked.connect(self.addMangaDir)
        self.ui.pushRemoveMangaDir.clicked.connect(self.removeMangaDir)
        self.ui.pushSelectMangaSettingsDir.clicked.connect(self.selectMangaSettingsDir)
        self.ui.pushSelectUnrarExecutable.clicked.connect(self.selectUnrarPath)

    def addMangaDir(self):
        dir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if len(dir) > 0:
            self.settings["mangadirs"].append(dir)
        self.updateData()

    def removeMangaDir(self):
        selitems = self.ui.listMangaDirs.selectedItems()
        self.settings["mangadirs"] = [ v for v in self.settings["mangadirs"] if not v in [x.text() for x in selitems]]
        self.updateData()

    def selectMangaSettingsDir(self):
        dir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if len(dir) > 0:
            self.settings["mangasettingsdir"] = dir
        self.updateData()

    def selectUnrarPath(self):
        file = QFileDialog.getOpenFileName(self, "Select Unrar executable")
        if len(file[0]) > 0:
            self.settings["unrarexepath"] = file[0]
        self.updateData()

    def updateData(self):
        self.ui.listMangaDirs.clear()
        for dir in self.settings["mangadirs"]:
            self.ui.listMangaDirs.addItem(dir)

        self.ui.labelMangaSettings.setText(self.settings["mangasettingsdir"])
        self.ui.labelUnrarExe.setText(self.settings["unrarexepath"])

    def getSettings(self):
        return self.settings

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        mainWin = MainWindow()
        mainWin.show()
        sys.exit(app.exec_())
    except Exception as ex:
        print(ex.message)