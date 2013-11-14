import sys
import os

from PyQt5.QtCore import (QSettings)
from PyQt5.QtGui import (QGuiApplication)

from PyMangaSettingsDialog import *

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

        # load manga specific settings from MANGA_SETTINGS_PATH as ini file
        self.mangasettings = QSettings(self.settings[MANGA_SETTINGS_PATH], QSettings.IniFormat)

    def save(self):
        """ save application settings into system """
        self.store("settings", self.settings)

    def execDialog(self):
        """ execute dialog and apply settings if pressed OK """
        dialog = SettingsDialog(self.settings)
        if dialog.exec_():
            print("Saving settings...")
            self.settings = dialog.settings
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