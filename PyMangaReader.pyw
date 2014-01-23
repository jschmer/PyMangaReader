import sys, os, threading, time

from ImageQt import ImageQt
from PIL import Image

from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QSettings, QSize, Qt, QTextStream, QEvent, pyqtSignal, QRect)
from PyQt5.QtGui import (QIcon, QKeySequence, QImage, QPainter, QPalette, QPixmap, QTransform, QKeyEvent, QCursor, QFontMetrics, QFont, QColor)
from PyQt5.QtWidgets import (QShortcut, QToolTip, QDialog, QComboBox, QLabel, QScrollArea, QAction, QApplication, QFileDialog, QMainWindow, QMessageBox, QTextEdit, QSizePolicy)

from ui_mainwindow import Ui_MainWindow
from PyMangaSettings import *
from PyMangaLayer import *
from PyMangaLogger import log, setupLoggerFromCmdArgs
from version import FULL_VERSION

class NoElementsError(BaseException): pass

def rotate(image, deg):
    if not isinstance(image, Image.Image):
        raise BaseException
    return image.rotate(-deg) ## rotates ccw!

class OrientationLabel(QLabel):
    rotation = 0

    # font settings
    font = None
    pointsize = 12
    family = "Arial"
    bold = True

    def __init__(self, text, parent):
        super(OrientationLabel, self).__init__(text, parent)
        self.font = QFont() # default application font

    def paintEvent(self, paintEvent):
        painter = QPainter(self)
 
        font = self.font
        font.setFamily(self.family)
        font.setBold(self.bold)
        font.setPointSize(self.pointsize)

        log.info("FONT: %s " % (self.font.toString()))

        # Set default font
        painter.setFont(font)
        # Set font color
        painter.setPen(Qt.black)
        # Get QFontMetrics reference
        fm = painter.fontMetrics()
 
        text = self.text()
        width = self.size().width()
        height = self.size().height()

        dim = lambda: QRect(-5, 5, fm.width(text) + 9, -(fm.height()+5))

        # top
        if self.rotation == 0:
            painter.resetTransform()
            center = QPoint( ( width - fm.width(text))/2, fm.height() )
            rectdimension = dim()
            painter.translate(center)
            painter.fillRect(rectdimension, Qt.white)
            painter.drawRect(rectdimension)
            painter.drawText(QPoint(0, 0), text)

        # right 
        if self.rotation == 90:
            painter.resetTransform()
            center = QPoint( (height - fm.width(text))/2, - width + fm.height())
            rectdimension = dim()
            painter.rotate(90)
            painter.translate(center)
            painter.fillRect(rectdimension, Qt.white)
            painter.drawRect(rectdimension)
            painter.drawText(QPoint(0, 0), text)

        # left
        if self.rotation == 270:
            painter.resetTransform()
            center = QPoint(-height + (height - fm.width(text))/2, fm.height() )
            rectdimension = dim()
            painter.rotate(-90)
            painter.translate(center)
            painter.fillRect(rectdimension, Qt.white)
            painter.drawRect(rectdimension)
            painter.drawText(QPoint(0, 0), text)

        # bottom
        if self.rotation == 180:
            painter.resetTransform()
            center = QPoint( -( width + fm.width(text))/2, -( height - fm.height()) )
            rectdimension = dim()
            painter.rotate(180)
            painter.translate(center)
            painter.fillRect(rectdimension, Qt.white)
            painter.drawRect(rectdimension)
            painter.drawText(QPoint(0, 0), text)

class DoubleClickLabel(QLabel):
    onDoubleClick = pyqtSignal()

    def __init__(self):
        super(DoubleClickLabel, self).__init__()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.onDoubleClick.emit()


WindowActive = QEvent.WindowActivate
WindowPassive = QEvent.WindowDeactivate

