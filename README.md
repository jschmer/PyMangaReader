PyMangaReader
=============

Simple reader for mangas.
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
but can also handle shallower hierarchies.

### Building
Checkout the repository, launch compile_ui.py to compile Qt designer and resource files to python and run `python PyMangaReader.pyw`.

To generate a native package with all dependencies, install [cx_Freeze] and run `python setup.py build`
NOTE: If you happen to encounter an error launching PyMangaReader with a generated package saying that Qt can't find a platform plugin, make sure that the library `libEGL.dll` is there!


[Python3]: http://www.python.org/
[PyQt5]: http://www.riverbankcomputing.co.uk/software/pyqt/download5
[UnRAR]: http://www.rarlab.com/rar_add.htm
[cx_Freeze]: http://cx-freeze.readthedocs.org/en/latest/index.html
