import PyQt5.uic
import subprocess

def compileUIFiles():
  print("Compiling *.ui files...")

  # compile ui files
  PyQt5.uic.compileUiDir(".", recurse=True)

  # compile qrc files
  print("Compiling *.qrc files...")
  out = subprocess.check_output(["pyrcc5", "images_res.qrc"])
  f = open("images_res_rc.py", "wb")
  f.write(out)

if __name__ == '__main__':
  compileUIFiles()
  print("Done.")