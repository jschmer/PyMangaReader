import subprocess, re, sys

def getLatestGitTag():
  out = subprocess.check_output(["git", "describe", "--abbrev=0", "--tags"])
  out = out.decode("utf-8")
  out = out.replace("\n", "").replace("\r", "")
  return out

def generateVersionForCurrentCommit():
  out = subprocess.check_output(["git", "describe", "--tags"])
  out = out.decode("utf-8")
  out = out.replace("\n", "").replace("\r", "")

  match = re.match(r"^(v[0-9\.]+)$", out)
  if match:
    return(match.group(1))
  else:
    match = re.match(r"^v([0-9]+)\.([0-9]+)-([0-9]+)", out)

    if match:
      major = int(match.group(1))
      minor = int(match.group(2)) + 1
      commits_ahead = int(match.group(3))


      temp_version_string = "v%d.%d-preview%d" % (major, minor, commits_ahead)
      return (temp_version_string, "%d.%d.%d" % (major, minor, commits_ahead))

    else:
      print("Failed to extract version from", out)
      sys.exit(-1)

if __name__ == '__main__':
  print("Latest tag:", getLatestGitTag())
  print("Version:",generateVersionForCurrentCommit())