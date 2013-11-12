import sys
import os

from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QSettings, QSize, Qt, QTextStream)
from PyQt5.QtGui import (QIcon, QKeySequence, QImage, QPainter, QPalette, QPixmap, QTransform)
from PyQt5.QtWidgets import (QToolTip, QDialog, QComboBox, QLabel, QScrollArea, QAction, QApplication, QFileDialog, QMainWindow, QMessageBox, QTextEdit, QSizePolicy)

from ui_mainwindow import Ui_MainWindow
from PyMangaSettings import *
from PyMangaLayer import *

supported_archives = [".zip"]
def isSupportedArchive(file):
        if os.path.isdir(file):
            return True
        else:
            for arch in supported_archives:
                if arch not in file:
                    return False
            return True

class NoElementsError(BaseException): pass

class MainWindow(QMainWindow):
    settings = Settings()
    manga_image = None

    manga_books = {}
    manga_vols = {}
    manga_chaps = {}
    manga_pages = {}

    def __init__(self, fileName=None):
        super(MainWindow, self).__init__()

        super(MainWindow, self).setFocusPolicy(Qt.StrongFocus)

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
        self.ui.list_page.currentIndexChanged.connect(self.loadPage)

        # select last viewed manga
        last_manga = self.settings.load("last_manga")
        if last_manga:
            # select it!
            idx = self.ui.list_manga.findText(last_manga)
            self.ui.list_manga.setCurrentIndex(idx)

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

    def selectedVolumeIdx(self):
        vol = self.ui.list_volume.currentIndex()
        return vol

    def selectedVolume(self):
        vol = self.ui.list_volume.currentText()
        return vol

    def selectedChapterIndex(self):
        chap = self.ui.list_chapter.currentIndex()
        return chap

    def selectedChapter(self):
        chap = self.ui.list_chapter.currentText()
        return chap

    def selectedPageIndex(self):
        page = self.ui.list_page.currentIndex()
        return page

    def selectedPage(self):
        page = self.ui.list_page.currentText()
        return page

    def saveMangaSettings(self):
        self.settings.storeMangaSetting(self.selectedManga(), [self.selectedVolumeIdx(), self.selectedChapterIndex(), self.selectedPageIndex()])

    def loadMangaSettings(self):
        manga_settings = self.settings.loadMangaSettings(self.selectedManga())
        if manga_settings:
            volidx, chapteridx, pageidx = manga_settings
            try:
                self.selectEntry(self.ui.list_volume, int(volidx))
                self.selectEntry(self.ui.list_chapter, int(chapteridx))
                self.selectEntry(self.ui.list_page, int(pageidx))
            except NoElementsError:
                pass

    def updateIndices(self):
        # update idx/count text
        self.ui.volume_label.setText("%d/%d" % (self.ui.list_volume.currentIndex()+1, self.ui.list_volume.count()))
        self.ui.chapter_label.setText("%d/%d" % (self.ui.list_chapter.currentIndex()+1, self.ui.list_chapter.count()))
        self.ui.page_label.setText("%d/%d" % (self.ui.list_page.currentIndex()+1, self.ui.list_page.count()))

    def loadVolumeFiles(self):
        self.manga_pages.clear()
        self.manga_chaps.clear()
        self.manga_vols.clear()

        self.ui.list_page.clear()
        self.ui.list_chapter.clear()
        self.ui.list_volume.clear()

        # current manga book
        selected = self.selectedManga()
        if selected in self.manga_books:
            manga_path = self.manga_books[selected]
            #print("Loading volume data from", manga_path)

            vol_layer = Layer(manga_path).open()
            if not vol_layer.image is None:
                self.loadImage(vol_layer.image)
                self.updateIndices()
            elif vol_layer.names is not None:
                self.manga_vols = vol_layer.names

                # add to gui
                self.ui.list_volume.clear()
                self.ui.list_volume.addItems(sorted([key for key, value in self.manga_vols.items()]))
                self.updateIndices()

            self.loadMangaSettings()
        else:
            self.clearImage()

    def loadChapterFiles(self):
        self.manga_pages.clear()
        self.manga_chaps.clear()

        self.ui.list_page.clear()
        self.ui.list_chapter.clear()

        selected = self.selectedVolume()
        if selected in self.manga_vols:
            chap_path = self.manga_vols[selected]
            #print("Loading chapter data from", chap_path)

            chap_layer = chap_path.open()
            if not chap_layer.image is None:
                self.loadImage(chap_layer.image)
                self.updateIndices()
            elif chap_layer.names is not None:
                self.manga_chaps = chap_layer.names

                # add to gui
                self.ui.list_chapter.clear()
                self.ui.list_chapter.addItems(sorted([key for key, value in self.manga_chaps.items()]))
                self.updateIndices()
        else:
            self.clearImage()

    def loadPageFiles(self):
        self.manga_pages.clear()
        self.ui.list_page.clear()

        selected = self.selectedChapter()
        if selected in self.manga_chaps:
            page_path = self.manga_chaps[selected]
            #print("Loading page data from", page_path)

            page_layer = page_path.open()
            if not page_layer.image is None:
                self.loadImage(page_layer.image)
                self.updateIndices()
            elif page_layer.names is not None:
                self.manga_pages = page_layer.names

                # add to gui
                self.ui.list_page.clear()
                self.ui.list_page.addItems(sorted([key for key, value in self.manga_pages.items()]))
                self.updateIndices()
        else:
            self.clearImage()

    def loadPage(self, idx = None):
        """
        load an image
        idx is the selected index of the list_page combobox
        """
        if idx == -1:
            self.clearImage()
            return

        image_layer = self.manga_pages[self.selectedPage()]
        image_layer.open()
        qimg = image_layer.image
        self.loadImage(qimg)

        self.updateIndices()

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

    def loadImage(self, image):
        """ load an image of type QImage """
        if not isinstance(image, QImage):
            #print("cancelling print for", image)
            return

        if not image.isNull():
            self.manga_image = QPixmap.fromImage(image)
            self.ui.manga_image_label.setPixmap(self.manga_image)
            self.resizeEvent(None)

            self.saveMangaSettings()

    def clearImage(self):
        self.manga_image = QPixmap()
        self.resizeEvent(None)

    def clearMangaData(self):
        self.manga_pages.clear()
        self.manga_chaps.clear()
        self.manga_vols.clear()

        self.ui.list_page.clear()
        self.ui.list_chapter.clear()
        self.ui.list_volume.clear()

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

        # save manga settings
        self.saveMangaSettings()

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

    def selectEntry(self, combobox, delta):
        if not isinstance(combobox, QComboBox):
            print("Dammit, not a ComboBox?!")
            return

        idx = combobox.currentIndex()
        count = combobox.count()

        if count == 0:
            raise NoElementsError

        new_idx = idx + delta
        if new_idx < 0 or new_idx >= count:
            return False
        else:
            combobox.setCurrentIndex(new_idx)
            return True

    def keyReleaseEvent(self, event):
        """
        Keyboard stuff:
        Left    Previous page
        Right   Next page
        """
        if event.key() == Qt.Key_Left:
            # go to previous page
            # if the page-list doesn't have any entries then try to go to the previous "chapter"
            # if the chapter-list doesn't have any entries then try to go to the previous "volume"
            boxes = [self.ui.list_page, self.ui.list_chapter, self.ui.list_volume]
            for box in boxes:
                try:
                    if self.selectEntry(box, -1) == False:
                        # show toast with info
                        QToolTip.showText(self.ui.manga_image_label.mapToGlobal(QPoint(0, 0)), "already at first page!")
                    break
                except NoElementsError:
                    continue
        elif event.key() == Qt.Key_Right:
            # go to next page
            # if the page-list doesn't have any entries then try to go to the next "chapter"
            # if the chapter-list doesn't have any entries then try to go to the next "volume"
            boxes = [self.ui.list_page, self.ui.list_chapter, self.ui.list_volume]
            for box in boxes:
                try:
                    if self.selectEntry(box, 1) == False:
                        # show toast with info
                        QToolTip.showText(self.ui.manga_image_label.mapToGlobal(QPoint(0, 0)), "already at last page!")
                    break
                except NoElementsError:
                    continue

    def keyPressEvent(self, event):
        """
        Keyboard stuff:
        Left    Previous page
        Right   Next page
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

    def mouseDoubleClickEvent(self, event):
        self.toggleFullscreen()

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