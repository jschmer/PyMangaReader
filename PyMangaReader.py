import sys

from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QSettings, QSize, Qt, QTextStream)
from PyQt5.QtGui import (QIcon, QKeySequence, QImage, QPainter, QPalette, QPixmap, QTransform)
from PyQt5.QtWidgets import (QDialog, QLabel, QScrollArea, QAction, QApplication, QFileDialog, QMainWindow, QMessageBox, QTextEdit, QSizePolicy)

from ui_dialog import Ui_MainWindow
from PyMangaSettings import SettingsDialog

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

        # loading settings
        settings = QSettings("jschmer", "PyMangaReader");

        # window geometry
        geom = settings.value("geometry")
        if geom:
            self.restoreGeometry(geom)
            self.showMenu(True)
            self.showNormal()
            self.resizeEvent(None)

        # configuration/settings
        config = settings.value("settings")
        if config:
            self.settings = config

    def load(self, image_path):
        image = QImage(image_path)
        if image.isNull():
            QMessageBox.error(self, "Error", "Cannot load %s." % image_path)
        else:
            self.manga_image = QPixmap.fromImage(image)
            self.ui.manga_image_label.setPixmap(self.manga_image)

    # fit image into label
    def resizeEvent(self, event):
        self.updateHack()
        print("Label: %d x %d" % (self.ui.manga_image_label.size().width(), self.ui.manga_image_label.size().height()))
        pic = self.manga_image.scaled(self.ui.manga_image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ui.manga_image_label.setPixmap(pic)

    # save window size and position
    def closeEvent(self, event):
        settings = QSettings("jschmer", "PyMangaReader");
        settings.setValue("geometry", self.saveGeometry());
        settings.setValue("settings", self.settings);
        QMainWindow.closeEvent(self, event);

    # rotate image
    def rotate(self, deg):
        rotate = QTransform().rotate(deg)
        self.manga_image = self.manga_image.transformed(rotate);
        self.resizeEvent(None)
        
    def updateHack(self):
        # yay! hacking around! qt doesn't update the size of the qlabel after hiding the groupbox
        # so i force the update here with hiding and showing the centralwidget
        self.ui.centralwidget.hide()
        self.ui.centralwidget.show()

    def showMenu(self, activate = None):
        if activate == None:
            activate = not self.ui.groupBox.isVisible()

        if activate:
            self.ui.groupBox.show()
        else:
            self.ui.groupBox.hide()

        # update image in label
        self.resizeEvent(None)

    def keyPressEvent(self, event):
        # rotate cw
        if event.key() == Qt.Key_R:
            self.rotate(90)    
        # rotate ccw
        if event.key() == Qt.Key_E:
            self.rotate(-90)
        # go fullscreen!
        if event.key() == Qt.Key_F:
            if not self.isFullScreen():
                self.showMenu(False)
                self.showFullScreen()
            else:
                self.showMenu(True)
                self.showNormal()
        # hide menu
        elif event.key() == Qt.Key_H:
            self.showMenu()
        # ESC
        if event.key() == Qt.Key_Escape:
            self.close()

    def on_settings(self):
        # TODO: show settings dialog
        dialog = SettingsDialog(self.settings)
        if dialog.exec_():
            print("Saving settings...")
            self.settings = dialog.getSettings()

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