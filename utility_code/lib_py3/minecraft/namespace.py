#!/usr/bin/env python3

import copy
import re

valid_namespace_re = re.compile(r"""^[-_0-9a-z]+$""")
valid_namespace_path_re = re.compile(r"""^[-_0-9a-z/]+$""")

class Namespace(object):
    def __init__(self, other):
        if isinstance(other, type(self)):
            self.namespace = other.namespace
            self.contents = copy.deepcopy(other.contents)

        elif isinstance(other, str):
            if not valid_namespace_re.match(other):
                

            self.namespace = other
            self.contents = {}

        else:
            raise TypeError()

class NamespacedId(object):
    def __init__(self, other):
        """Load from another NamespacedId."""
        if isinstance(other, type(self)):
            self.namespace = other.namespace
            self.key = other.key

        elif isinstance(other, str):
            parts = other.split(":")
            if len(parts) > 2:
                raise ValueError("other may only contain one ':'.")

            elif len(parts) == 2:
                self.namespace, self.key = parts
                if not valid_namespace_re.match(self.namespace):
                    raise SyntaxError("namespace may only contain [-_0-9a-z]")

                if not valid_namespace_path_re.match(self.key):
                    raise SyntaxError("namespace may only contain [-_0-9a-z/]")

            else:
                # 1 Part with no namespace
                # Assume the namespace is `minecraft`
                self.namespace = "minecraft"

                self.key = parts[0]
                if not valid_namespace_path_re.match(self.key):
                    raise SyntaxError("namespace may only contain [-_0-9a-z/]")

        else:
            raise TypeError()

    @classmethod
    def from_pair(cls, namespace, key):
        """Load as a namespace-key pair."""
        if not valid_namespace_re.match(namespace):
            raise SyntaxError("namespace may only contain [-_0-9a-z]")

        if not valid_namespace_path_re.match(key):
            raise SyntaxError("namespace may only contain [-_0-9a-z/]")

        self.namespace = namespace
        self.key = key

    def to_pair(self):
        return (self.namespace, self.key)

    def __str__(self):
        return self.namespace + ":" + self.key

    def __repr__(self):
        return "NamespacedId.from_pair({!r}, {!r})".format(self.namespace, self.key)

