import PyQt5.uic
import subprocess

# compile ui files
PyQt5.uic.compileUiDir(".", recurse=True)

# compile qrc files
out = subprocess.check_output("C:\Py\Python33\Lib\site-packages\PyQt5\pyrcc5.exe images_res.qrc")
f = open("images_res_rc.py", "wb")
f.write(out)