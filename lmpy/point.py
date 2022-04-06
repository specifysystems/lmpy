"""Module containing Point class.

Note: A namedtuple could replace this class for Python 3.7+
"""
import copy
import csv
import io
import json
import zipfile

import defusedxml.ElementTree as ET


DEFAULT_META_FILENAME = 'meta.xml'
# Metadata about occurrence records in DWCA with default values
# From https://dwc.tdwg.org/text/tdwg_dwc_text.xsd
DWCA_OCCURRENCE_PARAMS = {
    # Key: Default
    'linesTerminatedBy': '\n',
    'fieldsTerminatedBy': ',',
    'fieldsEnclosedBy': '"',
    'ignoreHeaderLines': 0,
    'rowType': None,  # Required
    'encoding': 'UTF-8',
    'dateFormat': 'YYY-MM-DD',
}

DEFAULT_SPECIES_TERM = 'scientificName'
DEFAULT_X_TERM = 'decimalLongitude'
DEFAULT_Y_TERM = 'decimalLatitude'

# DWCA Tag Constants
CORE_TAG = '{http://rs.tdwg.org/dwc/text/}core'
FIELD_TAG = '{http://rs.tdwg.org/dwc/text/}field'
FILES_TAG = '{http://rs.tdwg.org/dwc/text/}files'
ID_TAG = '{http://rs.tdwg.org/dwc/text/}id'
LOCATION_TAG = '{http://rs.tdwg.org/dwc/text/}location'
# EXTENSION_TAG = '{http://rs.tdwg.org/dwc/text/}extension'

# ROW_TYPE_ATT = 'rowType'
OCCURRENCE_ROW_TYPE = 'http://rs.tdwg.org/dwc/terms/Occurrence'


# .....................................................................................
class Point:
    """Class representing an occurrence data point."""

    # .......................
    def __init__(self, species_name, x, y, attributes=None):
        """Constructor.

        Args:
            species_name (:obj:`str`): The species name for this point.
            x (:obj:`float`): The value of the x coordinate for this occurrence point.
            y (:obj:`float`): The value of the y coordinate for this occurrence point.
            attributes (:obj:`dict`): A dictionary of attributes associated with this
                point.

        Raises:
            ValueError: Raised if the species name is omitted.
        """
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
        """Test if this point equals the other.

        Args:
            other (:obj:`Point`): A different Point object to compare with.

        Returns:
            bool: An indication if the two points are equal for the primary attributes.
        """
        return (
            self.species_name == other.species_name
            and self.x == other.x
            and self.y == other.y
        )

    # .......................
    def __lt__(self, other):
        """Test if this point is less than the other.

        Args:
            other (:obj:`Point`): A different Point object to compare with.

        Returns:
            bool: An indication if this point is less than the other for the primary
                attributes.
        """
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
        """Get a string representation of this Point object.

        Returns:
            str: A string representation of this Point.
        """
        return 'Point(species="{}", x={}, y={})'.format(
            self.species_name, self.x, self.y
        )

    # .......................
    def get_attribute(self, attribute_name):
        """Get an attribute for the point.

        Args:
            attribute_name (:obj:`str`): The attribute to attempt to retrieve.

        Returns:
            object: The value of the attribute if it exists.
            None: Returned if the attribute does not exist for the Point.
        """
        if attribute_name in self.attributes.keys():
            return self.attributes[attribute_name]
        return None

    # .......................
    def get_attribute_names(self):
        """Get the point's attributes.

        Returns:
            list of str: A list of the attributes for the point.
        """
        return list(self.attributes.keys())

    # .......................
    def set_attribute(self, attribute_name, value):
        """Set an attribute for the point.

        Args:
            attribute_name (:obj:`str`): The name of the attribute to set.
            value (:obj:`object`): The value to set the attribute to.
        """
        self.attributes[attribute_name] = value


