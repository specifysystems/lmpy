"""Test the split occurrence data tool."""
from collections import namedtuple
import csv
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import pytest

from lmpy.point import DWCA_OCCURRENCE_PARAMS, OCCURRENCE_ROW_TYPE


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

def get_random_int_func(min, max):
    def get_random_int():
        return np.random.randint(min, max)
    return get_random_int

def get_random_float_func(min_val, max_val, min_precision, max_precision):
    def get_random_float():
        return np.round(
            (max_val - min_val) * np.random.random() + min_val,
            np.random.randint(min_precision, max_precision)
        )
    return get_random_float

def get_random_string_func(min_chars, max_chars, char_set, do_capitalize):
    def get_random_string():
        rand_str = ''.join([np.random.choice(char_set) for _ in np.random.randint(min_chars, max_chars)])
        if do_capitalize:
            rand_str = rand_str.capitalize()
        return rand_str
    return get_random_string

def get_random_choice_func(choices):
    def get_random_choice():
        return np.random.choice(choices)
    return get_random_choice

@pytest.fixture(scope='function')
def generate_temp_filename(request):
    """Get a function to generate (and clean up) temporary files."""
    fns = []

    def get_filename(*args, **kwargs):
        fn = tempfile.NamedTemporaryFile().name
        fns.append(fn)
        return fn

    def finalizer():
        for fn in fns:
            if os.path.exists(fn):
                os.remove(fn)

    request.addfinalizer(finalizer)
    return get_filename


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

# header - A CSV column header for this field
# concept - A DarwinCore concept for the field
# create - A function to create a value
# type_str - The type of this field, as a string
SimulatedField = namedtuple(
    'SimulatedField', ['header', 'concept', 'create', 'type_str']
)

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


def test_one_dwca(monkeypatch, generate_temp_filename, temp_out_dir):
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
        '--dwca',
        'dwca_filename',
        'wrangler_config_filename',
        temp_out_dir
    ]

    monkeypatch('sys.argv', params)
    cli()


