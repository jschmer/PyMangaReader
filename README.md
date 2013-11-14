PyMangaReader
=============

Lightweight reader for mangas.
Reads images (manga pages) from directories, zips and rars (only if the UnRAR utility is provided).
Supported image formats are jpg and png.

### Dependencies
[Python3] and [PyQt5]  
If you want to read rar archives you need the [UnRAR] utility

### Features
- Configurable base directories to read mangas from
- Adjustable settings path for storing manga specific settings for easy synchronisation
- Remembers last opened manga/volume/chapter/page between application launches to continue reading where you left off
- Fullscreen mode
- Rotate image by 90° in either direction

Works best with following directory/archive hierarchy:
```
MangaName (directory)
|- Volume 1 (dir or archive)
|  |- chapter 1 (dir or archive)
|  |  |- Page 1 (image)
|  |  |- Page ... (image)
|  |- chapter ...
|- Volume ...
```

[Python3]: http://www.python.org/
[PyQt5]: http://www.riverbankcomputing.co.uk/software/pyqt/download5
[UnRAR]: http://www.rarlab.com/rar_add.htm
