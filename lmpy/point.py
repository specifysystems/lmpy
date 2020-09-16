"""Module containing Point class

Note: A namedtuple could replace this class for Python 3.7+
"""


# .............................................................................
class Point:
    """Class representing an occurrence data point."""
    # .......................
    def __init__(self, species_name, x, y, attributes=None):
        """Constructor."""
        if species_name is None or len(species_name) < 1:
            raise ValueError('Species name must be provided')
        self.species_name = species_name.capitalize()
        self.x = float(x)
        self.y = float(y)
        if attributes is None:
            self.attributes = {}
        else:
            self.attributes = attributes
        # Set attributes for species name, x, and y
        self.attributes['species_name'] = self.species_name
        self.attributes['x'] = self.x
        self.attributes['y'] = self.y

    # .......................
    def __eq__(self, other):
        return self.species_name == other.species_name and \
            self.x == other.x and self.y == other.y

    # .......................
    def __lt__(self, other):
        if self.species_name < other.species_name:
            return True
        if self.species_name == other.species_name:
            if self.x < other.x:
                return True
            if self.x == other.x:
                return self.y < other.y
        return False

    # .......................
    def __repr__(self):
        return 'Point(species="{}", x={}, y={})'.format(
            self.species_name, self.x, self.y)

    # .......................
    def get_attribute(self, attribute_name):
        """Get an attribute for the point."""
        if attribute_name in self.attributes.keys():
            return self.attributes[attribute_name]
        else:
            return None

    # .......................
    def set_attribute(self, attribute_name, value):
        """Set an attribute for the point."""
        self.attributes[attribute_name] = value
