"""A library for tracking changes over time or versions."""

class ChangelogMap(dict):
    """A map of changes over time or versions.

    >>> banana_log = ChangelogMap({AlwaysLess(): "not ripe", 22: "ripe", 24: "rotten"})
    >>> banana_log[3]
    "not ripe"
    >>> banana_log[21.9]
    "not ripe"
    >>> banana_log[22]
    "ripe"
    >>> banana_log[23]
    "ripe"
    >>> banana_log[28]
    "rotten"
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._verify_keys()

    def __getitem__(self, key):
        keys = self.keys()
        index = 0
        delta = 2**len(self).bit_length()
        while delta > 0:
            delta >>= 1
            if index + delta >= len(self):
                continue
            if keys[index + delta] <= key:
                index += delta
        return super().__getitem__(keys[index])

    def __setitem__(self, key, value):
        try:
            sorted(list(self.keys()) + [key])
        except TypeError:
            raise TypeError('Key must be comparable to existing keys in this structure.')
        super().__setitem__(key, value)

    def __delitem__(self, key):
        return super().__delitem__(key)

    def keys(self):
        return sorted(super().keys())

    def values(self):
        for key in self.keys():
            yield self[key]

    def items(self):
        for key in self.keys():
            yield (key, self[key])

    def _verify_keys(self):
        try:
            keys = self.keys()
        except TypeError:
            raise TypeError('Keys must be comparable.')
        previous_key = keys[0]
        for key in keys[1:]:
            if key == previous_key:
                raise ValueError('Keys must not be equal.')
            previous_key = key

    def __repr__(self):
        pairs = []
        for key, value in self.items():
            pairs.append(f'{key}: {value}')
        return f'ChangelogMap({{{", ".join(pairs)}}})'

