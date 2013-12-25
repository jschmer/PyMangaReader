from PyQt5.QtWidgets import (QLineEdit, QDialog)
from PyQt5.QtCore import (Qt, QEvent)
from PyQt5.QtGui import QKeySequence

from ui_hotkey import Ui_HotkeyDialog

class HotkeyLineEdit(QLineEdit):
    def __init__(self, parent):
        super(HotkeyLineEdit, self).__init__(parent)

    def keyPressEvent(self, event):
        key = event.key(); 
        key = Qt.Key(key); 

        # Handle unknown keys
        if key == Qt.Key_unknown:
            return

        # Pressing Esc or Backspace will clear the content
        if key == Qt.Key_Escape or key == Qt.Key_Backspace:
            self.setText(None)
            return
        
        # Empty means a special key like F5, Delete, Home etc
        if len(event.text()) == 0:
            return

        # Checking for key combinations
        modifiers = event.modifiers();

        if(modifiers & Qt.NoModifier):
            return
        if(modifiers & Qt.ShiftModifier):
            key += Qt.SHIFT; 
        if(modifiers & Qt.ControlModifier):
            key += Qt.CTRL; 
        if(modifiers & Qt.AltModifier):
            key += Qt.ALT; 

        self.setText( QKeySequence(key).toString(QKeySequence.NativeText) )

class HotkeyDialog(QDialog):

    def __init__(self):
        super(HotkeyDialog, self).__init__()

        # Set up the user interface from Designer.
        self.ui = Ui_HotkeyDialog()
        self.ui.setupUi(self)

        self.setAttribute(Qt.WA_DeleteOnClose)

        # connect buttons
        self.ui.edit_hotkey = HotkeyLineEdit(self)