import shutil
import os
from pathlib import Path

def main():
    src = os.path.expanduser("~/project_epic/server_config")
    dst = os.path.expanduser(os.path.join(os.getcwd(), "server_config"))

    jar_dir = [
        ".",
        "plugins",
        "mods"
    ]
    for dir in jar_dir:

        p = os.path.join(dst, dir)
        if not p.exists():
            os.makedirs(p, exist_ok=True)

        for jar in list(Path(os.path.join(src, dir)).glob("*.jar")):
            if "-" not in jar.name:
                shutil.copy(jar, p)
                print(f"Copied {jar} to {p}")

    data_include = [
        "server_config_template"
    ]

    for item in data_include:
        shutil.copytree(
            os.path.join(src, "data", item),
            os.path.join(dst, "data", item),
            dirs_exist_ok=True
        )
    
if __name__ == "__main__":
    main()