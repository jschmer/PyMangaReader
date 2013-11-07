import sys
import os

from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QSettings, QSize, Qt, QTextStream)
from PyQt5.QtGui import (QIcon, QKeySequence, QImage, QPainter, QPalette, QPixmap, QTransform)
from PyQt5.QtWidgets import (QDialog, QComboBox, QLabel, QScrollArea, QAction, QApplication, QFileDialog, QMainWindow, QMessageBox, QTextEdit, QSizePolicy)

from ui_mainwindow import Ui_MainWindow
from PyMangaSettings import *

class MainWindow(QMainWindow):
    settings = Settings()
    manga_image = None

    manga_books = {}
    manga_vols = {}
    manga_chaps = {}
    manga_pages = {}

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

        self.loadMangaBooks()

        # connect buttons
        self.ui.pushSettings.clicked.connect(self.on_settings)
        self.ui.pushAbout.clicked.connect(self.on_about)
        self.ui.list_manga.currentIndexChanged.connect(self.loadVolumeFiles)
        self.ui.list_volume.currentIndexChanged.connect(self.loadChapterFiles)
        self.ui.list_chapter.currentIndexChanged.connect(self.loadPageFiles)
        self.ui.list_page.currentIndexChanged.connect(self.onPageIdxChanged)

        # select last viewed manga
        last_manga = self.settings.load("last_manga")
        if last_manga:
            # select it!
            idx = self.ui.list_manga.findText(last_manga)
            self.ui.list_manga.setCurrentIndex(idx)

        # debug: load image
        filename = "C:/Projects/Py/PyMangaReader/bild.jpg"
        self.loadImage(filename)

        # load previous window geometry
        geom = self.settings.load("geometry")
        if geom:
            self.restoreGeometry(geom)

            # show normal window and menu by default, regardless of last stored window pos/size
            # this is here to disable fullscreen at startup
            self.showMenu(True)
            self.showNormal()
            self.resizeEvent(None)

    def saveCurrentMangaSettings(self):
        pass

    def selectedManga(self):
        manga = self.ui.list_manga.currentText()
        return manga

    def selectedVolume(self):
        vol = self.ui.list_volume.currentText()
        return vol

    def selectedChapter(self):
        chap = self.ui.list_chapter.currentText()
        return chap

    def selectedPage(self):
        page = self.ui.list_page.currentText()
        return page

    def loadVolumeFiles(self):
        # current manga book
        selected = self.selectedManga()
        if selected in self.manga_books:
            manga_path = self.manga_books[selected]
            print("Loading volume data from", manga_path)

            # for current manga: search for volumes: directories and archives (zip, rar)
            vols = [(x, os.path.join(manga_path, x)) for x in os.listdir(manga_path)]
            vols = [x for x in vols if os.path.isdir(x[1])] # throw out anyting other than directories

            self.manga_vols = dict(vols)
            # add to gui
            self.ui.list_volume.clear()
            self.ui.list_volume.addItems(sorted([key for key, value in self.manga_vols.items()]))

    def loadChapterFiles(self):
        selected = self.selectedVolume()
        if selected in self.manga_vols:
            chap_path = self.manga_vols[selected]
            print("Loading chapter data from", chap_path)

            # for current volume: search for chapters: directories and archives (zip, rar)
            chaps = [(x, os.path.join(chap_path, x)) for x in os.listdir(chap_path)]
            chaps = [x for x in chaps if os.path.isdir(x[1])] # throw out anyting other than directories

            self.manga_chaps = dict(chaps)
            # add to gui
            self.ui.list_chapter.clear()
            self.ui.list_chapter.addItems(sorted([key for key, value in self.manga_chaps.items()]))

    def loadPageFiles(self):
        selected = self.selectedChapter()
        if selected in self.manga_chaps:
            page_path = self.manga_chaps[selected]
            print("Loading page data from", page_path)

            # for current volume: search for chapters: directories and archives (zip, rar)
            pages = [(x, os.path.join(page_path, x)) for x in os.listdir(page_path)]
            pages = [x for x in pages if os.path.isfile(x[1])] # throw out anyting other than directories

            self.manga_pages = dict(pages)
            # add to gui
            self.ui.list_page.clear()
            self.ui.list_page.addItems(sorted([key for key, value in self.manga_pages.items()]))

    def loadMangaBooks(self):
        # scan each configured directory for top-level mangas
        manga_list = []
        for path in self.settings.settings[MANGA_DIRS]:
            p = os.path.abspath(path)
            mangas = os.listdir(p)

            # save as (name, path) pairs
            list = [(x, os.path.join(path, x)) for x in mangas]
            manga_list += list
        self.manga_books = dict(manga_list)

        self.ui.list_manga.addItems(sorted([key for key, value in self.manga_books.items()]))

    def onPageIdxChanged(self, idx = None):
        """
        load an image
        idx is the selected index of the list_page combobox
        """
        if idx == -1:
            self.manga_image.clear()
            return

        image_path = self.manga_pages[self.selectedPage()]
        self.loadImage(image_path)

    def loadImage(self, image_path):
        """ load an image """
        image = QImage(image_path)
        if image.isNull():
            QMessageBox.warning(self, "Error", "Cannot load %s." % image_path)
        else:
            self.manga_image = QPixmap.fromImage(image)
            self.ui.manga_image_label.setPixmap(self.manga_image)
            self.resizeEvent(None)

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
        
        # save last selected manga
        self.settings.store("last_manga", self.selectedManga())

        # save last vol/chap/page in manga settings
        self.saveCurrentMangaSettings()

        # save general settings
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
        print(ex)