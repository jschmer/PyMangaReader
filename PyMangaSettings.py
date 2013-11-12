import sys

from PyQt5.QtCore import (QSettings, QCoreApplication)

from PyMangaSettingsDialog import *

# application tags
COMPANY = "jschmer"
APPLICATION = "PyMangaReader"

MANGASETTINGSFILE = "C:/Projects/Py/PyMangaReader/manga_settings.ini";

class Settings():

    # the default application settings
    settings = {
                MANGA_DIRS : [],
                MANGA_SETTINGS : "MangaData",
                UNRAR_EXE : "unrar"
               }

    # load settings from system
    appsettings = QSettings(COMPANY, APPLICATION)
    mangasettings = QSettings(MANGASETTINGSFILE, QSettings.IniFormat)

    def __init__(self):
        # load configuration/settings
        config = self.appsettings.value("settings")
        if config:
            # merge settings
            self.settings = dict(list(self.settings.items()) + list(config.items()))

    def save(self):
        """ save settings into system """
        self.store("settings", self.settings)

    def execDialog(self):
        """ execute dialog and apply settings if pressed OK """
        dialog = SettingsDialog(self.settings)
        if dialog.exec_():
            print("Saving settings...")
            self.settings = dialog.getSettings()

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