# .....................................................................................
class PointCsvReader:
    """Class for reading Points from a CSV file."""

    # .......................
    def __init__(
        self,
        filename,
        species_field,
        x_field,
        y_field,
        geopoint=None,
        group_field='species_name',
    ):
        """Constructor for a Point CSV retriever.

        Args:
            filename (:obj:`str`): A file path containing CSV occurrence data.
            species_field (:obj:`str`): The field name of the column containing species
                data.
            x_field (:obj:`str`): The field name of the column containing x
                coordinates.
            y_field (:obj:`str`): The field name of the column containing y
                coordinates.
            geopoint (:obj:`str`): The field name of the column containing geopoint
                data.
            group_field (:obj:`str`): The name of the field to use for grouping points.
        """
        self.filename = filename
        self.file = None
        self.reader = None
        self.species_field = species_field
        self.x_field = x_field
        self.y_field = y_field
        self.geopoint = geopoint
        self.group_field = group_field
        self._next_points = []
        self._curr_val = None

    # .......................
    def __enter__(self):
        """Context manager magic method.

        Returns:
            PointCsvReader: This instance.
        """
        self.open()
        return self

    # .......................
    def __exit__(self, *args):
        """Context manager magic method on exit.

        Args:
            *args: Positional arguments passed to the exit function.
        """
        self.close()

    # .......................
    def __iter__(self):
        """Iterator magic method.

        Returns:
            PointCsvReader: This instance.
        """
        return self

    # .......................
    def __next__(self):
        """Get lists of consecutive points with the same attribute value.

        Returns:
            list: A list of point objects.

        Raises:
            KeyError: Raised if an attribute is missing.
            StopIteration: Raised when there are no additional objects.
        """
        for point_dict in self.reader:
            try:
                if self.geopoint is not None:
                    x_val = json.loads(point_dict[self.geopoint])[self.x_field]
                    y_val = json.loads(point_dict[self.geopoint])[self.y_field]
                else:
                    x_val = point_dict[self.x_field]
                    y_val = point_dict[self.y_field]
                pt = Point(
                    point_dict[self.species_field], x_val, y_val, attributes=point_dict
                )
                test_val = pt.get_attribute(self.group_field)
                if test_val != self._curr_val:
                    if self._curr_val is not None:
                        self._curr_val = test_val
                        tmp = self._next_points
                        self._next_points = [pt]
                        return tmp
                    self._curr_val = test_val
                self._next_points.append(pt)

            except ValueError:  # pragma: no cover
                pass
            except KeyError as ke:  # pragma: no cover
                raise ke
            except TypeError:  # pragma: no cover
                pass
        if self._next_points:
            tmp = self._next_points
            self._next_points = []
            return tmp
        raise StopIteration

    # .......................
    def open(self):
        """Open the file and initialize."""
        self.file = open(self.filename, 'r')
        temp_lines = []
        try:
            for _ in range(3):
                temp_lines.append(next(self.file))
        except StopIteration:  # Raised if fewer than 3 lines in file
            pass
        dialect = csv.Sniffer().sniff('\n'.join(temp_lines), delimiters="\t,")
        self.file.seek(0)
        self.reader = csv.DictReader(self.file, dialect=dialect)

    # .......................
    def close(self):
        """Close the file."""
        self.file.close()


# .....................................................................................
class PointCsvWriter:
    """Class for writing Points to a CSV file."""

    # .......................
    def __init__(self, filename, fields, write_headers=True, mode='w', **kwargs):
        """Constructor for writing points to csv file.

        Args:
            filename (:obj:`str`): A file location to write points to.
            fields (:obj:`list`): A list of fields to include in the csv headers.
            write_headers (:obj:`bool`): Should headers be written.
            mode (:obj:`str`): File write mode.
            **kwargs (:obj:`dict`): Keyword parameters that will be passed to the
                DictWriter instance from the csv module.
        """
        self.filename = filename
        self.file = None
        self.writer = None
        self.field_names = fields
        self.kwargs = kwargs
        self.write_headers = write_headers
        self.file_mode = mode

    # .......................
    def __enter__(self):
        """Context manager magic method.

        Returns:
            PointCsvWriter: This instance.
        """
        self.open()
        return self

    # .......................
    def __exit__(self, *args):
        """Context manager magic method on exit.

        Args:
            *args: Positional arguments passed to the exit function.
        """
        self.close()

    # .......................
    def close(self):
        """Close file."""
        self.file.close()

    # .......................
    def open(self):
        """Open file for writing."""
        self.file = open(self.filename, self.file_mode)
        self.writer = csv.DictWriter(self.file, self.field_names, **self.kwargs)
        if self.write_headers:
            self.writer.writeheader()

    # .......................
    def write_points(self, points):
        """Write a Point object to the CSV file.

        Args:
            points (:obj:`list` of :obj:`Point`): A list of points to write.
        """
        if isinstance(points, Point):
            points = [points]

        for point in points:
            point_dict = {k: point.get_attribute(k) for k in self.field_names}
            self.writer.writerow(point_dict)


