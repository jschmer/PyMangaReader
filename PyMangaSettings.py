import sys
import os

from PyQt5.QtCore import (QSettings)
from PyQt5.QtGui import (QGuiApplication)

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

    def __init__(self):
        # load application settings (fixed location)
        self.appsettings = QSettings(COMPANY, APPLICATION)
        config = self.appsettings.value("settings")
        if config:
            # merge settings
            self.settings = dict(list(self.settings.items()) + list(config.items()))

        self.refreshMangaSettings()

    def refreshMangaSettings(self):
        # load manga specific settings from MANGA_SETTINGS_PATH as ini file
        self.mangasettings = QSettings(self.settings[MANGA_SETTINGS_PATH], QSettings.IniFormat)
        setupUnrar(self.settings[UNRAR_EXE])

    def save(self):
        """ save application settings into system """
        self.store("settings", self.settings)

    def execDialog(self):
        """ execute dialog and apply settings if pressed OK """
        dialog = SettingsDialog(self.settings.copy())
        if dialog.exec_():
            log.info("Saving settings...")
            oldpath = self.settings[MANGA_SETTINGS_PATH]
            newpath = dialog.settings[MANGA_SETTINGS_PATH]

            # check if we have a new path
            if oldpath != newpath:
                # move old file to new location
                move(oldpath, newpath)

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