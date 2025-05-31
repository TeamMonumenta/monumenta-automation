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
        if not Path(p).exists():
            print(f"Creating {p}")
            os.makedirs(p, exist_ok=True)

        for jar in list(Path(os.path.join(src, dir)).glob("*.jar")):
            if "-" not in jar.name:
                shutil.copy(jar, p)
                print(jar.name)

    data_include = [
        "server_config_template"
    ]

    if not Path(os.path.join(dst, "data")).exists():
        os.makedirs(os.path.join(dst, "data"), exist_ok=True)

    for item in data_include:
        shutil.copytree(
            os.path.join(src, "data", item),
            os.path.join(dst, "data", item),
            dirs_exist_ok=True
        )
        print(item)

    data_plugins_all_include = [
        "dynmap",
        "goPaint",
        "goBrush",
        "LibraryOfSouls",
        "Monumenta",
        "ChestSort",
        "MonumentaNetworkChat"
    ]

    if not Path(os.path.join(dst, "data/plugins/all")).exists():
        os.makedirs(os.path.join(dst, "data/plugins/all"), exist_ok=True)   

    for item in data_plugins_all_include:
        shutil.copytree(
            os.path.join(src, "data/plugins/all", item),
            os.path.join(dst, "data/plugins/all", item),
            dirs_exist_ok=True
        )
        print(item)

if __name__ == "__main__":
    main()