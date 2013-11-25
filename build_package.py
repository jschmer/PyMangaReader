import shutil, os, sys, re
from compile_ui import compileUIFiles
from setup import build
from get_latest_git_tag import generateVersionForCurrentCommit
from tempfile import mkstemp
from shutil import move
from os import remove, close
import zipfile

# zipping an entire directory
def zipdir(path, zip):
    for root, dirs, files in os.walk(path):
        for file in files:
            zip.write(os.path.join(root, file))

# architecture string mappings for package name
X64 = 0
X86 = 1
arch = {
  X64: "x64",
  X86: "x86"
}

# platform string mappings for package name
WIN = 10
LINUX = 11
platform = {
  WIN: "win",
  LINUX: "linux"
}

def generateVersionForGUI(version_string):
  # version template file
  version_template = "version.template"
  
  # output version python file
  version_py = "version.py"

  new_file = open(version_py, 'w')
  old_file = open(version_template)
  
  for line in old_file:
    new_file.write(re.sub(r"^FULL_VERSION=.*", 'FULL_VERSION="%s"' % version_string , line))
  
  # close files
  new_file.close()
  old_file.close()
 

def buildPackage():
  version = generateVersionForCurrentCommit()

  generateVersionForGUI(version)
  
  # compile Qt ui and resource files
  compileUIFiles()

  # build the package with cx_freeze
  build(cmd="build", ver=version)

  # got to build folder
  os.chdir("build")

  # determine cx_freeze output folder
  is_64bits = sys.maxsize > 2**32
  platform_str = None
  arch_str = None
  package_arch = None
  package_platform = None
  if sys.platform == "win32":
    package_platform = platform[WIN]
    if is_64bits:
      arch_str = "amd64"
      platform_str = "win"
      package_arch = arch[X64]
    else:
      arch_str = ""
      platform_str = "win32"
      package_arch = arch[X86]
  elif sys.platform == "linux":
    package_platform = platform[LINUX]
    if is_64bits:
      arch_str = "x86_64"
      package_arch = arch[X64]
    else:
      arch_str = "i686"
      package_arch = arch[X86]
    platform_str = "linux"
  else:
    print("Unsopported platform:", sys.platform)
    exit(-1)

  if arch_str != "":
    arch_desc = platform_str + "-" + arch_str
  else:
    arch_desc = platform_str

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
  #    exe.win-amd64-3.3 -> PyMangaReader.[win|linux]-[x86|x64].[vX.Y]

  package_name = os.path.abspath("PyMangaReader." + package_platform + "-" + package_arch + "." + version)
  if os.path.exists(package_name):
    shutil.rmtree(package_name)

  print("Rename directory to", package_name)
  os.rename(freeze_build_output, package_name)

  if sys.platform == "win32":
    # copy files in build/win-additional-deps to output folder
    print("Copy win32 dependencies...")
    root = None
    if is_64bits:
      root = os.path.abspath('win-additional-deps/x64/')
    else:
      root = os.path.abspath('win-additional-deps/x86/')

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
  # this would otherwise break the build() step
  sys.argv = [x for x in sys.argv if "log" not in x]
  buildPackage()
  print("Done.")