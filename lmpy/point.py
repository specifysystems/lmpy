"""Module containing Point class

Note: A namedtuple could replace this class for Python 3.7+
"""
import csv
import json
from operator import itemgetter


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


# .............................................................................
class PointCsvReader:
    """Class for reading Points from a CSV file."""
    # .......................
    def __init__(self, filename, species_field, x_field, y_field,
                 geopoint=None, group_field='species_name'):
        self.filename = filename
        self.file = None
        self.reader = None
        self.species_field = species_field
        self.x_field = x_field
        self.y_field = y_field
        self.geopoint = geopoint
        self.group_field = group_field

    # .......................
    def __enter__(self):
        self.open()
        return self

    # .......................
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    # .......................
    def __iter__(self):
        return self

    # .......................
    def __next__(self):
        """Get lists of consecutive points with the same attribute value."""
        ret_points = []
        curr_val = None
        for point_dict in self.reader:
            try:
                if self.geopoint is not None:
                    x_val = json.loads(point_dict[self.geopoint])[self.x_field]
                    y_val = json.loads(point_dict[self.geopoint])[self.y_field]
                else:
                    x_val = point_dict[self.x_field]
                    y_val = point_dict[self.y_field]
                pt = Point(
                    point_dict[self.species_field], x_val, y_val,
                    attributes=point_dict)
                test_val = pt.get_attribute(self.group_field)
                if test_val != curr_val:
                    if curr_val is not None:
                        return ret_points
                        ret_points = []
                    curr_val = test_val
                ret_points.append(pt)

            except ValueError as ve:
                pass
            except KeyError as ke:
                raise ke
        if ret_points:
            tmp = ret_points
            ret_points = None
            return tmp
        raise StopIteration

    # .......................
    def open(self):
        self.file = open(self.filename, 'r')
        temp_lines = [next(self.file), next(self.file), next(self.file)]
        dialect = csv.Sniffer().sniff('\n'.join(temp_lines), delimiters="\t,")
        self.file.seek(0)
        self.reader = csv.DictReader(self.file, dialect=dialect)

    # .......................
    def close(self):
        """Close file"""
        self.file.close()


# .............................................................................
class PointCsvWriter():
    """Class for writing Points to a CSV file."""
    # .......................
    def __init__(self, filename, fields):
        self.filename = filename
        self.file = None
        self.writer = None
        self.field_names = fields

    # .......................
    def __enter__(self):
        self.open()
        return self

    # .......................
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    # .......................
    def close(self):
        """Close file"""
        self.file.close()

    # .......................
    def open(self):
        """Open file for writing."""
        self.file = open(self.filename, 'w')
        self.writer = csv.DictWriter(self.file, self.field_names)
        self.writer.writeheader()

    # .......................
    def write_points(self, points):
        """Write a Point object to the CSV file."""
        if isinstance(points, Point):
            points = [points]

        for point in points:
            point_dict = {k: point.get_attribute(k) for k in self.field_names}
            self.writer.writerow(point_dict)


# .............................................................................
class PointJsonWriter():
    """Class for writing Points to JSON"""
    # .......................
    def __init__(self, filename):
        self.filename = filename
        self.points = []

    # .......................
    def __enter__(self):
        self.open()
        return self

    # .......................
    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Exit and write JSON"""
        self.close()

    # .......................
    def close(self):
        """Close the writer"""
        with open(self.filename, 'w') as out_file:
            json.dump(self.points, out_file)

    # .......................
    def open(self):
        """Dummy method for consistency."""
        pass

    # .......................
    def write_points(self, point):
        """Add a point to the JSON output."""
        self.points.append(dict(point))


# .............................................................................
def none_getter(obj):
    """Return None as a function.

    Returns:
        None - Always returns None.
    """
    return None
