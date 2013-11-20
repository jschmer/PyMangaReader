import shutil, os, sys, re
from compile_ui import compileUIFiles
from setup import build
from get_latest_git_tag import getLatestGitTag
import zipfile

# zipping an entire directory
def zipdir(path, zip):
    for root, dirs, files in os.walk(path):
        for file in files:
            zip.write(os.path.join(root, file))

def buildPackage():
  version = getLatestGitTag()

  # compile Qt ui and resource files
  compileUIFiles()

  # build the package with cx_freeze
  build(cmd="build", ver=version)

  # got to build folder
  os.chdir("build")

  # determine cx_freeze output folder
  platforms = {
               "win32" : "win",
               "linux2" : "linux"
              }

  is_64bits = sys.maxsize > 2**32
  arch = None
  if is_64bits:
    arch = "amd64"
  else:
    arch = "i686"

  arch_desc = platforms[sys.platform] + "-" + arch

  freeze_build_output = os.path.abspath("exe." + arch_desc + "-3.3")
  if not os.path.exists(freeze_build_output):
    print("ERROR: Can't determine cx_freeze build output path!\nGuess was", freeze_build_output)

  # copy READMEs to build output
  root = ".."
  for file in os.listdir(root):
    if file.endswith(".md"):
      src = os.path.abspath(os.path.join(root, file))
      shutil.copy(src, freeze_build_output)
  
  # rename build folder to something more sane 
  #    exe.win-amd64-3.3 -> PyMangaReader.win-amd64.v0.2
  package_name = os.path.abspath("PyMangaReader." + arch_desc + "." + version)
  if os.path.exists(package_name):
    shutil.rmtree(package_name)

  print("Rename directory to", package_name)
  os.rename(freeze_build_output, package_name)

  if sys.platform == "win32":
    # copy files in build/win-x64-additional-deps to output folder
    print("Copy win32 dependencies...")
    root = os.path.abspath('win-x64-additional-deps')
    for file in os.listdir(root):
      src = os.path.join(root, file)
      shutil.copy(src, package_name)

  # zip up the folder
  print("Zip up package", package_name+'.zip')
  zip = zipfile.ZipFile(package_name+'.zip', 'w', zipfile.ZIP_DEFLATED)
  zipdir(os.path.basename(package_name), zip)
  zip.close()

if __name__ == '__main__':
  print("Building package...")
  # strip out log parameter in debug version of VS (so i don't have to remove it everytime i want to build a package)
  sys.argv = [x for x in sys.argv if "log" not in x]
  buildPackage()
  print("Done.")