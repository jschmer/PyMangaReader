import sys
from cx_Freeze import setup, Executable

def build(cmd = None, ver = None):
  if cmd:
    sys.argv.append(cmd)
  #print(sys.argv)

  # see http://cx-freeze.readthedocs.org/en/latest/distutils.html
  base = None
  if sys.platform == "win32":
      base = "Win32GUI"

  setup(  name = "PyMangaReader",
          version = ver,
          description = "PyMangaReader",
          executables = [Executable("PyMangaReader.pyw", base=base)])
        
if __name__ == '__main__':
  build()
  print("Done.")