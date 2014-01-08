import sys
import os

from shutil import move, copy

from PyQt5.QtCore import (QSettings)
from PyQt5.QtGui import (QGuiApplication, QKeySequence)
from PyQt5.QtWidgets import (QShortcut)

from PyMangaSettingsDialog import *
from PyMangaLogger import log
from PyMangaLayer import *

# application tags
COMPANY = "jschmer"
APPLICATION = "PyMangaReader"

class Settings():
    """ Settings class for storing and retrieving settings """
    # the default application settings
    settings = {
                MANGA_DIRS : [],
                MANGA_SETTINGS_PATH : os.path.dirname(os.path.realpath(__file__)) + "/manga_settings.ini",
                UNRAR_EXE : "unrar"
               }

    # the QSettings objects
    appsettings = None
    mangasettings = None

    # shortcuts/hotkeys
    shortcuts = None

    parent = None

    def __init__(self, parent):
        self.parent = parent

        # load application settings (fixed location)
        self.appsettings = QSettings(COMPANY, APPLICATION)
        config = self.appsettings.value("settings")
        if config:
            # merge settings
            self.settings = dict(list(self.settings.items()) + list(config.items()))

        self.setupDefaultShortcuts()
        shortcuts = self.appsettings.value("shortcuts")
        if shortcuts:
            # unserialize keysequences and assign them to their corresponding shortcuts!
            for key, value in shortcuts.items():
                keysequence = QKeySequence.fromString(value, QKeySequence.NativeText)

                # skip shortcuts that don't exist
                if key not in self.shortcuts: continue

                self.shortcuts[key].setKey(keysequence)

        self.refreshMangaSettings()

    def setupDefaultShortcuts(self):
        self.shortcuts = {}
        self.shortcuts["Rotate CW"] = QShortcut(QKeySequence("R"), self.parent)
        self.shortcuts["Rotate CCW"] = QShortcut(QKeySequence("E"), self.parent)
        self.shortcuts["Next Page"] = QShortcut(QKeySequence(Qt.Key_Right), self.parent)
        self.shortcuts["Previous Page"] = QShortcut(QKeySequence(Qt.Key_Left), self.parent)
        self.shortcuts["Quit"] = QShortcut(QKeySequence(Qt.Key_Escape), self.parent)
        self.shortcuts["Toggle Fullscreen"] = QShortcut(QKeySequence(Qt.Key_F), self.parent)
        self.shortcuts["Show/Hide Menu"] = QShortcut(QKeySequence(Qt.Key_H), self.parent)

    def refreshMangaSettings(self):
        # load manga specific settings from MANGA_SETTINGS_PATH as ini file
        self.mangasettings = QSettings(self.settings[MANGA_SETTINGS_PATH], QSettings.IniFormat)
        setupUnrar(self.settings[UNRAR_EXE])

    def save(self):
        """ save application settings into system """
        self.store("settings", self.settings)

        # serialize shortcuts
        shorts = {}
        for key, shortcut in self.shortcuts.items():
          shorts[key] = shortcut.key().toString(QKeySequence.NativeText)
        self.store("shortcuts", shorts)

    def execDialog(self):
        """ execute dialog and apply settings if pressed OK """
        dialog = SettingsDialog(self.settings.copy(), self.shortcuts)
        if dialog.exec_():
            log.info("Saving settings...")
            oldpath = self.settings[MANGA_SETTINGS_PATH]
            newpath = dialog.settings[MANGA_SETTINGS_PATH]

            # copy old file to new location if newpath doesn't exist
            if oldpath != newpath and not os.path.exists(newpath):
                copy(oldpath, newpath)

            self.settings = dialog.settings
            self.refreshMangaSettings()

            return True
        return False

    def store(self, tag, value):
        """ store data in application settings """
        self.appsettings.setValue(tag, value);

    def load(self, tag):
        """
        load data from application settings 
        returns None if tag not available
        """
        return self.appsettings.value(tag)

    def storeMangaSetting(self, manga, value):
        self.mangasettings.setValue(manga, value)

    def loadMangaSettings(self, manga):
        return self.mangasettings.value(manga)