# This is a simple "port" of PIL.ImageQt to PyQt5
from PIL import Image
from PIL._util import isPath

from PyQt5.QtGui import QImage, qRgb

##
# (Internal) Turns an RGB color into a Qt compatible color integer.

def rgb(r, g, b):
    # use qRgb to pack the colors, and then turn the resulting long
    # into a negative integer with the same bitpattern.
    return (qRgb(r, g, b) & 0xffffff) - 0x1000000

##
# An PIL image wrapper for Qt.  This is a subclass of PyQt5's QImage
# class.
#
# @param im A PIL Image object, or a file name (given either as Python
#     string or a PyQt string object).

class ImageQt(QImage):
    def __init__(self, im):

        data = None
        colortable = None

        # handle filename, if given instead of image name
        if hasattr(im, "toUtf8"):
            # FIXME - is this really the best way to do this?
            im = unicode(im.toUtf8(), "utf-8")
        if isPath(im):
            im = Image.open(im)

        if im.mode == "1":
            format = QImage.Format_Mono
        elif im.mode == "L":
            format = QImage.Format_Indexed8
            colortable = []
            for i in range(256):
                colortable.append(rgb(i, i, i))
        elif im.mode == "P":
            format = QImage.Format_Indexed8
            colortable = []
            palette = im.getpalette()
            for i in range(0, len(palette), 3):
                colortable.append(rgb(*palette[i:i+3]))
        elif im.mode == "RGB":
            data = im.tobytes("raw", "BGRX")
            format = QImage.Format_RGB32
        elif im.mode == "RGBA":
            try:
                data = im.tobytes("raw", "BGRA")
            except SystemError:
                # workaround for earlier versions
                r, g, b, a = im.split()
                im = Image.merge("RGBA", (b, g, r, a))
            format = QImage.Format_ARGB32
        else:
            raise ValueError("unsupported image mode %r" % im.mode)

        # must keep a reference, or Qt will crash!
        self.__data = data or im.tobytes()

        QImage.__init__(self, self.__data, im.size[0], im.size[1], format)

        if colortable:
            self.setColorTable(colortable)
