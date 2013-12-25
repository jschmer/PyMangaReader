from PyQt5.QtWidgets import (QLineEdit, QDialog, QFormLayout)
from PyQt5.QtCore import (Qt, QEvent)
from PyQt5.QtGui import QKeySequence

from PyMangaLogger import log
from ui_hotkey import Ui_HotkeyDialog

class HotkeyLineEdit(QLineEdit):
    key_sequence = None

    def __init__(self, parent=None):
        super(HotkeyLineEdit, self).__init__(parent)
        self.clearKeySequence()

    def clearKeySequence(self):
        self.key_sequence = QKeySequence()
        self.updateText()

    def setKeySequence(self, keyseq):
        if not isinstance(keyseq, QKeySequence): raise RuntimeError
        self.key_sequence = keyseq
        self.updateText()

    def updateText(self):
        self.setText(self.key_sequence.toString(QKeySequence.NativeText))

    def mousePressEvent(self, event):
        log.info("Mouse press")
        # TODO: construct a data structure to hold mouse presses that can be used as shortcuts

    def keyPressEvent(self, event):
        log.info("Key Press")
        key = event.key(); 
        key = Qt.Key(key); 

        # Ignore unknown keys
        # and if modifier keys come alone
        if key == Qt.Key_unknown or key in (Qt.Key_Control, Qt.Key_Alt, Qt.Key_AltGr, Qt.Key_Shift):
            return

        # Pressing Backspace will clear the content
        if key == Qt.Key_Backspace:
            self.setText(None)
            self.clearKeySequence()
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

        self.setKeySequence(QKeySequence(key))

class HotkeyDialog(QDialog):
    shortcuts = None

    def __init__(self, shortcuts):
        super(HotkeyDialog, self).__init__()

        # shortcuts is a reference to the real shortcuts dict so modify it only if the user presses ok!
        self.shortcuts = shortcuts

        # Set up the user interface from Designer.
        self.ui = Ui_HotkeyDialog()
        self.ui.setupUi(self)

        self.setAttribute(Qt.WA_DeleteOnClose)

        # add hotkey edits
        for key in sorted(shortcuts.keys()):
            shortcut = self.shortcuts[key]
            edit = HotkeyLineEdit()
            edit.setKeySequence(shortcut.key())
            self.ui.formLayout.addRow(key, edit)

        # save if the user accepts the dialog (presses ok)
        self.accepted.connect(self.save)

    # save shortcuts in container when the dialog is closed
    def save(self):
      log.info("Saving Hotkey stuff in Hotkeydialog")
      
      for i in range(0, self.ui.formLayout.rowCount()):
        key  = self.ui.formLayout.itemAt(i, QFormLayout.LabelRole).widget().text()
        edit = self.ui.formLayout.itemAt(i, QFormLayout.FieldRole).widget()

        if key not in self.shortcuts: raise RuntimeError
        self.shortcuts[key].setKey(edit.key_sequence)