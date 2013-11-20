import subprocess

def getLatestGitTag():
  out = subprocess.check_output(["git", "describe", "--abbrev=0", "--tags"])
  out = out.decode("utf-8")
  out = out.replace("\n", "").replace("\r", "")
  return out

if __name__ == '__main__':
  print(getLatestGitTag())