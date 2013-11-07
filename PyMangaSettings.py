import sys

from PyQt5.QtCore import (QSettings)

from PyMangaSettingsDialog import *

# application tags
COMPANY = "jschmer"
APPLICATION = "PyMangaReader"

class Settings():

    # the default application settings
    settings = {
                MANGA_DIRS : [],
                MANGA_SETTINGS : "MangaData",
                UNRAR_EXE : "unrar"
               }

    # load settings from system
    qsettings = QSettings(COMPANY, APPLICATION)

    def __init__(self):
        # load configuration/settings
        config = self.qsettings.value("settings")
        if config:
            # merge settings
            self.settings = dict(list(self.settings.items()) + list(config.items()))

    def save(self):
        """ save settings into system """
        self.store("settings", self.settings)

    def refresh(self):
        """ load application settings from system """
        self.qsettings = QSettings(COMPANY, APPLICATION)

    def execDialog(self):
        """ execute dialog and apply settings if pressed OK """
        dialog = SettingsDialog(self.settings)
        if dialog.exec_():
            print("Saving settings...")
            self.settings = dialog.getSettings()

    def store(self, tag, value):
        """ store data in application settings """
        self.qsettings.setValue(tag, value);

    def load(self, tag):
        """
        load data from application settings 
        returns None if tag not available
        """
        return self.qsettings.value(tag)