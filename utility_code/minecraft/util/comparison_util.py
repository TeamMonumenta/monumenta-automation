"""A library for forced comparison results."""

class AlwaysLess():
    """Special object similar in concept to negative infinity, but without type checks."""
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __lt__(self, other):
        return True

    def __le__(self, other):
        return True

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True

    def __gt__(self, other):
        return False

    def __ge__(self, other):
        return False

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return 'AlwaysLess()'


class AlwaysEqual():
    """Special object that always matches without type checks."""
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __lt__(self, other):
        return False

    def __le__(self, other):
        return True

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __gt__(self, other):
        return False

    def __ge__(self, other):
        return True

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return 'AlwaysEqual()'


class AlwaysGreater():
    """Special object similar in concept to positive infinity, but without type checks."""
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __lt__(self, other):
        return False

    def __le__(self, other):
        return False

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True

    def __gt__(self, other):
        return True

    def __ge__(self, other):
        return True

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return 'AlwaysGreater()'

