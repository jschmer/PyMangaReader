import os
import zipfile
import re
from PyQt5.QtGui import QImage

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
        self.load(file)
        pass

    def load(self, file):
        if not os.path.isfile(file):
            raise RuntimeError("%s is not a zipfile!" % file)
        self.zf = zipfile.ZipFile(file, "r")

        self.names = self.zf.namelist()

    def open(self, name):
        return self.zf.open(name, "r")


class Layer():
    """
    Generic Layer that provides a consistent view for archives and directories
    """
    supported_archives = [".zip"]
    names = None
    path = None
    zip = None
    image = None

    def __init__(self, _path, _zip = None):
        self.zip = _zip
        self.path = _path
        
    def open(self):
        # if path is directory
        if os.path.isdir(self.path):
            # load names in directory
            dir = os.listdir(self.path)
            self.names = []
            for d in dir:
                #if isSupportedArchive(d):
                self.names.append((d, Layer(os.path.join(self.path, d))))
            self.names = dict(self.names)
            pass

        elif ".zip" in self.path:
            # load archive and names
            self.zip = Zip(self.path)
            names = self.zip.names

            # throw out deep files, we use only top level files
            # TODO: if only one directory then recurse into it
            self.names = []
            #pattern = re.compile("[\\/].")
            for name in names:
                #if not pattern.search(name):
                    self.names.append( (name, Layer(name, self.zip)) )
                
            #self.names = []
            #for name in names:
            #    self.names.append( (name, Layer(name, self.zip)) )

            self.names = dict(self.names)
            pass
        else:
            if self.zip:
                # got an image, load the image from the zip!
                if isImage(self.path):
                    #print("image! :C", self.path)
                    file = self.zip.open(self.path)
                    self.image = QImage()
                    if not self.image.loadFromData(file.read()):
                        self.image = None
                else:
                    #print("archive dir! :C", self.path)

                    # got a directory in an archive
                    # list all names under path
                    names = self.zip.names

                    self.names = []
                    for name in names:
                        if self.path in name and len(self.path) != len(name):
                            self.names.append( (name, Layer(name, self.zip)) )

                    self.names = dict(self.names)

            else:
                self.image = QImage(self.path)

        return self