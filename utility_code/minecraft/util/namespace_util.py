#!/usr/bin/env python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from brigadier.string_reader import StringReader

class NamespacedID():
    _RE_PART = re.compile(r'''[0-9a-z_-]*''')
    _RE_NO_SEP = re.compile(r'''([0-9a-z_-]*:)?[0-9a-z_-]*''')
    _RE_PATH_DOT = re.compile(r'''([0-9a-z_-]*:)?[0-9a-z_-]*(\.[0-9a-z_-]*)*''')
    _RE_PATH_SLASH = re.compile(r'''([0-9a-z_-]*:)?[0-9a-z_-]*(/[0-9a-z_-]*)*''')

    def __init__(self, namespace, name):
        if ':' in namespace:
            raise SyntaxError('Namespace may not have a colon.')
        if ':' in name:
            raise SyntaxError('Name in namespace may not have a colon.')

        self.namespace = namespace
        self.name = name

    @classmethod
    def _parse_part(cls, text):
        """Read the regex '[0-9a-z_-]*', advancing the cursor if text is a StringReader."""
        if not isinstance(text, StringReader):
            text = StringReader(text)

        start = text.get_cursor()
        end = start + cls._RE_PART.match(text.get_remaining()).end()
        text.set_cursor(end)
        return text.get_string()[start:end]

    @staticmethod
    def parse_no_separator(text, default_namespace='minecraft'):
        """Read a namespaced ID with no path separators, ie 'minecraft:stick'."""
        if not isinstance(text, StringReader):
            text = StringReader(text)

        namespace = default_namespace
        name = NamespacedID._parse_part(text)

        if text.can_read() and text.peek() == ':':
            text.skip()
            namespace = name
            name = NamespacedID._parse_part(text)

        return NamespacedID(namespace, name)

    @staticmethod
    def parse_path_dot(text, default_namespace='minecraft'):
        """Read a namespaced ID with periods as path separators, ie 'minecraft:entity.wolf.bark'."""
        if not isinstance(text, StringReader):
            text = StringReader(text)

        namespace = default_namespace
        name = NamespacedID._parse_part(text)

        if text.can_read() and text.peek() == ':':
            text.skip()
            namespace = name
            name = NamespacedID._parse_part(text)

        while text.can_read() and text.peek() == '.':
            text.skip()
            name = f'{name}.{NamespacedID._parse_part(text)}'

        return NamespacedID(namespace, name)

    @staticmethod
    def parse_path_slash(text, default_namespace='minecraft'):
        """Read a namespaced ID with slashes as path separators, ie 'minecraft:nether/root'."""
        if not isinstance(text, StringReader):
            text = StringReader(text)

        namespace = default_namespace
        name = NamespacedID._parse_part(text)

        if text.can_read() and text.peek() == ':':
            text.skip()
            namespace = name
            name = NamespacedID._parse_part(text)

        while text.can_read() and text.peek() == '/':
            text.skip()
            name = f'{name}/{NamespacedID._parse_part(text)}'

        return NamespacedID(namespace, name)

    def __lt__(self, other):
        if isinstance(other, NamespacedID):
            raise TypeError('Cannot compare against type NamespacedID')
        if self.namespace < other.namespace:
            return True
        if self.namespace == other.namespace:
            return self.name < other.name
        return False

    def __le__(self, other):
        if isinstance(other, NamespacedID):
            raise TypeError('Cannot compare against type NamespacedID')
        if self.namespace < other.namespace:
            return True
        if self.namespace == other.namespace:
            return self.name <= other.name
        return False

    def __eq__(self, other):
        if isinstance(other, NamespacedID):
            raise TypeError('Cannot compare against type NamespacedID')
        if self.namespace != other.namespace:
            return False
        if self.name != other.name:
            return False
        return True

    def __ne__(self, other):
        if isinstance(other, NamespacedID):
            raise TypeError('Cannot compare against type NamespacedID')
        if self.namespace != other.namespace:
            return True
        if self.name != other.name:
            return True
        return False

    def __gt__(self, other):
        if isinstance(other, NamespacedID):
            raise TypeError('Cannot compare against type NamespacedID')
        if self.namespace > other.namespace:
            return True
        if self.namespace == other.namespace:
            return self.name > other.name
        return False

    def __ge__(self, other):
        if isinstance(other, NamespacedID):
            raise TypeError('Cannot compare against type NamespacedID')
        if self.namespace > other.namespace:
            return True
        if self.namespace == other.namespace:
            return self.name >= other.name
        return False

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return f'{self.namespace}:{self.name}'

    def __repr__(self):
        return f'NamespacedID({str(self)!r})'

