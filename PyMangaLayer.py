import os
import zipfile
import re

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

class Zip(object):
    zipfile = None

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


class Layer():
    """
    Generic Layer that provides a consistent view for archives, directories, files
    """
    path  = None # path to the archive
    names = None # for archive names
    zip   = None # cache for the opened zip
    image = None # in case we hit an image

    def __init__(self, _path, _zip = None):
        self.zip  = _zip
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
                self.names.append( (name, Layer(name, self.zip)) )
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
                            self.names.append( (name, Layer(name, self.zip)) )

                    self.names = dict(self.names)

            elif isImage(self.path):
                self.image = QImage(self.path)

            else:
                log.warning("Unknown file: %s" % self.path)

        return self