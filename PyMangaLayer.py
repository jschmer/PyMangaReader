import os
import zipfile
import re
import rarfile

from PyQt5.QtGui import QImage
from PyMangaLogger import log

supported_archives = ["", ".zip"]
def isSupportedArchive(file):
    fileName, fileExtension = os.path.splitext(file)
    if fileExtension not in supported_archives:
        return False
    return True

supported_images = [".png", ".jpg"]
def isImage(file):
    fileName, fileExtension = os.path.splitext(file)
    if fileExtension in supported_images:
        return True
    return False

# UnRAR stuff
rarfile.UNRAR_TOOL = "unrar"
rarfile.PATH_SEP = '\\'

def isRARactive():
    global supported_archives
    return "*.rar" in supported_archives

def setupUnrar(unrar_path):
    global supported_archives
    unrar = which(unrar_path)
    if unrar is None:
        log.warning("UnRAR executable not accessible: %s" % unrar_path)
        log.warning("Disabling rar archive support...")
        supported_archives = [x for x in supported_archives if x != "*.rar"]
    else:
        log.info("UnRAR executable accessible: %s" % unrar)
        log.info("Enabling rar archive support...")
        rarfile.UNRAR_TOOL = unrar
        if "*.rar" not in supported_archives:
            supported_archives.append("*.rar")

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
    zf = None

    def __init__(self, file):
        """ open zip archive pointed to by file """
        self.load(file)

    def load(self, file):
        """ open zip archive pointed to by file """
        if not os.path.isfile(file):
            raise RuntimeError("%s is not a zipfile!" % file)
        self.zf = zipfile.ZipFile(file, "r")

        self.names = self.zf.namelist()

    def open(self, name):
        return self.zf.open(name, "r")

class Rar(object):
    rf = None

    def __init__(self, file):
        """ open zip archive pointed to by file """
        self.load(file)

    def load(self, file):
        """ open zip archive pointed to by file """
        if not os.path.isfile(file):
            raise RuntimeError("%s is not a zipfile!" % file)
        self.rf = rarfile.RarFile(file, "r")

        self.names = self.rf.namelist()

    def open(self, name):
        return self.rf.open(name, "r")


class Layer():
    """
    Generic Layer that provides a consistent view for archives, directories, files
    """
    path  = None # path to the archive
    names = None # for archive names
    zip   = None # cache for an opened zip
    rar   = None # cache for an opened rar
    image = None # in case we hit an image

    def __init__(self, _path, _zip = None, _rar = None):
        self.zip  = _zip
        self.rar  = _rar
        self.path = _path
        
    def open(self):
        """
        Opens the path the layer was constructed with
        Handles the type of the path appropriately
        """
        if os.path.isdir(self.path):
            # load names in directory
            dir = os.listdir(self.path)

            # save all names in directory
            self.names = []
            for d in dir:
                self.names.append((d, Layer(os.path.join(self.path, d))))
            self.names = dict(self.names)

        elif ".zip" in self.path:
            # load archive and its content names
            self.zip = Zip(self.path)
            names = self.zip.names

            self.names = []
            for name in names:
                self.names.append( (name, Layer(name, self.zip, self.rar)) )
            self.names = dict(self.names)

        elif isRARactive() and ".rar" in self.path:
            # load archive and its content names
            self.rar = Rar(self.path)
            names = self.rar.names

            self.names = []
            for name in names:
                self.names.append( (name, Layer(name, self.zip, self.rar)) )
            self.names = dict(self.names)

        else:
            # no directory, no zip: are we already inside a zip?
            if self.zip:
                # we are already inside a zip
                if isImage(self.path):
                    # got an image, load the image from the zip!
                    file = self.zip.open(self.path)
                    self.image = QImage()
                    if not self.image.loadFromData(file.read()):
                        self.image = None
                else:
                    # got a directory in an archive, list all names under path
                    names = self.zip.names

                    self.names = []
                    for name in names:
                         # make sure we only get subpaths and not the current path
                        if self.path in name and len(self.path) != len(name):
                            self.names.append( (name, Layer(name, self.zip, self.rar)) )

                    self.names = dict(self.names)

            if isRARactive() and self.rar:
                # we are already inside a rar
                if isImage(self.path):
                    # got an image, load the image from the zip!
                    file = self.rar.open(self.path)
                    self.image = QImage()
                    if not self.image.loadFromData(file.read()):
                        self.image = None
                else:
                    # got a directory in an archive, list all names under path
                    names = self.rar.names

                    self.names = []
                    for name in names:
                         # make sure we only get subpaths and not the current path
                        if self.path in name and len(self.path) != len(name):
                            self.names.append( (name, Layer(name, self.rar, self.rar)) )

                    self.names = dict(self.names)

            elif isImage(self.path):
                self.image = QImage(self.path)

            else:
                log.warning("Unknown file: %s" % self.path)

        return self