import PyQt5.uic
import subprocess

# compile ui files
PyQt5.uic.compileUiDir(".", recurse=True)

# compile qrc files
out = subprocess.check_output(["pyrcc5", "images_res.qrc"])
f = open("images_res_rc.py", "wb")
f.write(out)