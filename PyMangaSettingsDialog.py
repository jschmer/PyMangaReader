import sys
import os

from PyQt5.QtCore import (Qt)
from PyQt5.QtWidgets import (QDialog, QFileDialog)

from PyMangaLayer import *
from ui_settings import Ui_SettingsDialog
from PyMangaHotkeySettings import HotkeyDialog

# setting tags
MANGA_DIRS = "mangadirs"
MANGA_SETTINGS_PATH = "mangasettingspath"
UNRAR_EXE = "unrarexepath"

class SettingsDialog(QDialog):

    settings = None

    def __init__(self, settings, shortcuts):
        super(SettingsDialog, self).__init__()

        if not settings:
            raise "No Settings? Damn You!"

        self.settings = settings
        self.shortcuts = shortcuts

        # Set up the user interface from Designer.
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)

        self.setAttribute(Qt.WA_DeleteOnClose)

        # initialitze textboxes with settings
        self.updateData()

        # connect buttons
        self.ui.pushAddMangaDir.clicked.connect(self.addMangaDir)
        self.ui.pushRemoveMangaDir.clicked.connect(self.removeMangaDir)
        self.ui.pushSelectMangaSettingsDir.clicked.connect(self.selectMangaSettingsPath)
        self.ui.pushSelectUnrarExecutable.clicked.connect(self.selectUnrarPath)
        self.ui.button_hotkey.clicked.connect(self.execHotkey)

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

    def selectMangaSettingsPath(self):
        file = QFileDialog.getSaveFileName(self, "Select Manga Settings File", self.settings[MANGA_SETTINGS_PATH])
        if len(file[0]) > 0:
            self.settings[MANGA_SETTINGS_PATH] = file[0]
        self.updateData()

    def selectUnrarPath(self):
        exe = ""
        if os.name == "nt":
            exe = "UnRAR (UnRAR.exe)"

        file = QFileDialog.getOpenFileName(self, "Select Unrar executable", self.settings[UNRAR_EXE], exe)
        if len(file[0]) > 0:
            self.settings[UNRAR_EXE] = file[0]
            setupUnrar(self.settings[UNRAR_EXE])
        self.updateData()


    def updateData(self):
        self.ui.listMangaDirs.clear()
        for dir in self.settings[MANGA_DIRS]:
            self.ui.listMangaDirs.addItem(dir)

        self.ui.labelMangaSettings.setText(self.settings[MANGA_SETTINGS_PATH])
        self.ui.labelUnrarExe.setText(self.settings[UNRAR_EXE])

    def execHotkey(self):
        dialog = HotkeyDialog(self.shortcuts)
        dialog.exec_()