import sys
from cx_Freeze import setup, Executable

# see http://cx-freeze.readthedocs.org/en/latest/distutils.html

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "PyMangaReader",
        version = "0.1",
        description = "PyMangaReader",
        executables = [Executable("PyMangaReader.pyw", base=base)])