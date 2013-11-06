import os
import sys
import PyQt5.uic
import subprocess

# ui files
PyQt5.uic.compileUiDir(".", recurse=True)

# qrc files
out = subprocess.check_output("C:\Py\Python33\Lib\site-packages\PyQt5\pyrcc5.exe images_res.qrc")
#print(out)
#out = out.decode('utf-8')
f = open("images_res_rc.py", "wb")
f.write(out)