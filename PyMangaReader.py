import sys

from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QSettings, QSize, Qt, QTextStream)
from PyQt5.QtGui import (QIcon, QKeySequence, QImage, QPainter, QPalette, QPixmap, QTransform)
from PyQt5.QtWidgets import (QDialog, QLabel, QScrollArea, QAction, QApplication, QFileDialog, QMainWindow, QMessageBox, QTextEdit, QSizePolicy)

from ui_mainwindow import Ui_MainWindow
from PyMangaSettings import *

class MainWindow(QMainWindow):
    settings = Settings()
    manga_image = None

    def __init__(self, fileName=None):
        super(MainWindow, self).__init__()

        # Set up the user interface from Designer
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(APPLICATION)

        # arbitrary default size
        self.resize(800, 600)

        # init vars
        self.manga_image = QPixmap()

        # connect buttons
        self.ui.pushSettings.clicked.connect(self.on_settings)
        self.ui.pushAbout.clicked.connect(self.on_about)

        # load previous window geometry
        geom = self.settings.load("geometry")
        if geom:
            self.restoreGeometry(geom)

            # show normal window and menu by default, regardless of last stored window pos/size
            # this is here to disable fullscreen at startup
            self.showMenu(True)
            self.showNormal()
            self.resizeEvent(None)

        # debug: load image
        filename = "C:/Projects/Py/PyMangaReader/bild.jpg"
        self.load(filename)

    def load(self, image_path):
        """  load an image """
        image = QImage(image_path)
        if image.isNull():
            QMessageBox.error(self, "Error", "Cannot load %s." % image_path)
        else:
            self.manga_image = QPixmap.fromImage(image)
            self.ui.manga_image_label.setPixmap(self.manga_image)

    def resizeEvent(self, event):
        """ fit image into label """
        #print("Label: %d x %d" % (self.ui.manga_image_label.size().width(), self.ui.manga_image_label.size().height()))

        # force an geometry update for all widgets
        self.updateHack()
        
        # resize manga image (pixmap)
        pic = self.manga_image.scaled(self.ui.manga_image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # update label with scaled pixmap
        self.ui.manga_image_label.setPixmap(pic)

    def closeEvent(self, event):
        # save window size and position
        self.settings.store("geometry", self.saveGeometry());
        self.settings.save()
        QMainWindow.closeEvent(self, event);

    def rotate(self, deg):
        """ rotate image by deg """
        rotate = QTransform().rotate(deg)
        self.manga_image = self.manga_image.transformed(rotate);
        # refresh image
        self.resizeEvent(None)
        
    def updateHack(self):
        """
        yay! hacking around! qt doesn't update the size of the qlabel after hiding the groupbox
        so i force the update here with hiding and showing the centralwidget
        """
        self.ui.centralwidget.hide()
        self.ui.centralwidget.show()

    def showMenu(self, activate = None):
        """
        Show the menu, if ativate is not given, it is toggled
        """
        if activate == None:
            activate = not self.ui.groupBox.isVisible()

        if activate:
            self.ui.groupBox.show()
        else:
            self.ui.groupBox.hide()

        # update image in label
        self.resizeEvent(None)

    def toggleFullscreen(self):
        if not self.isFullScreen():
            self.showMenu(False)
            self.showFullScreen()
        else:
            self.showMenu(True)
            self.showNormal()

    def keyPressEvent(self, event):
        """
        Keyboard stuf::
        R       Rotate CW
        E       Rotate CCW
        F       Toggle Fullscreen
        H       Show/Hide Menu
        ESC     Quit application
        """
        if event.key() == Qt.Key_R:
            self.rotate(90)    
        elif event.key() == Qt.Key_E:
            self.rotate(-90)
        elif event.key() == Qt.Key_F:
            self.toggleFullscreen()
        elif event.key() == Qt.Key_H:
            self.showMenu()
        elif event.key() == Qt.Key_Escape:
            self.close()

    def on_settings(self):
        self.settings.execDialog()

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