# .....................................................................................
class PointDwcaReader:
    """Class for reading Darwin Core Archives."""

    # .......................
    def __init__(
        self,
        dwca_filename,
        meta_filename=DEFAULT_META_FILENAME,
        species_term=DEFAULT_SPECIES_TERM,
        x_term=DEFAULT_X_TERM,
        y_term=DEFAULT_Y_TERM,
        geopoint_term=None,
    ):
        """Constructor for reading Darwin Core Archives.

        Args:
            dwca_filename (:obj:`str`): File location of a DWCA zip file.
            meta_filename (:obj:`str`): File within the archive containing metadata.
                Defaults to DEFAULT_META_FILENAME.
            species_term (:obj:`str`): Species term in the DWCA file.  Defaults to
                DEFAULT_SPECIES_TERM.
            x_term (:obj:`str`): X term in the DWCA file.  Defaults to DEFAULT_X_TERM.
            y_term (:obj:`str`): Y term in the DWCA file.  Defaults to DEFAULT_Y_TERM.
            geopoint_term (:obj:`str`): Geopoint term in the DWCA file.
                Default is None.
        """
        self.meta_filename = meta_filename
        self.archive_filename = dwca_filename
        self.occurrence_filename = None
        self.fields = {}
        self.occurrence_params = copy.deepcopy(DWCA_OCCURRENCE_PARAMS)
        self._curr_val = None
        self._next_points = []
        self.species_term = species_term
        self.x_term = x_term
        self.y_term = y_term
        self.geopoint_term = geopoint_term
        self.group_field = self.species_term

    # .......................
    def _get_species_name(self, point_dict):
        """Get the species name from the attribute dictionary.

        Args:
            point_dict (:obj:`dict`): A dictionary of point attributes.

        Returns:
            str: A species name
        """
        return point_dict[self.species_term]

    # .......................
    def _get_x_value(self, point_dict):
        """Get the x coordinate value from the attribute dictionary.

        Args:
            point_dict (:obj:`dict`): A dictionary of point attributes.

        Returns:
            numeric: The x coordinate retrieved.
            None: Returned if there is no x value.
        """
        if self.geopoint_term is not None:
            try:
                return json.loads(point_dict[self.geopoint_term].replace("'", '"'))[
                    self.x_term
                ]
            except Exception:
                return None
        return point_dict[self.x_term]

    # .......................
    def _get_y_value(self, point_dict):
        """Get the y coordinate value from the attribute dictionary.

        Args:
            point_dict (:obj:`dict`): A dictionary of point attributes.

        Returns:
            numeric: The y coordinate retrieved.
            None: Returned if there is no y value.
        """
        if self.geopoint_term is not None:
            try:
                return json.loads(point_dict[self.geopoint_term].replace("'", '"'))[
                    self.y_term
                ]
            except Exception:
                return None
        return point_dict[self.y_term]

    # .......................
    def __enter__(self):
        """Context manager magic method.

        Returns:
            PointDwcaReader: This instance.
        """
        self.open()
        return self

    # .......................
    def __exit__(self, *args):
        """Context manager magic method on exit.

        Args:
            *args: Positional arguments passed to the exit function.
        """
        self.close()

    # .......................
    def __iter__(self):
        """Iterator magic method.

        Returns:
            PointDwcaReader: This instance.
        """
        return self

    # .......................
    def __next__(self):
        """Get lists of consecutive points with the same attribute value.

        Returns:
            list: A list of point objects.

        Raises:
            StopIteration: Raised when there are no additional objects.
        """
        for point_row in self.reader:
            try:
                point_dict = {
                    term: self.fields[term](point_row) for term in self.fields.keys()
                }
                pt = Point(
                    self._get_species_name(point_dict),
                    self._get_x_value(point_dict),
                    self._get_y_value(point_dict),
                    attributes=point_dict,
                )
                test_val = pt.get_attribute(self.group_field)
                if test_val != self._curr_val:
                    if self._curr_val is not None:
                        self._curr_val = test_val
                        tmp = self._next_points
                        self._next_points = [pt]
                        return tmp
                    self._curr_val = test_val
                self._next_points.append(pt)
            except KeyError:
                pass
            except TypeError:
                pass

        if self._next_points:
            tmp = self._next_points
            self._next_points = []
            return tmp
        raise StopIteration

    # .......................
    def _process_metadata(self, meta_contents):
        """Process the metadata file contained in the archive.

        Args:
            meta_contents (:obj:`str`): The string contents of the metadata file
                (meta.xml).
        """
        root_element = ET.fromstring(meta_contents)
        core_element = root_element.find(CORE_TAG)

        # If core element is missing (iDigBio) look in extensions
        # if core_element is None:
        #    for extension_el in root_element.findall(EXTENSION_TAG):
        #        if core_element is None and \
        #           extension_el.attrib[ROW_TYPE_ATT] == OCCURRENCE_ROW_TYPE:
        #            core_element = extension_el

        # Process core element
        # - Look for parameters we use for processing
        for core_att in self.occurrence_params.keys():
            if core_att in core_element.attrib.keys():
                self.occurrence_params[core_att] = core_element.attrib[core_att]

        # Get the occurrence data file name in the zip file
        self.occurrence_filename = (
            core_element.find(FILES_TAG).findall(LOCATION_TAG)[0].text
        )

        # Get the CSV fields from the metadata
        for field_element in core_element.findall(FIELD_TAG):
            # Get field processing function
            field_term = field_element.attrib['term']
            # Remove namespace
            if field_term.find('/') > 0:
                field_term = field_term.split('/')[-1]
            field_index = None
            field_default = None
            field_vocabulary = None
            field_delimiter = None

            if 'index' in field_element.attrib.keys():
                field_index = int(field_element.attrib['index'])
            if 'default' in field_element.attrib.keys():
                field_default = field_element.attrib['default']
            if 'vocabulary' in field_element.attrib.keys():
                field_vocabulary = field_element.attrib['vocabulary']
            if 'delimitedBy' in field_element.attrib.keys():
                field_delimiter = field_element.attrib['delimitedBy']

            self.fields[field_term] = get_field_process_func(
                index=field_index,
                default=field_default,
                vocabulary=field_vocabulary,
                delimiter=field_delimiter,
            )
        # Check for id field
        for id_element in core_element.findall(ID_TAG):
            field_term = 'id'
            field_index = None
            field_default = None
            field_vocabulary = None
            field_delimiter = None

            if 'index' in id_element.attrib.keys():
                field_index = int(id_element.attrib['index'])
            if 'default' in id_element.attrib.keys():
                field_default = id_element.attrib['default']
            if 'vocabulary' in id_element.attrib.keys():
                field_vocabulary = id_element.attrib['vocabulary']
            if 'delimitedBy' in id_element.attrib.keys():
                field_delimiter = id_element.attrib['delimitedBy']

            self.fields[field_term] = get_field_process_func(
                index=field_index,
                default=field_default,
                vocabulary=field_vocabulary,
                delimiter=field_delimiter,
            )

    # .......................
    def open(self):
        """Open the file and initialize."""
        # Open the zip file
        self._zip_archive = zipfile.ZipFile(self.archive_filename, mode='r')
        # self._zip_archive.open()
        meta_contents = io.TextIOWrapper(
            self._zip_archive.open(self.meta_filename), encoding='utf8'
        ).read()
        self._process_metadata(meta_contents)
        # Read metadata
        # Get occurrence file ready
        self.file = io.TextIOWrapper(
            self._zip_archive.open(self.occurrence_filename),
            encoding=self.occurrence_params['encoding']
        )

        delimiter = self.occurrence_params['fieldsTerminatedBy']
        if delimiter.find('t') > 0:
            delimiter = '\t'

        reader_params = {
            'delimiter': delimiter,
        }
        if len(self.occurrence_params['linesTerminatedBy']) > 0:
            reader_params['lineterminator'] = self.occurrence_params[
                'linesTerminatedBy'
            ]
        if len(self.occurrence_params['fieldsEnclosedBy']) > 0:
            reader_params['quotechar'] = self.occurrence_params['fieldsEnclosedBy']
        # reader_params['quotechar'] = None

        self.reader = csv.reader(self.file, **reader_params)
        for _ in range(int(self.occurrence_params['ignoreHeaderLines'])):
            next(self.reader)

    # .......................
    def close(self):
        """Close the file."""
        self.file.close()
        self._zip_archive.close()


