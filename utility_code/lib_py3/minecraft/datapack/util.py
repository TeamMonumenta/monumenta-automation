#!/usr/bin/env python3

import copy
import random

class OrderedSet(list):
    """A list with no more than one of each element."""
    def __init__(self, *args):
        print(args)
        if len(args) == 0:
            pass

        elif (
            len(args) == 1
            and '__iter__' in dir(args[0])
            and not isinstance(args[0], str)
        ):
            for item in args[0]:
                self.append(item)

        else:
            for item in args:
                self.append(item)


    def append(self, value):
        if value in self:
            return
        list.append(self, value)


    def __setitem__(self, index, value):
        if value in self:
            return
        list.__setitem__(self, index, value)


    def __repr__(self):
        return "OrderedSet({})".format(list.__repr__(self))


class GetNumberOrRandom(object):
    """Return a fixed or random number based on "other".

    other should be an integer, float, or dict.

    If other is an integer or float, that value is returned.

    If other is a dict, it must have the keys "min" and "max",
    and a random number is returned in that inclusive range.

    If rand_float is True, random numbers will be floats.
    If it is False, random numbers will be ints.

    Call the resulting object as a function with no arguements for a result.
    """
    def __init__(self, other, rand_float=True):
        """Return a fixed or random number based on "other".

        other should be an integer, float, or dict.

        If other is an integer or float, that value is returned.

        If other is a dict, it must have the keys "min" and "max",
        and a random number is returned in that inclusive range.

        If rand_float is True, random numbers will be floats.
        If it is False, random numbers will be ints.
        """
        self._other = copy.deepcopy(other)
        self.rand_float = rand_float

        if isinstance(self._other, dict):
            if "min" not in other:
                raise KeyError("No minimum specified in random range.")

            if "max" not in other:
                raise KeyError("No maximum specified in random range.")

            self.is_rand = True
            self._min = self._other["min"]
            self._max = self._other["max"]

        elif isinstance(self._other, int) or isinstance(self._other, float):
            self.is_rand = False
            self.value = self._other

        else:
            raise TypeError("Could not parse other={!r} (type={}) as a dict, int, or float.".format(other, type(other)))

    def __call__(self):
        if not self.is_rand:
            return self.value

        elif self.rand_float:
            return random.uniform(self._min, self._max)

        else:
            return random.randint(self._min, self._max)

    def description(self):
        """A description of what this condition requires"""
        if not self.is_rand:
            return str(self.value)

        elif self.rand_float:
            return "a random number in {}..{}".format(float(self._min), float(self._max))

        else:
            return "a random number in {}..{}".format(int(self._min), int(self._max))

    def __repr__(self):
        return "GetNumberOrRandom({}, {})".format(self._other, self.is_rand)


class TestNumberOrRange(object):
    """Test if to_test matches conditions."""
    def __init__(self, conditions):
        """
        conditions should be an integer, float, or dict.

        If conditions is an integer or float, to_test must match exactly.

        If conditions is a dict, it must have the keys "min" and/or "max", inclusive.
        """
        self.conditions = copy.deepcopy(conditions)

        if isinstance(conditions, dict):
            self.is_range = True
            if "min" not in conditions and "max" not in conditions:
                raise KeyError("No minimum or maximum specified in range; must have at least one.")

            self._min = conditions.get("min", None)
            self._max = conditions.get("max", None)

        elif isinstance(conditions, int) or isinstance(conditions, float):
            self.is_range = False
            self.value = conditions

        else:
            raise TypeError("Could not parse other={!r} (type={}) as a dict, int, or float.".format(other, type(other)))

    def __call__(self, other):
        if self.is_range:
            if self._min is not None and other < self._min:
                return False

            if self._max is not None and self._max < other:
                return False

            return True

        else:
            return other == self.value

    def description(self):
        """A description of this number or range"""
        if not self.is_range:
            return "equals ".format(self.value)

        elif self._min is None:
            return "is in ..{}".format(int(self._max))

        elif self._max is None:
            return "is in {}..".format(int(self._min))

        else:
            return "is in {}..{}".format(int(self._min), int(self._max))

    def __repr__(self):
        return "TestNumberOrRange({})".format(self.conditions)

