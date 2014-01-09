Build PyMangaReader
===================

## Dependencies
[Python3], [PyQt5], [rarfile] and [Pillow]
If you want to read rar archives you also need the [UnRAR] utility

### Building
Checkout the repository, launch compile_ui.py to compile Qt designer and resource files to python and run `python PyMangaReader.pyw`.

To generate a native package with all dependencies, install [cx_Freeze] and run `python build_package.py`   
You'll get a zip archive with reasonable name taken from the last git tag and the architecture you are on. Example: `PyMangaReader.win-x64.v0.3-preview13.zip`  
cx_Freeze can't always find all dependencies if Python modules are installed as eggs, therefore the resulting package may not be standalone launchable.

[Python3]: http://www.python.org/
[PyQt5]: http://www.riverbankcomputing.co.uk/software/pyqt/download5
[rarfile]: https://pypi.python.org/pypi/rarfile/
[UnRAR]: http://www.rarlab.com/rar_add.htm
[cx_Freeze]: http://cx-freeze.readthedocs.org/en/latest/index.html
[Pillow]: https://pypi.python.org/pypi/Pillow/2.0.0