# .....................................................................................
class PointJsonWriter:
    """Class for writing Points to JSON."""

    # .......................
    def __init__(self, filename):
        """Constructor for writing JSON points.

        Args:
            filename (:obj:`str`): A file location to write the points to.
        """
        self.filename = filename
        self.points = []

    # .......................
    def __enter__(self):
        """Context manager magic method.

        Returns:
            PointJsonWriter: This instance.
        """
        self.open()
        return self

    # .......................
    def __exit__(self, *args):
        """Exit and write JSON.

        Args:
            *args: Positional arguments sent to the exit function.
        """
        self.close()

    # .......................
    def close(self):
        """Close the writer."""
        with open(self.filename, 'w') as out_file:
            json.dump(self.points, out_file)

    # .......................
    def open(self):
        """Dummy method for consistency."""
        pass

    # .......................
    def write_points(self, points):
        """Add a point to the JSON output.

        Args:
            points (:obj:`list` of :obj:`Point`): A list of point objects to write out.
        """
        if isinstance(points, Point):
            points = [points]

        for point in points:
            self.points.append(point.attributes)


# .....................................................................................
def get_field_process_func(index=None, default=None, vocabulary=None, delimiter=None):
    """Get a function to process a field for a specimen record.

    Args:
        index (:obj:`int`, optional): The column index of the field value to process.
            If none, always return the default.
        default (number or string, optional): An optional default value (optional if
            index is not None) to return when the value of the field is empty.
        vocabulary (:obj:`str`, optional): A URI that identifies a vocabulary used for
            this field's possible values.
        delimiter (:obj:`str`, optional): An optional delimiter to split the field
            value with.

    Returns:
        Method: A method for getting the value of a field for a specimen row.
    """
    # .......................
    def default_getter(row):
        """Returns the default value, always.

        Args:
            row (:obj:`list`): A row of data for a specimen.

        Returns:
            object: Whatever the default value for the field is.
        """
        return default

    # .......................
    def list_getter(row):
        """Returns a list of value for the field.

        Args:
            row (:obj:`list`): A row of data for a specimen.

        Returns:
            list: A list of values generated by splitting the row index.
        """
        raw_val = ''
        if default is not None:
            raw_val = default
        if len(row[index]) > 0:
            raw_val = row[index]
        if len(raw_val) > 0:
            return raw_val.split(delimiter)
        return []

    # .......................
    def value_getter(row):
        """Returns a value for the field.

        Args:
            row (:obj:`list`): A row of data for a specimen.

        Returns:
            object: Whatever value is retrieved from the field.
        """
        if len(row[index]) > 0:
            if vocabulary is None or row[index] in vocabulary:
                return row[index]
        return default

    # Get the proper function
    if index is None:
        # Returned if there is no index to get data from, always return the default
        return default_getter
    if delimiter is not None:
        # If there is an index and a delimiter, return a list generating function
        return list_getter
    # If there is an index but no delimiter, return a field getter
    return value_getter


# .....................................................................................
def none_getter(obj):
    """Return None as a function.

    Args:
        obj (:obj:`object`): Any object.

    Returns:
        None: Always returns None.
    """
    return None
