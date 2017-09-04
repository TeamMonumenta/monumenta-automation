# Edited pymclevel from pymclevel

This is a fork of https://github.com/Khroki/pymclevel, part of MCEdit made available for scripting purposes.

This folder has been renamed to mclevel and is expected to be moved or linked to at ~/.local/lib/python2.7/site-packages/mclevel. If linked, the original folder can be left with its current name.
Having the folder named ~/.local/lib/python2.7/site-packages/mclevel means that within Python, running "from mclevel import whatever" grabs ~/.local/lib/python2.7/site-packages/mclevel/whatever.py, and matches formatting I've seen elsewhere with Python.

Please note that this version is out of date, but working. As of when this was forked, the current version of pymclevel was non-functional (crash, missing libraries, etc). This may be updated if pymclevel's repository gets fixed.

The following files were added or edited:

```
added:
README.md - describing my changes and reasoning
materials/ - because if I can convert minecraft.yaml to a .py file and not need the one and only yaml file, it'll be nice.
*.pyc because .gitignore is ignoring my rule about *.pyc files

changed:
minecraft.yaml - added blocks that were not in this version
nbt.py - adding json string support (not yet complete)

todo:
_nbt.pyx - is unchanged, faster version of nbt.py that is loaded if possible
```

Also note that I don't know how to properly fork a repository yet, so I cloned the repository and copied the files. Probably not the right way, but good enough for now.

