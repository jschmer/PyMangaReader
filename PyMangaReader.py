import sys

from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QSettings, QSize, Qt, QTextStream)
from PyQt5.QtGui import (QIcon, QKeySequence, QImage, QPainter, QPalette, QPixmap, QTransform)
from PyQt5.QtWidgets import (QLabel, QScrollArea, QAction, QApplication, QFileDialog, QMainWindow, QMessageBox, QTextEdit, QSizePolicy)

from ui_dialog import Ui_MainWindow
from ui_settings import Ui_SettingsDialog

class MainWindow(QMainWindow):
    sequenceNumber = 1
    windowList = []

    def __init__(self, fileName=None):
        super(MainWindow, self).__init__()

        # Set up the user interface from Designer.
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # arbitrary default size
        self.resize(800, 600)

        # debug: load image
        filename = "C:/Projects/Py/PyMangaReader/bild.jpg"
        self.load(filename)
            
        # connect buttons
        self.ui.pushSettings.clicked.connect(self.on_settings)
        self.ui.pushAbout.clicked.connect(self.on_about)

    def load(self, image_path):
        image = QImage(image_path)
        if image.isNull():
            QMessageBox.error(self, "Error", "Cannot load %s." % image_path)
        else:
            self.manga_image = QPixmap.fromImage(image)
            self.ui.manga_image_label.setPixmap(self.manga_image)

    # fit image into label
    def resizeEvent(self, event):
        print("Label: %d x %d" % (self.ui.manga_image_label.size().width(), self.ui.manga_image_label.size().height()))
        pic = self.manga_image.scaled(self.ui.manga_image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ui.manga_image_label.setPixmap(pic)

    # rotate image
    def rotate(self, deg):
        rotate = QTransform().rotate(deg)
        self.manga_image = self.manga_image.transformed(rotate);
        self.resizeEvent(None)
        
    def keyPressEvent(self, event):
        # rotate cw
        if event.key() == Qt.Key_R:
            self.rotate(90)    
        # rotate ccw
        if event.key() == Qt.Key_E:
            self.rotate(-90)
        # hide menu
        elif event.key() == Qt.Key_H:
            if self.ui.groupBox.isVisible():
                self.ui.groupBox.hide()

                # yay! hacking around! qt doesn't update the size of the qlabel after hiding the groupbox
                # so i force the update here with hiding and showing the centralwidget
                self.ui.centralwidget.hide()
                self.ui.centralwidget.show()
            else:
                self.ui.groupBox.show()
           
            # update image in label
            self.resizeEvent(None)
        # ESC
        if event.key() == Qt.Key_Escape:
            self.close()

    def on_settings(self):
        # TODO: show settings dialog
        dialog = QDialog()
        dialog.ui = Ui_SettingsDialog()
        dialog.ui.setupUi(dialog)
        dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        dialog.exec_()

    def on_about(self):
        QMessageBox.information(self, "About PyMangaReader", "MIT License")

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        mainWin = MainWindow()
        mainWin.show()
        sys.exit(app.exec_())
    except Exception as ex:
        print(ex.message)