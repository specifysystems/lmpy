"""Module containing Point class

Note: A namedtuple could replace this class for Python 3.7+
"""
import csv
import json


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
                #print('value error: {}'.format(ve))
                #print(point_dict)
                pass
            except KeyError as ke:
                #pass
                print(point_dict)
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


# .............................................................................
def _get_points_for_generator(rec_generator, species_name_getter, x_getter,
                              y_getter, flags_getter):
    """Get a list of Points from a specimen record generator.

    Args:
        rec_generator: A generator function that generates point records.
        species_name_getter: A function for getting species name from a record.
        x_getter: A function for getting the 'x' value from a record.
        y_getter: A function for getting the 'y' value from a record.
        flags_getter: A function for getting the 'flags' value from a record.

    Returns:
        list of Point named tuples
    """
    points = []
    for pt_rec in rec_generator:
        try:
            points.append(
                Point(
                    species_name_getter(pt_rec), float(x_getter(pt_rec)),
                    float(y_getter(pt_rec)), flags_getter(pt_rec)))
        except (IndexError, KeyError, ValueError):  # pragma: no cover
            print('Could not extract required fields from {}'.format(pt_rec))
    return points


# .............................................................................
def convert_delimited_to_point(filename, species_getter, x_getter, y_getter,
                               flags_getter=none_getter, delimiter=', ',
                               headers=True):
    """Convert a file of delimited data into points.

    Args:
        filename (str): A path to a file of delimited data.
        species_getter (function or int): A method to get the species name or
            a column index in a delimited file.
        x_getter (function or int): A method to get the point x value or a
            column index in a delimited file.
        y_getter (function or int): A method to get the point y value or a
            column index in a delimited file.
        flags_getter (function or int): A method to get the point flags or a
            column index in a delimited file.
        delimiter (str): The delimiter of the delimited data.
        headers (bool): Does the file have a header row.

    Returns:
        list of Point objects
    """
    if isinstance(species_getter, int):
        species_getter = itemgetter(species_getter)

    if isinstance(x_getter, int):
        x_getter = itemgetter(x_getter)

    if isinstance(y_getter, int):
        y_getter = itemgetter(y_getter)

    with open(filename) as in_file:
        if headers:
            _ = next(in_file)
        reader = csv.reader(in_file, delimiter=delimiter)
        points = _get_points_for_generator(
            reader, species_getter, x_getter, y_getter, flags_getter)
    return points


# .............................................................................
def convert_json_to_point(json_obj, species_name_getter, x_getter, y_getter,
                          flags_getter=none_getter, point_iterator=iter):
    """Get a list of Points from a JSON object.

    Args:
        json_obj (dict or list): A JSON object to get point records from.
        species_name_getter: A function for getting species name from a record.
        x_getter: A function for getting the 'x' value from a record.
        y_getter: A function for getting the 'y' value from a record.
        flags_getter: A function for getting the 'flags' value from a record.
        point_iterator: An iterator function to pull records from the JSON
            object.

    Returns:
        list of Point named tuples
    """
    points = _get_points_for_generator(
        point_iterator(json_obj), species_name_getter, x_getter, y_getter,
        flags_getter)
    return points


