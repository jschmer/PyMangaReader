import os
import zipfile
import re, io
import rarfile

#from PyQt5.QtGui import QImage
from PIL import Image
from PyMangaLogger import log

supported_archives = [".zip", ".cbz"]
def isSupportedArchive(file):
    if os.path.isdir(file):
        return True

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
    return the path to the program
    or None if it couldn't be found
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
    """ zipfile wrapper with a totally simple API """
    zipfile = None  # zipfile instance
    file    = None
    names   = None  # archive content of zipfile/file

    def __init__(self, file):
        self.file = file
        self.load(file)

    def load(self, file):
        """ load filenames in the archive pointed to by file """
        self.zipfile = zipfile.ZipFile(file, "r")
        self.names = self.zipfile.namelist()

    def open(self, name):
        """ open the file with name in this archive as bytestream """
        return io.BytesIO(self.zipfile.read(name))

class Rar(object):
    """ rarfile wrapper with a totally simple API """
    rarfile = None
    file    = None
    names   = None  # archive content of rarfile/file

    def __init__(self, file):
        self.file = file
        self.load(file)

    def load(self, file):
        """ load files in the archive pointed to by file """
        self.rarfile = rarfile.RarFile(file, "r")
        self.names = self.rarfile.namelist()

    def open(self, name):
        """ open the file with name in this archive as bytestream """
        return io.BytesIO(self.rarfile.read(name))

class Layer():
    """
    Generic Layer that provides a consistent view for archives, directories, images
    """
    path    = None # path to the archive/dir/image
    archive = None # cache for an opened archive

    def __init__(self, _path, _archive = None):
        self.archive = _archive
        self.path    = _path
        
    def open(self):
        """
        Opens the path the layer was constructed with.
        Handles the type of the path appropriately
            and returns a list of pairs with (path, Layer) entries
            or a PIL.Image if self.path is an image
            or None if it failed to load anything
        """
        entries = None
        if isImage(self.path):
            # got an image, load it!
            if self.archive:
                # load the image from the archive!
                log.info("Open image '%s' in archive '%s'" % (self.path, self.archive.file))
                file = self.archive.open(self.path)
                try:
                    image = Image.open(file).convert("RGB")
                    return image
                except IOError as ex:
                    log.error("Failed loading image '%s' in archive '%s'" % (self.path, self.archive.file))
                    return None
                return image
            else:
                log.info("Open image '%s' from filesystem" % self.path)
                return Image.open(self.path).convert("RGB")

        elif isZip(self.path):
            # got a zipfile, open it!
            if self.archive:
                log.info("Open zip '%s' in archive '%s'" % (self.path, self.archive.file))
                file = self.archive.open(self.path)
                archive = Zip(file)
            else:
                log.info("Open zip '%s' from filesystem" % self.path)
                archive = Zip(self.path)

            name_pairs = [(name, Layer(name, archive)) for name in archive.names if isRar(name) or isZip(name) or isImage(name)]
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

            name_pairs = [(name, Layer(name, archive)) for name in archive.names if isRar(name) or isZip(name) or isImage(name)]
            entries = dict(name_pairs)

        elif os.path.isdir(self.path):
            # load names in directory
            log.info("Open directory '%s' from filesystem" % self.path)
            dir = os.listdir(self.path)

            # save all names in directory
            name_pairs = [(d, Layer(os.path.join(self.path, d))) for d in dir if isSupportedArchive(os.path.join(self.path, d)) or isImage(d)]
            entries = dict(name_pairs)

        else:
            log.warning("Unknown file: %s" % self.path)
            return None

        return entries