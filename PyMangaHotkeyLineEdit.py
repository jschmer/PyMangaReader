from PyQt5.QtWidgets import (QLineEdit, QDialog)
from PyQt5.QtCore import (Qt, QEvent)
from PyQt5.QtGui import QKeySequence

from PyMangaLogger import log
from ui_hotkey import Ui_HotkeyDialog

class HotkeyLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super(HotkeyLineEdit, self).__init__(parent)

    def mousePressEvent(self, event):
        log.info("Mouse press")
        # TODO: construct a data structure to hold mouse presses that can be used as shortcuts

    def keyPressEvent(self, event):
        log.info("Key Press")
        key = event.key(); 
        key = Qt.Key(key); 

        # Handle unknown keys
        if key == Qt.Key_unknown:
            return

        # Pressing Esc or Backspace will clear the content
        if key == Qt.Key_Escape or key == Qt.Key_Backspace:
            self.setText(None)
            return
        
        # modifier keys can't stand alone
        if key in (Qt.Key_Control, Qt.Key_Alt, Qt.Key_AltGr, Qt.Key_Shift):
            return

        # Checking for key combinations
        modifiers = event.modifiers();

        if(modifiers & Qt.NoModifier):
            return
        if(modifiers & Qt.ShiftModifier):
            key += Qt.SHIFT
        if(modifiers & Qt.ControlModifier):
            key += Qt.CTRL 
        if(modifiers & Qt.AltModifier):
            key += Qt.ALT 

        self.setText(QKeySequence(key).toString(QKeySequence.NativeText))

class HotkeyDialog(QDialog):

    def __init__(self):
        super(HotkeyDialog, self).__init__()

        # Set up the user interface from Designer.
        self.ui = Ui_HotkeyDialog()
        self.ui.setupUi(self)

        self.setAttribute(Qt.WA_DeleteOnClose)

        # add hotkey edits
        self.ui.formLayout.addRow("Next Page", HotkeyLineEdit())
        self.ui.formLayout.addRow("Previous Page", HotkeyLineEdit())
        self.ui.formLayout.addRow("Toggle Fullscreen", HotkeyLineEdit())

    # TODO: save shortcuts in easy accessable container when the dialog is closed