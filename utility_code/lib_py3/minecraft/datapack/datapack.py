#!/usr/bin/env python3

"""A library to process datapack information.

Datapack handles a single datapack.
DatapackNamespace handles a namespace within a datapack.
LoadedDatapacks handles multiple datapacks as handled by a world.
"""

import json
import os
import re
import sys

valid_namespace_re = re.compile(r"""^[-_0-9a-z]+$""")
valid_namespace_path_re = re.compile(r"""^[-_0-9a-z/]+$""")

class DatapackNamespace(object):
    """A namespace within a datapack."""
    def __init__(self, namespace, folder):
        """Load a namespace in a datapack."""
        if not valid_namespace_re.match(namespace):
            raise SyntaxError("namespace may only contain [-_0-9a-z]")

        self.namespace = namespace
        self.folder = folder

    def advancements(self, inner_path=''):
        """Iterator for advancements in this namespace.

        If inner_path is specified, yields only within that path.
        If not specified, iterates over all results.
        """
        for result_inner_path in self._find_paths("advancements", ".json", inner_path):
            # TODO actually load advancement
            yield result_inner_path

    def functions(self, inner_path=''):
        """Iterator for functions in this namespace.

        If inner_path is specified, yields only within that path.
        If not specified, iterates over all results.
        """
        for result_inner_path in self._find_paths("functions", ".mcfunction", inner_path):
            # TODO actually load function
            yield result_inner_path

    def loot_tables(self, inner_path=''):
        """Iterator for loot tables in this namespace.

        If inner_path is specified, yields only within that path.
        If not specified, iterates over all results.
        """
        for result_inner_path in self._find_paths("loot_tables", ".json", inner_path):
            # TODO actually load loot table
            yield result_inner_path

    def recipes(self, inner_path=''):
        """Iterator for recipes in this namespace.

        If inner_path is specified, yields only within that path.
        If not specified, iterates over all results.
        """
        for result_inner_path in self._find_paths("recipes", ".json", inner_path):
            # TODO actually load recipes
            yield result_inner_path

    def structures(self, inner_path=''):
        """Iterator for structures in this namespace.

        If inner_path is specified, yields only within that path.
        If not specified, iterates over all results.
        """
        for result_inner_path in self._find_paths("structures", ".nbt", inner_path):
            # TODO actually load structures
            yield result_inner_path

    def block_tags(self, inner_path=''):
        """Iterator for block tags in this namespace.

        If inner_path is specified, yields only within that path.
        If not specified, iterates over all results.
        """
        for result_inner_path in self._find_paths(os.path.join("tags", "blocks"), ".json", inner_path):
            # TODO actually load block tags
            yield result_inner_path

    def entity_tags(self, inner_path=''):
        """Iterator for entity tags in this namespace.

        If inner_path is specified, yields only within that path.
        If not specified, iterates over all results.
        """
        for result_inner_path in self._find_paths(os.path.join("tags", "entity_types"), ".json", inner_path):
            # TODO actually load entity tags
            yield result_inner_path

    def fluid_tags(self, inner_path=''):
        """Iterator for fluid tags in this namespace.

        If inner_path is specified, yields only within that path.
        If not specified, iterates over all results.
        """
        for result_inner_path in self._find_paths(os.path.join("tags", "fluids"), ".json", inner_path):
            # TODO actually load fluid tags
            yield result_inner_path

    def function_tags(self, inner_path=''):
        """Iterator for function tags in this namespace.

        If inner_path is specified, yields only within that path.
        If not specified, iterates over all results.
        """
        for result_inner_path in self._find_paths(os.path.join("tags", "functions"), ".json", inner_path):
            # TODO actually load function tags
            yield result_inner_path

    def item_tags(self, inner_path=''):
        """Iterator for item tags in this namespace.

        If inner_path is specified, yields only within that path.
        If not specified, iterates over all results.
        """
        for result_inner_path in self._find_paths(os.path.join("tags", "items"), ".json", inner_path):
            # TODO actually load item tags
            yield result_inner_path

    def _find_paths(self, category, extension, inner_path=""):
        """Returns possible loot table paths.

        category must be one of these:
        (
            "advancements",
            "functions",
            "loot_tables",
            "recipes",
            "structures",
            os.path.join("tags", "blocks"),
            os.path.join("tags", "entity_types"),
            os.path.join("tags", "fluids"),
            os.path.join("tags", "functions"),
            os.path.join("tags", "items"),
        )

        extension must be the appropriate
        file extension for the category,
        including the "."
        """

        file_path = os.path.join(self.folder, category, inner_path)

        if os.path.isdir(file_path):
            for child in os.listdir(file_path):
                for child_path in self._find_paths(
                    category,
                    extension,
                    os.path.join(inner_path, child)
                ):
                    yield child_path
            raise StopIteration

        if not os.path.isfile(file_path):
            raise StopIteration

        if not file_path.endswith(extension):
            raise StopIteration

        inner_path_sans_ext = inner_path[:0 - len(extension)]
        file_id = self.namespace + ":" + inner_path_sans_ext.replace(os.sep, "/")

        if not valid_namespace_path_re.match(inner_path_sans_ext):
            raise StopIteration

        yield inner_path

    def __repr__(self):
        return "DatapackNamespace({!r}, {!r})".format(self.namespace, self.folder)


class Datapack(object):
    """A class to identify datapack folders and their contents."""
    def __init__(self, datapack_id, datapack_folder):
        """Load a datapack from a folder.

        datapack_id is the same as with /datapacks, ie "file/spam".
        datapack_folder is the folder the datapack is located in.

        To read a zipped datapack, it must be extracted to a
        temporary folder. This also works with the default
        datapack if an appropriate vanilla jar is extracted.
        """
        self.id = datapack_id
        self.folder = datapack_folder
        self._read_pack_mcmeta()
        self._get_namespaces()

    def _read_pack_mcmeta(self):
        with open(os.path.join(self.folder, "pack.mcmeta")) as meta_fp:
            meta_json = json.load(meta_fp)
            self.pack_version = meta_json["pack"]["pack_format"]
            self.description = meta_json["pack"]["description"]
            meta_fp.close()

    def _get_namespaces(self):
        self.namespaces = {}
        data_dir = os.path.join(self.folder, "data")
        for namespace in os.listdir(data_dir):
            self._parse_namespace(namespace)

    def _parse_namespace(self, namespace):
        folder = os.path.join(self.folder, "data", namespace)
        if not os.path.isdir(folder):
            return

        try:
            self.namespaces[namespace] = DatapackNamespace(namespace, folder)
        except Exception:
            pass

    def __repr__(self):
        return "Datapack({!r}, {!r})".format(self.id, self.folder)


class LoadedDatapacks(object):
    """A class to observe datapacks in a world.

    This should be added to the World class later,
    but exists here for testing.

    May wind up as a separate class that is
    loaded by the World class.
    """
    def __init__(self, datapacks_folder, enabled_datapacks):
        """Read enabled the datapacks for a world.

        The "world" may be real or simulated here.
        """
        self.datapacks_folder = datapacks_folder
        self.enabled_datapacks = enabled_datapacks
        # TODO find datapacks

    def find_datapacks(self):
        NotImplemented

    def __repr__(self):
        return "LoadedDatapacks({!r}, {!r})".format(self.datapacks_folder, self.enabled_datapacks)

