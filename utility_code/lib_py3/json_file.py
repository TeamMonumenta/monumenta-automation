# Don't rename this to json.py - it'll break things

import json
from collections import OrderedDict

from lib_py3.common import eprint

class jsonFile():
    """
    A json utility for json files;

    NOTE:
    Do NOT use for NBT json strings! It will not work!
    NBT json is less strict than this utility allows.

    If you want to parse or save nbt json within a json
    file, store the nbt json as a string and use the nbt
    library's json functions.
    """
    def __init__(self, path=None):
        """
        read a file as json; edit self.dict
        if no path is provided, it will create
        an empty dictionary to be saved later
        """
        self.path = path
        if path is None:
            self.dict = {}
            return
        with open(path, 'r', encoding='utf-8-sig') as fp:
            try:
                self.dict = json.load(fp, object_pairs_hook=OrderedDict)
            except Exception:
                eprint("Error loading {!r}:".format(path))
                raise
            fp.close()

    def save(self, path=None, indent=2, separators=(',', ': '), sort_keys=False):
        """
        save a json file; defaults to original location
        """
        if path is None:
            path = self.path
            if path is None:
                raise TypeError("Path not specified for json file")
        with open(path, 'w', encoding='utf-8') as fp:
            json.dump(
                self.dict,
                fp,
                ensure_ascii=False,
                indent=indent,
                separators=separators,
                sort_keys=sort_keys
            )
            fp.write("\n")
            fp.close()
