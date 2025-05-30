import shutil
import os
from pathlib import Path

def main():
    src = os.path.expanduser("~/project_epic/server_config")
    dst = os.path.expanduser(os.path.join(os.getcwd(), "server_config"))

    for jar in list(Path(src).glob("*.jar")):
        if "-" not in jar.name:
            shutil.copy(jar, dst)
            print(f"Copied {jar} to {dst}")
    
    for jar in list(Path(os.path.join(src, 'plugins')).glob("*.jar")):
        if "-" not in jar.name:
            shutil.copy(jar, os.path.join(dst, 'plugins'))
            print(f"Copied {jar} to {os.path.join(dst, 'plugins')}")
    
if __name__ == "__main__":
    main()