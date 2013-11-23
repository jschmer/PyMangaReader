import os
import zipfile
import re, io
import rarfile

from PyQt5.QtGui import QImage
from PyMangaLogger import log

supported_archives = ["", ".zip", ".cbz"]
def isSupportedArchive(file):
    global supported_archives
    fileName, fileExtension = os.path.splitext(file)
    return fileExtension.lower() in supported_archives

zip_like_archives = [".zip", ".cbz"]
def isZip(path):
    global zip_like_archives
    fileName, fileExtension = os.path.splitext(path)
    return fileExtension.lower() in zip_like_archives

rar_like_archives = [".rar", ".cbr"]
def isRar(path):
    global rar_like_archives
    fileName, fileExtension = os.path.splitext(path)
    return fileExtension.lower() in rar_like_archives

supported_images = [".png", ".jpg", ".gif"]
def isImage(file):
    global supported_images
    fileName, fileExtension = os.path.splitext(file)
    return fileExtension.lower() in supported_images

# UnRAR stuff
rarfile.UNRAR_TOOL = "unrar"
rarfile.PATH_SEP = '\\'

def isRARactive():
    global supported_archives
    rars = [1 for x in supported_archives if x in rar_like_archives]
    return len(rars) > 0

def setupUnrar(unrar_path):
    global supported_archives
    unrar = which(unrar_path)
    if unrar is None:
        log.warning("UnRAR executable not accessible: %s" % unrar_path)
        log.warning("Disabling rar archive support...")
        rarfile.UNRAR_TOOL = None
        supported_archives = [x for x in supported_archives if x not in rar_like_archives]
    else:
        log.info("UnRAR executable accessible: %s" % unrar)
        log.info("Enabling rar archive support...")
        rarfile.UNRAR_TOOL = unrar
        supported_archives += rar_like_archives

def which(program):
    '''
    Check if a program is in PATH
    Taken from http://stackoverflow.com/a/377028
    '''
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

class Zip(object):
    zipfile = None
    file = None

    def __init__(self, file):
        """ open zip archive pointed to by file """
        self.file = file
        self.load(file)

    def load(self, file):
        """ open zip archive pointed to by file """
        self.zipfile = zipfile.ZipFile(file, "r")
        self.names = self.zipfile.namelist()

    def open(self, name):
        return io.BytesIO(self.zipfile.read(name))

class Rar(object):
    rarfile = None
    file = None

    def __init__(self, file):
        """ open zip archive pointed to by file """
        self.file = file
        self.load(file)

    def load(self, file):
        """ open zip archive pointed to by file """
        self.rarfile = rarfile.RarFile(file, "r")
        self.names = self.rarfile.namelist()

    def open(self, name):
        return io.BytesIO(self.rarfile.read(name))

class Layer():
    """
    Generic Layer that provides a consistent view for archives, directories, files
    """
    path    = None # path to the archive
    archive = None # cache for an opened archive

    def __init__(self, _path, _archive = None):
        self.archive = _archive
        self.path    = _path
        
    def open(self):
        """
        Opens the path the layer was constructed with
        Handles the type of the path appropriately
        and return a list of pairs with (direntry, Layer)
        """
        entries = None
        if isImage(self.path):
            # got an image, load it!
            if self.archive:
                # load the image from the archives!
                log.info("Open image '%s' in archive '%s'" % (self.path, self.archive.file))
                file = self.archive.open(self.path)
                image = QImage()
                if not image.loadFromData(file.read()):
                    log.error("Failed loading image '%s' in archive '%s'" % (self.path, self.archive.file))
                    return None
                return image
            else:
                log.info("Open image '%s' from filesystem" % self.path)
                return QImage(self.path)

        elif isZip(self.path):
            # got a zipfile, open it!
            if self.archive:
                log.info("Open zip '%s' in archive '%s'" % (self.path, self.archive.file))
                file = self.archive.open(self.path)
                archive = Zip(file)
            else:
                log.info("Open zip '%s' from filesystem" % self.path)
                archive = Zip(self.path)

            names = archive.names

            name_pairs = []
            for name in names:
                if isRar(name) or isZip(name) or isImage(name):
                    name_pairs.append( (name, Layer(name, archive)) )
            entries = dict(name_pairs)

        elif isRar(self.path) and isRARactive():
            # got a rarfile, open it!
            if self.archive:
                log.info("Open rar '%s' in archive '%s'" % (self.path, self.archive.file))
                #file = self.archive.open(self.path)
                #archive = Rar(file)
                log.error("Opening rar archives inside another archive isn't supported!")
                raise RuntimeError("Opening rar archives inside another archive isn't supported!")
            else:
                log.info("Open rar '%s' from filesystem" % self.path)
                archive = Rar(self.path)

            names = archive.names

            name_pairs = []
            for name in names:
                if isRar(name) or isZip(name) or isImage(name):
                    name_pairs.append( (name, Layer(name, archive)) )
            entries = dict(name_pairs)

        elif os.path.isdir(self.path):
            # load names in directory
            log.info("Open directory '%s' from filesystem" % self.path)
            dir = os.listdir(self.path)

            # save all names in directory
            name_pairs = []
            for d in dir:
                name_pairs.append((d, Layer(os.path.join(self.path, d))))
            entries = dict(name_pairs)

        else:
            log.warning("Unknown file: %s" % self.path)
            return None

        return entries