import sys
import os
import threading
import time

from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QSettings, QSize, Qt, QTextStream, QEvent)
from PyQt5.QtGui import (QIcon, QKeySequence, QImage, QPainter, QPalette, QPixmap, QTransform, QKeyEvent)
from PyQt5.QtWidgets import (QToolTip, QDialog, QComboBox, QLabel, QScrollArea, QAction, QApplication, QFileDialog, QMainWindow, QMessageBox, QTextEdit, QSizePolicy)

from ui_mainwindow import Ui_MainWindow
from PyMangaSettings import *
from PyMangaLayer import *
from PyMangaLogger import log, setupLoggerFromCmdArgs
from version import FULL_VERSION

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

def rotate(image, deg):
    if not isinstance(image, QPixmap):
        raise BaseException
    rot = QTransform().rotate(deg)
    return image.transformed(rot)

class MainWindow(QMainWindow):
    manga_image = None  # holds the real image for display
    absolute_rotation = 0

    manga_before = None # cache for last selected manga
    settings = None

    # dicts for the manga hierarchy
    manga_books = {}
    manga_vols = {}
    manga_chaps = {}
    manga_pages = {}

    # aliases for the dropdown boxes on the UI
    dropdown_manga = None
    dropdown_volume = None
    dropdown_chapter = None
    dropdown_page = None

    toast_thr = threading.Thread()

    def __init__(self, fileName=None):
        """
        init MainWindow:
        - load UI
        - apply last saved window properties (position and size)
        - load settings from system
        - load mangas in specified manga base directories
        - select last viewed manga
          (last viewed manga/chapter/page are selected with the event handler for dropdown_manga indexChanged)
        """
        super(MainWindow, self).__init__()

        self.settings = Settings()   # initialize and load settings from system
        self.manga_image = QPixmap() 

        # adjust tooltip font
        font = QGuiApplication.font()
        font.setPointSize(26)
        QToolTip.setFont(font)

        # Set up the user interface from Designer
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(APPLICATION)
        self.resize(800, 600) # arbitrary default size

        self.toast_label = QLabel("TOAST MESSAGE", self.ui.scrollArea)
        self.toast_label.setStyleSheet("background-color: rgb(255, 255, 255);\nborder: 1px solid rgb(0, 0, 0);\ncolor: rgb(0, 0, 0);")
        self.toast_label.setAlignment(Qt.AlignCenter)
        self.toast_label.setMargin(5)
        self.toast_label.hide()

        # load previous window geometry
        geom = self.settings.load("geometry")
        if geom:
            self.restoreGeometry(geom)

            # show normal window and menu by default, regardless of last stored window pos/size
            # fullscreen at startup doesn't happen this way
            self.showMenu(True)
            self.showNormal()
            self.refreshMangaImage()

        # give an alias to the dropdown boxes for easier name changes
        self.dropdown_manga   = self.ui.list_manga
        self.dropdown_volume  = self.ui.list_volume
        self.dropdown_chapter = self.ui.list_chapter
        self.dropdown_page    = self.ui.list_page

        # connect button clicks
        self.ui.pushSettings.clicked.connect(self.on_settings)
        self.ui.pushAbout   .clicked.connect(self.on_about)

        # and dropdown changes
        self.dropdown_manga  .currentIndexChanged.connect(self.loadVolumeFiles)
        self.dropdown_volume .currentIndexChanged.connect(self.loadChapterFiles)
        self.dropdown_chapter.currentIndexChanged.connect(self.loadPageFiles)
        self.dropdown_page   .currentIndexChanged.connect(self.loadPage)

        # "Connect" dropdown box hierarchy for selecting e.g. the next volume if we are at the last page
        self.dropdown_volume.parent = None
        self.dropdown_volume.child = self.dropdown_chapter
        self.dropdown_chapter.parent = self.dropdown_volume
        self.dropdown_chapter.child = self.dropdown_page
        self.dropdown_page.parent = self.dropdown_chapter
        self.dropdown_page.child = None

        # load mangas in manga directory setting, needs self.dropdown_manga.currentIndexChanged to be connected
        self.loadMangaBooks()

        # select last viewed manga
        self.loadLastSelectedManga()

        # load previous image absolute rotation
        rot = self.settings.load("absolute_rotation")
        if rot != None:
            self.rotate(int(rot))

        # refresh GUI
        self.refreshGUI()

    # GETTER
    def selectedMangaIdx(self):
        """ current selected volume index in the dropdown box """
        vol = self.dropdown_manga.currentIndex()
        return vol
    
    def selectedManga(self):
        """ current selected manga as string """
        manga = self.dropdown_manga.currentText()
        return manga

    def selectedVolumeIdx(self):
        """ current selected volume index in the dropdown box """
        vol = self.dropdown_volume.currentIndex()
        return vol

    def selectedVolume(self):
        """ current selected volume as string """
        vol = self.dropdown_volume.currentText()
        return vol

    def selectedChapterIndex(self):
        """ current selected chapter index in the dropdown box """
        chap = self.dropdown_chapter.currentIndex()
        return chap

    def selectedChapter(self):
        """ current selected chapter as string """
        chap = self.dropdown_chapter.currentText()
        return chap

    def selectedPageIndex(self):
        """ current selected page index in the dropdown box """
        page = self.dropdown_page.currentIndex()
        return page

    def selectedPage(self):
        """ current selected page as string """
        page = self.dropdown_page.currentText()
        return page

    # SETTINGS STUFF
    def saveMangaSettings(self, manga):
        """ save current selected volume/chapter/page for given manga """
        log.info("Saving manga page settings for %s" % manga)
        self.settings.storeMangaSetting(manga, [self.selectedVolumeIdx(), self.selectedChapterIndex(), self.selectedPageIndex()])

    def loadMangaSettings(self):
        """ select last viewed volume/chapter/manga for current manga """
        log.info("Loading manga page settings for %s" % self.selectedManga())
        manga_settings = self.settings.loadMangaSettings(self.selectedManga())
        if manga_settings:
            volidx, chapteridx, pageidx = manga_settings
            try:
                self.selectEntry(self.dropdown_volume, int(volidx))
                self.selectEntry(self.dropdown_chapter, int(chapteridx))
                self.selectEntry(self.dropdown_page, int(pageidx))
            except NoElementsError:
                pass

    def loadLastSelectedManga(self):
        last_manga = self.settings.load("last_manga")
        log.info("Loading last selected manga: %s" % last_manga)
        if last_manga:
            # select it!
            idx = self.dropdown_manga.findText(last_manga)
            currentIdx = self.selectedMangaIdx()
            if idx != currentIdx:
                self.dropdown_manga.setCurrentIndex(idx)
            else:
                # force the loading if it is already idx 0, setCurrentIndex wouldn't trigger
                # the currentIndexChanged slot and not call self.loadVolumeFiles()
                self.loadVolumeFiles()

    # LOADER
    def refreshGUI(self):
        """ Refresh the idx/count labels in front of the dropdown boxes """
        # update idx/count text
        self.ui.volume_label .setText("%d/%d" % (self.dropdown_volume.currentIndex() + 1,  self.dropdown_volume.count()))
        self.ui.chapter_label.setText("%d/%d" % (self.dropdown_chapter.currentIndex() + 1, self.dropdown_chapter.count()))
        self.ui.page_label   .setText("%d/%d" % (self.dropdown_page.currentIndex() + 1,    self.dropdown_page.count()))

        # hide empty boxes/labels
        if self.dropdown_volume.count() == 0:
            self.dropdown_volume.hide()
            self.ui.volume_label.hide()
        else:
            self.dropdown_volume.show()
            self.ui.volume_label.show()

        if self.dropdown_chapter.count() == 0:
            self.dropdown_chapter.hide()
            self.ui.chapter_label.hide()
        else:
            self.dropdown_chapter.show()
            self.ui.chapter_label.show()

        if self.dropdown_page.count() == 0:
            self.dropdown_page.hide()
            self.ui.page_label.hide()
        else:
            self.dropdown_page.show()
            self.ui.page_label.show()

    def loadMangaBooks(self):
        """ Scan each configured manga directory for top-level mangas """
        # save the manga settings (selected volume/chapter/page) if there was a manga selected before
        if self.manga_before:
            self.saveMangaSettings(self.manga_before)
        self.manga_before = None # no manga selected, this practically disables saving [0,0,0] for last manga page settings

        self.clearMangaData()
        self.dropdown_manga.clear()

        manga_list = []
        for path in self.settings.settings[MANGA_DIRS]:
            manga_names = os.listdir(os.path.abspath(path))

            # save as (name, path) pairs
            list = [(x, os.path.join(path, x)) for x in manga_names]
            manga_list += list

        # convert to dicts for easy lookup
        self.manga_books = dict(manga_list)

        # add the manga names to the manga dropdown
        self.dropdown_manga.currentIndexChanged.disconnect()
        self.dropdown_manga.addItems(sorted([key for key, value in self.manga_books.items()]))
        self.dropdown_manga.currentIndexChanged.connect(self.loadVolumeFiles)

        self.loadLastSelectedManga()
        self.loadVolumeFiles()

    def loadVolumeFiles(self):
        """
        Load the volume names for the current selected manga
        This is triggered by an index change in the manga dropdown box
        Also loads the last selected volume/chapter/page for the new selected manga
        """
        # save last selected manga
        if self.selectedManga() != "":
            self.settings.store("last_manga", self.selectedManga())

        # save the manga settings (selected volume/chapter/page) if there was a manga selected before
        if self.manga_before:
            self.saveMangaSettings(self.manga_before)
        self.manga_before = self.selectedManga() # new manga is the selected manga before changing the index in the manga dropdown :)

        self.clearMangaData()

        selected = self.selectedManga()
        if selected not in self.manga_books:
            # current selected manga is not in internal dict buffer?
            # -> clear image
            self.clearImage() 
        else:
            manga_path = self.manga_books[selected]

            log.info("Loading volume data from %s" % manga_path)

            # load the volumes under manga_path with the Layer proxy
            vol_layer = Layer(manga_path).open()
            if vol_layer.image is not None:
                # manga_path is an image! show it!
                self.loadImage(vol_layer.image)
                
            elif vol_layer.names is not None:
                # got some volumes, save them in internal dict for future lookup
                self.manga_vols = vol_layer.names # this is saved as (name, path) dict

                # add volume names to dropdown, was already cleared before
                self.dropdown_volume.addItems(sorted([key for key, value in self.manga_vols.items()]))
                
            self.refreshGUI()     # refresh the idx/count labels in front of the dropdowns
            self.loadMangaSettings() # load last selected volume/chapter/page for current manga

    def loadChapterFiles(self):
        """
        Load the chapter names for the current selected volume
        This is triggered by an index change in the volume dropdown box
        """
        # clear any remaining data
        self.manga_pages.clear()
        self.manga_chaps.clear()
        self.dropdown_page.clear()
        self.dropdown_chapter.clear()

        selected = self.selectedVolume()
        if selected not in self.manga_vols:
            # current selected volume is not in internal dict buffer?
            # -> clear image
            self.clearImage()
        else:
            chap_path = self.manga_vols[selected]

            log.info("Loading chapter data from %s" % chap_path.path)

            # load the chapters under chap_path with the Layer proxy
            chap_layer = chap_path.open()
            if chap_layer.image is not None:
                # chap_path is an image! show it!
                self.loadImage(chap_layer.image)

            elif chap_layer.names is not None:
                # got some chapters, save them in internal dict for future lookup
                self.manga_chaps = chap_layer.names # (name, path) dict!

                # add chapter names to dropdown, was already cleared before
                self.dropdown_chapter.addItems(sorted([key for key, value in self.manga_chaps.items()]))
           
            self.refreshGUI() # refresh the idx/count labels in front of the dropdowns
    
    def loadPageFiles(self):
        """
        Load the page names for the current selected chapter
        This is triggered by an index change in the chapter dropdown box
        """
        # clear any remaining data
        self.manga_pages.clear()
        self.dropdown_page.clear()

        selected = self.selectedChapter()
        if selected not in self.manga_chaps:
            # current selected volume is not in internal dict buffer?
            # -> clear image
            self.clearImage()
        else:
            page_path = self.manga_chaps[selected]

            log.info("Loading page data from %s" % page_path.path)

            page_layer = page_path.open()
            if page_layer.image is not None:
                # chap_path is an image! show it!
                self.loadImage(page_layer.image)
                
            elif page_layer.names is not None:
                # got some pages, save them in internal dict for future lookup
                self.manga_pages = page_layer.names # (name, path) dict!

                # add page names to dropdown, was already cleared before
                self.dropdown_page.addItems(sorted([key for key, value in self.manga_pages.items()]))

            self.refreshGUI() # refresh the idx/count labels in front of the dropdowns

    def loadPage(self, idx = None):
        """
        Open the image for the current selected page
        This is triggered by an index change in the page dropdown box
        """
        # nothing selected in the page box
        if idx == -1:
            self.clearImage()
            return

        # open selected page
        image_layer = self.manga_pages[self.selectedPage()]  
        self.loadImage(image_layer.open().image)

        self.refreshGUI()

    def loadImage(self, image):
        """ Load an image of type QImage """
        if not isinstance(image, QImage):
            return

        # if the image is not empty
        if not image.isNull():
            # convert to qpixmap and save in internal buffer
            self.manga_image = rotate(QPixmap.fromImage(image), self.absolute_rotation)

            # trigger resizing (includes setting/showing the image)
            self.refreshMangaImage()

    # CLEARER
    def clearImage(self):
        """ Clear the current image """
        self.manga_image = QPixmap()
        self.refreshMangaImage()

    def clearMangaData(self):
        """ Clear all data for selected manga """
        self.manga_pages.clear()
        self.manga_chaps.clear()
        self.manga_vols.clear()

        self.dropdown_page.clear()
        self.dropdown_chapter.clear()
        self.dropdown_volume.clear()

    # HELPER
    def rotate(self, deg):
        """ Rotate image by deg, always relative to the rotation before """
        self.absolute_rotation = (self.absolute_rotation + deg) % 360
        rot = QTransform().rotate(deg)
        self.manga_image = self.manga_image.transformed(rot);
        self.refreshMangaImage()

    def refreshMangaImage(self):
        self.resizeEvent(None)
        
    def geometryUpdateHack(self):
        """
        yay! hacking around! qt doesn't update the size of the qlabel after hiding the settings groupbox
        so i force the update here with hiding and showing the centralwidget
        """
        self.ui.centralwidget.hide()
        self.ui.centralwidget.show()

    def showMenu(self, activate = None):
        """
        Show the menu, if activate is not given, it is toggled
        """
        if activate == None:
            activate = not self.ui.groupBox.isVisible()

        if activate:
            self.ui.groupBox.show()
        else:
            self.ui.groupBox.hide()

        self.refreshMangaImage()

    def toggleFullscreen(self):
        """
        Toggle fullscreen mode,
        automatically hides the menu in fullscreen and shows it in normal mode
        The MainWindow is goind fullscreen because it should be possible to show the menu in fullscreen also,
        if the image would only go fullscreen this wouldn't be possible (as far as i know?)
        """
        if not self.isFullScreen():
            self.showMenu(False)
            self.showFullScreen()
        else:
            self.showMenu(True)
            self.showNormal()

    def selectEntry(self, combobox, delta):
        """
        Select the entry delta indexes away in the given combobox
        returns True if the index could be selected,
                False if the index is not in the range [0, number of combobox entries]
        raises  NoElementsError if the combobox doesn't have any entries at all
        """
        if not isinstance(combobox, QComboBox):
            log.error("Dammit, not a ComboBox?!")
            return

        idx = combobox.currentIndex()
        count = combobox.count()

        if count == 0:
            raise NoElementsError

        new_idx = idx + delta
        if new_idx < 0 or new_idx >= count: # catch any out of bounds indices
            return False
        else:
            combobox.setCurrentIndex(new_idx)
            return True

    def toast(self, label, duration):
        sleep_step = 0.01

        log.info("Showing toast for %d seconds" % duration)
        label.show()
        while not self.stop_toast and duration > 0:
            time.sleep(sleep_step)
            duration -= sleep_step
        label.hide()
        log.info("Hiding toast")

    def showToast(self, message):
        while self.toast_thr and self.toast_thr.is_alive():
            self.stop_toast = True
            self.toast_thr.join()

        self.toast_label.setText(message)

        self.stop_toast = False
        self.toast_thr = threading.Thread(target=self.toast, args=(self.toast_label, 3))
        self.toast_thr.start()

    # EVENT HANDLER
    def resizeEvent(self, event):
        """ Fit manga image into the image label """
        # force an geometry update for all widgets
        self.geometryUpdateHack()
        
        # resize manga image (pixmap) only if it is not empty
        pic = self.manga_image
        if not pic.isNull():
            pic = self.manga_image.scaled(self.ui.manga_image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # update label with scaled pixmap (or empty pixmap)
        self.ui.manga_image_label.setPixmap(pic)

    def closeEvent(self, event):
        """ Close the window but save settings before that! """
        # save window geometry
        self.settings.store("geometry", self.saveGeometry());

        # save absolute image rotation
        self.settings.store("absolute_rotation", self.absolute_rotation)
        
        # save last vol/chap/page for current manga
        self.saveMangaSettings(self.selectedManga())

        # save general settings (manga dirs, manga settings path, ...)
        self.settings.save()

        QMainWindow.closeEvent(self, event);

    def keyReleaseEvent(self, event):
        """
        Keyboard stuff:
        Left    Previous page
        Right   Next page

        Arrow keys somehow don't generate a keyPressEvent :(
        That's why they are handled here
        """
        if event.key() == Qt.Key_Left:
            # go to previous page
            # if the page-list doesn't have any entries then try to go to the previous "chapter"
            # if the chapter-list doesn't have any entries then try to go to the previous "volume"
            boxes = [self.dropdown_page, self.dropdown_chapter, self.dropdown_volume]
            for box in boxes:
                try:
                    if self.selectEntry(box, -1) == False:
                        # already at first entry in box -> try to decrement its parents until one can be decremented
                        # and show toast with info
                        cur_box = box.parent

                        while cur_box and self.selectEntry(cur_box, -1) == False:
                            cur_box = cur_box.parent
                        if cur_box == None:
                            self.showToast("Already at first page of the Manga!")
                            break
                        else:
                            self.showToast("Prev: %s" % cur_box.currentText())

                        # also select last entry in each child boxes (as we are coming from above)
                        cur_box = cur_box.child
                        while cur_box and self.selectEntry(cur_box, cur_box.count() - 1) == True:
                            cur_box = cur_box.child

                    break
                except NoElementsError:
                    continue
        elif event.key() == Qt.Key_Right:
            # go to next page
            # if the page-list doesn't have any entries then try to go to the next "chapter"
            # if the chapter-list doesn't have any entries then try to go to the next "volume"
            boxes = [self.dropdown_page, self.dropdown_chapter, self.dropdown_volume]
            for box in boxes:
                try:
                    if self.selectEntry(box, 1) == False:
                        # already at last entry in box -> try to advance its parents until one can be advanced
                        # and show toast with info
                        cur_box = box.parent

                        while cur_box and self.selectEntry(cur_box, 1) == False:
                            cur_box = cur_box.parent
                        if cur_box == None:
                            self.showToast("Already at last page of the Manga!")
                            break
                        else:
                            self.showToast("Next: %s" % cur_box.currentText())

                    break
                except NoElementsError:
                    continue

    def keyPressEvent(self, event):
        """
        Keyboard stuff:
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
            if not self.isFullScreen():
                self.close()
            else:
                self.toggleFullscreen()

    def mouseDoubleClickEvent(self, event):
        self.toggleFullscreen()

    def wheelEvent(self, event):
        """ Trigger left or right arrow key based on wheel direction """
        delta = event.angleDelta().y()
        if delta > 0:
            self.keyReleaseEvent(QKeyEvent(QEvent.KeyRelease, Qt.Key_Left, Qt.NoModifier))
        elif delta < 0:
            self.keyReleaseEvent(QKeyEvent(QEvent.KeyRelease, Qt.Key_Right, Qt.NoModifier))
        pass

    def on_settings(self):
        """ Show settings dialog """
        if self.settings.execDialog():
            self.loadMangaBooks()
        self.refreshGUI()

    def on_about(self):
        """ Show about box """
        QMessageBox.about(self,
            "About",
            """
            PyMangaReader

            Version: %s
            Release under the MIT License
            Copyright 2013 Jens Schmer
            """
            % FULL_VERSION
            )

if __name__ == '__main__':
    setupLoggerFromCmdArgs(sys.argv)

    try:
        app = QApplication(sys.argv)
        mainWin = MainWindow()
        mainWin.show()
        sys.exit(app.exec_())
    except Exception as ex:
        log.exception(ex)