"""Test the split occurrence data tool."""
from collections import namedtuple
import csv
import shutil
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import pytest

from lmpy.point import DWCA_OCCURRENCE_PARAMS, OCCURRENCE_ROW_TYPE
from lmpy.tools.split_occurrence_data import cli


# .....................................................................................
# Test mapping dictionary from raw names to accepted names
SPECIES_MAP = {
    'Species A': 'Accepted A',
    'Species B': 'Accepted B',
    'Species C': 'Accepted A',
    'Species D': 'Accepted A',
    'Species E': 'Accepted E',
    'Species F': 'Accepted B',
    'Species G': 'Accepted G',
    'Species H': 'Accepted G',
    'Accepted A': 'Accepted A',
    'Accepted B': 'Accepted B',
    'Accepted E': 'Accepted E',
    'Accepted G': 'Accepted G'
}

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
        """Get a random float

        Returns:
            float: A random float in the range specified in the outer function.
        """
        return np.round(
            (max_val - min_val) * np.random.random() + min_val,
            np.random.randint(min_precision, max_precision)
        )

    return get_random_float


# .....................................................................................
def get_random_string_func(min_chars, max_chars, char_set, do_capitalize):
    """Get a parameterless function to generate random strings.

    Args:
        min_chars (int): The minimum length of a generated string.
        max_chars (int): The maximum length of a generated string.
        char_set (iterable): Characters options for the generated string.
        do_capitalize (bool): Should the first character be capitalized.

    Returns:
        Method: A parameterless function that returns a string.
    """
    # ..................
    def get_random_string():
        """Get a random string.

        Returns:
            str: A randomly generated string determined by outer function parameters.
        """
        rand_str = ''.join([
            np.random.choice(
                char_set
            ) for _ in np.random.randint(min_chars, max_chars)]
        ])
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
@pytest.fixture(scope='function')
def generate_temp_filename(request):
    """Get a function to generate (and clean up) temporary files.

    Args:
        request (pytest.fixture): A pytest request fixture.

    Returns:
        Method: A function to generate a temporary filename.
    """
    fns = []

    # ..................
    def get_filename(*args, **kwargs):
        """Get a temporary filename.

        Args:
            *args (list): Positional arguments.
            **kwargs (dict): Named arguments.

        Returns:
            str: A temporary filename.
        """
        fn = tempfile.NamedTemporaryFile().name
        fns.append(fn)
        return fn

    # ..................
    def finalizer():
        """Clean up temporary files."""
        for fn in fns:
            if os.path.exists(fn):
                os.remove(fn)

    request.addfinalizer(finalizer)
    return get_filename


# .....................................................................................
@pytest.fixture(scope='function')
def temp_directory():
    """Get a temporary directory for storing files.

    Yields:
        str: A directory to use for testing.
    """
    dir_name = tempfile.TemporaryDirectory().name
    yield dir_name

    shutil.rmtree(dir_name)



# .....................................................................................
# header - A CSV column header for this field
# concept - A DarwinCore concept for the field
# create - A function to create a value
# type_str - The type of this field, as a string
SimulatedField = namedtuple(
    'SimulatedField', ['header', 'concept', 'create', 'type_str']
)


# .....................................................................................
def generate_dwca(filename, count, fields)
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
        'core',
        attrib={
            'encoding': DWCA_OCCURRENCE_PARAMS['encoding'],
            'fieldsTerminatedBy': ',',
            'linesTerminatedBy': '\n',
            'ignoreHeaderLines': '1',
            'rowType': OCCURRENCE_ROW_TYPE
        }
    )
    ET.SubElement(ET.SubElement(core_el, 'files'), 'location').text = occ_filename

    # Add id?
    ET.SubElement(core_el, 'id', attrib={'index': 0})

    # Add fields
    for idx, fld in enumerate(fields):
        ET.SubElement(core_el, 'field', attrib={'index': idx, 'term': fld['concept']})

    # Open zip file
    with zipfile.ZipFile(
        filename, mode='w', compression=zipfile.ZIP_DEFLATED, allowZip64=True
    ) as zip_f:
        # Write out occurrence data
        occ_buffer = StringIO()
        csv_writer = csv.DictWriter(
            occ_buffer, delimiter=',', fieldnames=[f['header'] for f in fields]
        )
        csv_writer.writeheader()
        for _ in range(count):
            csv_writer.writerow({f['header']: f['create']() for f in fields})
        zip_f.writestr(occ_filename, occ_buffer.getvalue())
        # Write out metadata
        zip_f.writestr('meta.xml', ET.dump(meta_el)


# .....................................................................................
def generate_csv(filename, count, fields)
    """Generate a CSV file for testing.

    Args:
        filename (str): A file location to write the CSV.
        count (int): The number of points to simulate.
        fields (list of SimulatedField): A list of simulated fields.
    """
    with open(filename, mode='wt') as out_file:
        # Write header
        out_file.write('{}\n'.format(','.join([f['header'] for f in fields])))
        for _ in range(count):
            # Write row of simulated values
            out_file.write('{}\n'.format(','.join([f['create']() for f in fields])))


# .....................................................................................
def test_one_dwca(monkeypatch, generate_temp_filename, temp_directory):
    """Test data splitting for a single Darwin Core Archive.

    Args:
        monkeypatch (pytest.fixture): A fixture for monkeypatching.
        generate_temp_filename (pytest.fixture): A fixture for generating tempoarary
            filenames.
        temp_directory (pytest.fixture): A fixture to get a temporary directory.
    """
    # Temporary files
    dwca_filename = generate_temp_filename()
    wrangler_config_filename = generate_temp_filename()

    # Generate a DWCA and wranglers
    dwca_fields = [
        SimulatedField(
            'taxonname',
            'http://rs.tdwg.org/dwc/terms/specificEpithet',
            get_random_choice_func(list(SPECIES_MAP.keys())),
            'str'
        ),
        SimulatedField(
            'latitude',
            'http://rs.tdwg.org/dwc/terms/decimalLatitude',
            get_random_float(-90.0, 90.0, 2, 6),
            'float'
        ),
        SimulatedField(
            'longitude',
            'http://rs.tdwg.org/dwc/terms/decimalLongitude',
            get_random_float(-180.0, 180.0, 2, 6),
            'float'
        )
    ]
    generate_dwca(dwca_filename, 1000, dwca_fields)
    with open(wrangler_config_filename, mode='wt') as json_out:
        json.dump(
            [
                {
                    'wrangler_type': 'attribute_modifier',
                    'attribute_name': 'taxonname',
                    'map_names': SPECIES_MAP
                }
            ],
            json_out
        )

    # Run script
    params = [
        'split_occurrence_data.py',
        '-k',
        'taxonname',
        '--dwca',
        'dwca_filename',
        'wrangler_config_filename',
        temp_directory
    ]

    monkeypatch('sys.argv', params)
    cli()

    # Todo: Check output

"""
DWCA
CSV
Multiple of each


mix of formats and fields
wranglers

make sure to test max open writers

test output fields

wranglers
 accepted name
 common format - species, x, y, source, original sp

"""
