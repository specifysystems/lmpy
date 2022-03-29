"""Module containing functions used to simulate data for testing."""
from collections import namedtuple
import csv
from io import StringIO
import string
# Bandit doesn't like bare element tree but we need it for creating xml docs.
# Note that we only create XML, we don't parse anything
import xml.etree.ElementTree as ET  # nosec
import zipfile

import numpy as np


from lmpy.point import (
    CORE_TAG,
    DWCA_OCCURRENCE_PARAMS,
    FIELD_TAG,
    FILES_TAG,
    ID_TAG,
    LOCATION_TAG,
    OCCURRENCE_ROW_TYPE,
    Point
)


# .....................................................................................
def get_random_dict_func(fields):
    """Get a parameterless function to generate random dictionaries.

    Args:
        fields (list): A list of SimulatedFields for the dictionary.

    Returns:
        Method: A parameterless function that returns a random dictionary.
    """
    # ..................
    def get_random_dict():
        """Get a random dictionary.

        Returns:
            dict: A random dictionary.
        """
        return {fld.header: fld.create() for fld in fields}

    return get_random_dict


# .....................................................................................
def get_random_int_func(min_val, max_val):
    """Get a parameterless function to generate random integers.

    Args:
        min_val (int): The minimum value in the desired range (inclusive).
        max_val (int): The maximum value in the desired range (exclusive).

    Returns:
        Method: A parameterless function that returns a random integer in range.
    """
    # ..................
    def get_random_int():
        """Get a random integer.

        Returns:
            int: A random integer in the range specified in the outer function.
        """
        return np.random.randint(min, max)

    return get_random_int


# .....................................................................................
def get_random_float_func(min_val, max_val, min_precision, max_precision):
    """Get a parameterless function to generate random floats.

    Args:
        min_val (float): The minimum value of the random range (inclusive).
        max_val (float): The maximum value of the random range (exclusive).
        min_precision (int): The minimum decimal place precision for the number.
        max_precision (int): The maximum decimal place precision for the number.

    Returns:
        Method: A parameterless function that returns a random float in range.
    """
    # ..................
    def get_random_float():
        """Get a random float.

        Returns:
            float: A random float in the range specified in the outer function.
        """
        return np.round(
            (max_val - min_val) * np.random.random() + min_val,
            np.random.randint(min_precision, max_precision)
        )

    return get_random_float


# .....................................................................................
def get_random_string_func(
    min_chars,
    max_chars,
    char_set=string.ascii_letters,
    do_capitalize=False,
):
    """Get a parameterless function to generate random strings.

    Args:
        min_chars (int): The minimum length of a generated string.
        max_chars (int): The maximum length of a generated string.
        char_set (iterable): Characters options for the generated string.
        do_capitalize (bool): Should the first character be capitalized.

    Returns:
        Method: A parameterless function that returns a string.
    """
    if isinstance(char_set, str):
        char_set = list(char_set)

    # ..................
    def get_random_string():
        """Get a random string.

        Returns:
            str: A randomly generated string determined by outer function parameters.
        """
        rand_str = ''.join(
            np.random.choice(char_set, np.random.randint(min_chars, max_chars))
        )
        if do_capitalize:
            rand_str = rand_str.capitalize()
        return rand_str

    return get_random_string


# .....................................................................................
def get_random_choice_func(choices):
    """Get a parameterless function to randomly select one of the provided choices.

    Args:
        choices (list): A list of options to choose from.

    Returns:
        Method: A parameterless function that returns a random choice.
    """
    # ..................
    def get_random_choice():
        """Get a random selection from the outer function choices.

        Returns:
            Object: A choice of one of the provided choices.
        """
        return np.random.choice(choices)

    return get_random_choice


# .....................................................................................
# header - A CSV column header for this field
# concept - A DarwinCore concept for the field
# create - A function to create a value
# type_str - The type of this field, as a string
SimulatedField = namedtuple(
    'SimulatedField', ['header', 'concept', 'create', 'type_str']
)


# .....................................................................................
def generate_dwca(filename, count, fields):
    """Generate a DarwinCore Archive for testing.

    Args:
        filename (str): A file location to write the DWCA.
        count (int): The number of points to simulate.
        fields (list of SimulatedField): A list of simulated fields.
    """
    occ_filename = 'occurrence.csv'

    # Create metadata xml
    meta_el = ET.Element('archive')
    core_el = ET.SubElement(
        meta_el,
        CORE_TAG,
        attrib={
            'encoding': DWCA_OCCURRENCE_PARAMS['encoding'],
            'fieldsTerminatedBy': ',',
            'linesTerminatedBy': '\n',
            'ignoreHeaderLines': '1',
            'rowType': OCCURRENCE_ROW_TYPE
        }
    )
    ET.SubElement(ET.SubElement(core_el, FILES_TAG), LOCATION_TAG).text = occ_filename

    # Add id?
    ET.SubElement(core_el, ID_TAG, attrib={'index': '0'})

    # Add fields
    for idx, fld in enumerate(fields):
        ET.SubElement(
            core_el,
            FIELD_TAG,
            attrib={'index': str(idx), 'term': fld.concept},
        )

    # Open zip file
    with zipfile.ZipFile(
        filename, mode='w', compression=zipfile.ZIP_DEFLATED, allowZip64=True
    ) as zip_f:
        # Write out occurrence data
        occ_buffer = StringIO()
        csv_writer = csv.DictWriter(
            occ_buffer, delimiter=',', fieldnames=[f.header for f in fields]
        )
        csv_writer.writeheader()
        for _ in range(count):
            csv_writer.writerow({f.header: f.create() for f in fields})
        zip_f.writestr(occ_filename, occ_buffer.getvalue())
        # Write out metadata
        zip_f.writestr('meta.xml', ET.tostring(meta_el))


# .....................................................................................
def generate_csv(filename, count, fields):
    """Generate a CSV file for testing.

    Args:
        filename (str): A file location to write the CSV.
        count (int): The number of points to simulate.
        fields (list of SimulatedField): A list of simulated fields.
    """
    with open(filename, mode='wt') as out_file:
        # Write out occurrence data
        csv_writer = csv.DictWriter(
            out_file, delimiter=',', fieldnames=[f.header for f in fields]
        )
        csv_writer.writeheader()
        for _ in range(count):
            # Write row of simulated values
            csv_writer.writerow({f.header: f.create() for f in fields})


# .....................................................................................
def generate_points(count, species_field, x_field, y_field, fields):
    """Generate a list of Point objects for testing.

    Args:
        count (int): THe number of points to simulate.
        species_field (SimulatedField): A simulated field for species.
        x_field (SimulatedField): A simulated field for the x coordiante.
        y_field (SimulatedField): A simulated field for the y coordinate.
        fields (list of SimulatedField): A list of simulated fields.

    Returns:
        list of Point: A list of Point objects.
    """
    points = []
    for _ in range(count):
        atts = {
            fld.header: fld.create() for fld in fields
        }
        atts[species_field.header] = species_field.create()
        atts[x_field.header] = x_field.create()
        atts[y_field.header] = y_field.create()
        points.append(
            Point(
                atts[species_field.header],
                atts[x_field.header],
                atts[y_field.header],
                attributes=atts
            )
        )

    return points
