"""Module containing Point class

Note: A namedtuple could replace this class for Python 3.7+
"""


# .............................................................................
class Point:
    def __init__(self, species_name, x, y, flags=None):
        """Constructor."""
        self.species_name = species_name
        self.x = x
        self.y = y
        self.flags = []
        if flags is not None:
            self.flags = flags
