import sys

from PyQt5.QtCore import (Qt)
from PyQt5.QtWidgets import (QDialog, QFileDialog)

from ui_settings import Ui_SettingsDialog

# setting tags
MANGA_DIRS = "mangadirs"
MANGA_SETTINGS = "mangasettingsdir"
UNRAR_EXE = "unrarexepath"

class SettingsDialog(QDialog):

    def __init__(self, settings):
        super(SettingsDialog, self).__init__()

        if not settings:
            raise "No Settings? Damn You!"

        self.settings = settings

        # Set up the user interface from Designer.
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)

        self.setAttribute(Qt.WA_DeleteOnClose)

        # initialitze textboxes with settings
        self.updateData()

        # connect buttons
        self.ui.pushAddMangaDir.clicked.connect(self.addMangaDir)
        self.ui.pushRemoveMangaDir.clicked.connect(self.removeMangaDir)
        self.ui.pushSelectMangaSettingsDir.clicked.connect(self.selectMangaSettingsDir)
        self.ui.pushSelectUnrarExecutable.clicked.connect(self.selectUnrarPath)

    def addMangaDir(self):
        dir = QFileDialog.getExistingDirectory(self, "Select Directory")
        if len(dir) > 0:
            self.settings[MANGA_DIRS].append(dir)
        self.updateData()

    def removeMangaDir(self):
        selitems = self.ui.listMangaDirs.selectedItems()
        # remove selected path from settings
        self.settings[MANGA_DIRS] = [ v for v in self.settings[MANGA_DIRS] if not v in [x.text() for x in selitems]]
        self.updateData()

    def selectMangaSettingsDir(self):
        dir = QFileDialog.getExistingDirectory(self, "Select Directory", self.settings[MANGA_SETTINGS])
        if len(dir) > 0:
            self.settings[MANGA_SETTINGS] = dir
        self.updateData()

    def selectUnrarPath(self):
        file = QFileDialog.getOpenFileName(self, "Select Unrar executable", self.settings[UNRAR_EXE])
        if len(file[0]) > 0:
            self.settings[UNRAR_EXE] = file[0]
        self.updateData()

    def updateData(self):
        self.ui.listMangaDirs.clear()
        for dir in self.settings[MANGA_DIRS]:
            self.ui.listMangaDirs.addItem(dir)

        self.ui.labelMangaSettings.setText(self.settings[MANGA_SETTINGS])
        self.ui.labelUnrarExe.setText(self.settings[UNRAR_EXE])

    def getSettings(self):
        return self.settings