class MainWindow(QMainWindow):
    manga_image = None  # holds the real image for display
    absolute_rotation = 0
    windowStatus = WindowPassive
    resize_mode = None
    scale_factor = 1.0
    zoomed = False

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

    shortcuts = dict()

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

        self.settings = Settings(self)   # initialize and load settings from system
        self.resize_mode = Image.BICUBIC

        # adjust tooltip font
        font = QGuiApplication.font()
        font.setPointSize(26)
        QToolTip.setFont(font)

        # Set up the user interface from Designer
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(APPLICATION)
        self.resize(800, 600) # arbitrary default size

        self.toast_label = OrientationLabel("TOAST MESSAGE", self.ui.scrollArea)
        self.toast_label.hide()

        self.manga_image_label = self.ui.manga_image_label
        self.manga_image_label = DoubleClickLabel()
        self.manga_image_label.onDoubleClick.connect(self.toggleFullscreen)
        self.manga_image_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.manga_image_label.setStyleSheet("background-color: rgb(0, 0, 0);\ncolor: rgb(255, 255, 255);")
        self.manga_image_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.manga_image_label.setScaledContents(False)

        # scrollArea alias
        self.scrollArea = self.ui.scrollArea

        self.scrollArea.setWidget(self.manga_image_label)

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
        self.ui.pushPrevManga.clicked.connect(self.on_navigate_to_prev_manga)
        self.ui.pushNextManga.clicked.connect(self.on_navigate_to_next_manga)

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
        # also selects last viewed manga
        self.loadMangaBooks()

        # load previous image absolute rotation
        rot = self.settings.load("absolute_rotation")
        if rot is not None and self.manga_image is not None:
            self.rotate(int(rot))

        # refresh GUI
        self.refreshGUI()
        self.checkForEmptyMangas()
        self.connectShortcuts()

    def connectShortcuts(self):
        """ Precondition: Shortcuts need to be already defined!! """
        self.settings.shortcuts["Rotate CW"].activated.connect(self.rotate_right)
        self.settings.shortcuts["Rotate CCW"].activated.connect(self.rotate_left)
        self.settings.shortcuts["Next Page"].activated.connect(self.pageflipNext)
        self.settings.shortcuts["Previous Page"].activated.connect(self.pageflipPrev)
        self.settings.shortcuts["Quit"].activated.connect(self.tryClose)
        self.settings.shortcuts["Toggle Fullscreen"].activated.connect(self.toggleFullscreen)
        self.settings.shortcuts["Show/Hide Menu"].activated.connect(self.showMenu)

        resize_mode_nearest = QShortcut(QKeySequence(Qt.Key_1), self)
        resize_mode_nearest.activated.connect(self.setResizeModeNearest)
        self.shortcuts["resize_mode_nearest"] = resize_mode_nearest

        resize_mode_bilinear = QShortcut(QKeySequence(Qt.Key_2), self)
        resize_mode_bilinear.activated.connect(self.setResizeModeBilinear)
        self.shortcuts["resize_mode_bilinear"] = resize_mode_bilinear

        resize_mode_bicubic = QShortcut(QKeySequence(Qt.Key_3), self)
        resize_mode_bicubic.activated.connect(self.setResizeModeBicubic)
        self.shortcuts["resize_mode_bicubic"] = resize_mode_bicubic

        resize_mode_antialias = QShortcut(QKeySequence(Qt.Key_4), self)
        resize_mode_antialias.activated.connect(self.setResizeModeAntiAlias)
        self.shortcuts["resize_mode_antialias"] = resize_mode_antialias

        zoom = QShortcut(QKeySequence(Qt.Key_Z), self)
        zoom.activated.connect(self.zoom)
        self.shortcuts["zoom"] = zoom

        unzoom = QShortcut(QKeySequence(Qt.Key_U), self)
        unzoom.activated.connect(self.unzoom)
        self.shortcuts["unzoom"] = unzoom

    def setResizeModeNearest(self):
        self.resize_mode = Image.NEAREST
        self.showToast("Using resize mode 'NEAREST'")
        self.refreshMangaImage()

    def setResizeModeBilinear(self):
        self.resize_mode = Image.BILINEAR
        self.showToast("Using resize mode 'BILINEAR'")
        self.refreshMangaImage()

    def setResizeModeBicubic(self):
        self.resize_mode = Image.BICUBIC
        self.showToast("Using resize mode 'BICUBIC'")
        self.refreshMangaImage()

    def setResizeModeAntiAlias(self):
        self.resize_mode = Image.ANTIALIAS
        self.showToast("Using resize mode 'ANTIALIAS'")
        self.refreshMangaImage()

    # GETTER
    def selectedMangaIdx(self):
        """ current selected manga index in the dropdown box """
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
        self.settings.storeMangaSetting(manga, [self.selectedVolume(), self.selectedChapter(), self.selectedPage()])

    def loadMangaSettings(self):
        """ select last viewed volume/chapter/manga for current manga """
        log.info("Loading manga page settings for %s" % self.selectedManga())
        manga_settings = self.settings.loadMangaSettings(self.selectedManga())
        if manga_settings:
            vol, chapter, page = manga_settings
            try:
                idx = self.dropdown_volume.findText(vol)
                if idx == -1: idx = 0
                self.selectEntry(self.dropdown_volume, idx)

                idx = self.dropdown_chapter.findText(chapter)
                if idx == -1: idx = 0
                self.selectEntry(self.dropdown_chapter, idx)

                idx = self.dropdown_page.findText(page)
                if idx == -1: idx = 0
                self.selectEntry(self.dropdown_page, idx)

            except NoElementsError:
                pass

    def loadLastSelectedManga(self):
        last_manga = self.settings.load("last_manga")
        log.info("Loading last selected manga: %s" % last_manga)
        if last_manga:
            # select it!
            idx = self.dropdown_manga.findText(last_manga)
            currentIdx = self.selectedMangaIdx()
            if idx == -1: idx = 0
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
            list = [(x, os.path.join(path, x)) for x in manga_names if isSupportedArchive(os.path.join(path, x))]
            manga_list += list

        # convert to dicts for easy lookup
        self.manga_books = dict(manga_list)

        # add the manga names to the manga dropdown
        self.dropdown_manga.currentIndexChanged.disconnect()
        self.dropdown_manga.addItems(sorted([key for key, value in self.manga_books.items()]))
        self.dropdown_manga.currentIndexChanged.connect(self.loadVolumeFiles)

        self.loadLastSelectedManga()
        #self.loadVolumeFiles()

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

            vol_layer = Layer(manga_path)

            self.load(vol_layer, self.manga_vols, self.dropdown_volume)
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
            chap_layer = self.manga_vols[selected]
            log.info("Loading chapter data from %s" % chap_layer.path)

            self.load(chap_layer, self.manga_chaps, self.dropdown_chapter)
    
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
            # current selected volume is not in internal dict buffer
            # -> clear image
            self.clearImage()
        else:
            page_layer = self.manga_chaps[selected]
            log.info("Loading page data from %s" % page_layer.path)

            self.load(page_layer, self.manga_pages, self.dropdown_page)

    def load(self, layer, store, dropdown):
        """
        if the content of layer are other files:
            load the content into the store and dropdown box
        if the content of layer is an image:
            load the image and display it
        """
        names_or_image = dict()
        try:
            names_or_image = layer.open()
        except Exception as ex:
            self.showToast("Failed loading %s\nMsg: %s" % (layer.path, ex))
        else:
            if isinstance(names_or_image, Image.Image):
                self.loadImage(names_or_image)
            elif isinstance(names_or_image, dict):
                store.clear()
                store.update(names_or_image) # (name, path) dict!

                # add names to dropdown, was already cleared before
                dropdown.addItems(sorted([key for key, value in store.items()]))
           
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
        try:
            image = image_layer.open()
            self.loadImage(image)
        except BaseException as ex:
            self.showToast("Failed loading %s" % image_layer.path)

        self.refreshGUI()

    def loadImage(self, image):
        """ Load an image of type Image """
        if not isinstance(image, Image.Image):
            return

        # if the image is not empty
        if not image is None:
            # convert to qpixmap and save in internal buffer
            self.manga_image = rotate(image, self.absolute_rotation)

            # trigger resizing (includes setting/showing the image)
            self.refreshMangaImage()

    # CLEARER
    def clearImage(self):
        """ Clear the current image """
        self.manga_image = None
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
        self.toast_label.rotation = self.absolute_rotation # update toast label rotation
        self.manga_image = rotate(self.manga_image, deg);
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

    def isMenuVisible(self):
        return self.ui.groupBox.isVisible()

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

        self.updateMouseCursor()
        self.refreshMangaImage()

    def updateMouseCursor(self):
        if not self.isMenuVisible() and self.isFullScreen() and self.windowStatus == WindowActive:
            self.hideMouseCursor()
        else:
            self.showMouseCursor()

    def showMouseCursor(self):
        QApplication.restoreOverrideCursor();

    def hideMouseCursor(self):
        QApplication.setOverrideCursor(QCursor(Qt.BlankCursor))

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

        self.updateMouseCursor()

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
        
        # resize toast label
        self.toast_label.resize(self.manga_image_label.size())

        # resize manga image only if it is not empty
        pic = self.manga_image
        if pic is None:
            pic = QPixmap()
        else:
            maxwidth  = self.manga_image_label.size().width()
            maxheight = self.manga_image_label.size().height()

            width = pic.size[0]
            height = pic.size[1]
            ratio = min(maxwidth/width, maxheight/height)

            pic = self.manga_image.resize((int(width*ratio), int(height*ratio)), self.resize_mode)
            # or PIL.Image.NEAREST
            # or PIL.Image.BILINEAR
            # or PIL.Image.BICUBIC
            # or PIL.Image.ANTIALIAS (for downsampling?)

            # convert PIL.Image to QPixmap
            self.___cached_data = ImageQt(pic) # to prevent python to clean the data up that qpixmap references :I
            pic = QPixmap.fromImage(self.___cached_data)

        # update label with scaled pixmap (or empty pixmap)
        self.manga_image_label.setPixmap(pic)

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
            
    def wheelEvent(self, event):
        """ Trigger left or right arrow key based on wheel direction """
        delta = event.angleDelta().y()
        if delta > 0:
            self.pageflipPrev()
        elif delta < 0:
            self.pageflipNext()
        pass

    def mousePressEvent(self, event):
        if event.button() == Qt.ExtraButton1:
            # mouse backward
            self.unzoom()
        elif event.button() == Qt.ExtraButton2:
            # mouse forwared
            self.zoom()
        #else:
        #    log.info("Mouse %d" % event.button())

    def checkForEmptyMangas(self):
        # ask if settings should be opened if no mangas were found
        if self.dropdown_manga.count() == 0:
            answer = QMessageBox.question(self, "Open Settings?", "No Mangas found!\nWould you like to open the settings?", QMessageBox.Yes | QMessageBox.No)
            if answer == QMessageBox.Yes:
                self.on_settings()

    def on_settings(self):
        """ Show settings dialog """
        if self.settings.execDialog():
            self.loadMangaBooks()
        self.refreshGUI()
        self.checkForEmptyMangas()

    def on_about(self):
        """ Show about box """
        QMessageBox.about(self,
            "About",
            """
            PyMangaReader

            Version: %s
            Released under the MIT License
            Copyright 2013 Jens Schmer
            """
            % FULL_VERSION
            )

    # Keyboard shortcut functions
    def tryClose(self):
        if not self.isFullScreen():
            self.close()
        else:
            self.toggleFullscreen()

    def rotate_right(self):
        self.rotate(90)

    def rotate_left(self):
        self.rotate(-90)

    def pageflipPrev(self):
        self.resetZoom()

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
                else:
                    cur_box = box

                # also select last entry in each child boxes
                # cur_box is the dropdown box that was sucessfully decremented without going over bounds
                cur_box = cur_box.child
                while cur_box and self.selectEntry(cur_box, cur_box.count() - 1) == True:
                    cur_box = cur_box.child

                break
            except NoElementsError:
                continue

    def pageflipNext(self):
        self.resetZoom()

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

    def on_navigate_to_prev_manga(self):
        self.selectEntry(self.dropdown_manga, -1)

    def on_navigate_to_next_manga(self):
        self.selectEntry(self.dropdown_manga, 1)

    def event(self, event):
        if event.type() in (QEvent.WindowActivate, QEvent.WindowDeactivate):
            self.windowStatus = event.type()
            self.updateMouseCursor()

        return super().event(event)

    def scaleImage(self, factor):
        scale_factor = self.scale_factor
        if scale_factor < 0.3 or scale_factor > 2:
            return
        scale_factor *= factor;

        self.scrollArea.setWidgetResizable(False) # honors the manga_image_label size         

        image_size = self.manga_image_label.pixmap().size()
        scaled_image_size = image_size * scale_factor

        # manga_image is a PIL.Image, use biliniear filter for speed
        pic = self.manga_image.resize((scaled_image_size.width(), scaled_image_size.height()), Image.BILINEAR)
        
        # convert PIL.Image to QPixmap
        self.___cached_data = ImageQt(pic) # to prevent python to clean the data up that qpixmap references :I
        pic = QPixmap.fromImage(self.___cached_data)

        # update label with scaled pixmap (or empty pixmap)
        self.manga_image_label.setPixmap(pic)

        # adjust size of the image label (but minimum is scrollArea size!) to let the scrollArea create scrollbars
        w = max(scaled_image_size.width(), self.scrollArea.size().width())
        h = max(scaled_image_size.height(), self.scrollArea.size().height())

        if w > self.scrollArea.size().width():
            #log.info("Showing horizontal scrollbar")
            # works for now but should be determined programatically,
            # unforunately the scrollbars aren't shown yet so we can't get the
            # actual size with self.scrollArea.horizontalScrollBar().size().height()
            h -= 17
        if h > self.scrollArea.size().height():
            #log.info("Showing vertical scrollbar")
            w -= 17 # self.scrollArea.verticalScrollBar().size().width()

        self.manga_image_label.resize(w, h)

        adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor);
        adjustScrollBar(self.scrollArea.verticalScrollBar(), factor);

    def zoom(self):
        self.scaleImage(1.1)
    
    def unzoom(self):
        self.scaleImage(0.9)

    def resetZoom(self):
        self.scale_factor = 1.0
        self.scrollArea.setWidgetResizable(True)


def adjustScrollBar(scrollBar, factor):
    scrollBar.setValue(int(factor * scrollBar.value() + ((factor - 1) * scrollBar.pageStep()/2)));

if __name__ == '__main__':
    setupLoggerFromCmdArgs(sys.argv)

    try:
        app = QApplication(sys.argv)
        mainWin = MainWindow()
        mainWin.show()
        sys.exit(app.exec_())
    except Exception as ex:
        log.exception(ex)