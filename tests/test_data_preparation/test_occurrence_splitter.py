"""Test the occurrence_splitter module."""
import glob

from lmpy.data_preparation.occurrence_splitter import (
    get_writer_filename_func,
    get_writer_key_from_fields_func,
    OccurrenceSplitter,
)
from lmpy.data_wrangling.factory import WranglerFactory
from lmpy.point import PointCsvReader, PointDwcaReader

from tests.data_simulator import (
    generate_csv,
    generate_dwca,
    get_random_choice_func,
    get_random_float_func,
    get_random_string_func,
    SimulatedField,
)
from tests.data_validator import validate_point_csvs


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
            get_random_float_func(-90.0, 90.0, 2, 6),
            'float'
        ),
        SimulatedField(
            'longitude',
            'http://rs.tdwg.org/dwc/terms/decimalLongitude',
            get_random_float_func(-180.0, 180.0, 2, 6),
            'float'
        )
    ]
    generate_dwca(dwca_filename, 1000, dwca_fields)
    wrangler_config = [
        {
            'wrangler_type': 'AcceptedNameOccurrenceWrangler',
            'attribute_name': 'taxonname',
            'accepted_name_map': SPECIES_MAP
        }
    ]

    # Run script
    splitter = OccurrenceSplitter(
        get_writer_key_from_fields_func('taxonname'),
        get_writer_filename_func(temp_directory)
    )
    factory = WranglerFactory()

    splitter.process_reader(
        PointDwcaReader(dwca_filename), factory.get_wranglers(wrangler_config)
    )
    splitter.close()

    # Check output
    assert validate_point_csvs(
        glob.glob(f'{temp_directory}/*.csv'), 'taxonname', 'longitude', 'latitude'
    )


# .....................................................................................
def test_one_csv(monkeypatch, generate_temp_filename, temp_directory):
    """Test data splitting for a single CSV file.

    Args:
        monkeypatch (pytest.fixture): A fixture for monkeypatching.
        generate_temp_filename (pytest.fixture): A fixture for generating tempoarary
            filenames.
        temp_directory (pytest.fixture): A fixture to get a temporary directory.
    """
    # Temporary files
    csv_filename = generate_temp_filename()

    # Generate a CSV and wranglers
    sp_key = 'species'
    x_key = 'decimallongitude'
    y_key = 'decimallatitude'
    csv_fields = [
        SimulatedField(
            sp_key,
            'http://rs.tdwg.org/dwc/terms/specificEpithet',
            get_random_choice_func(list(SPECIES_MAP.keys())),
            'str'
        ),
        SimulatedField(
            y_key,
            'http://rs.tdwg.org/dwc/terms/decimalLatitude',
            get_random_float_func(-90.0, 90.0, 2, 6),
            'float'
        ),
        SimulatedField(
            x_key,
            'http://rs.tdwg.org/dwc/terms/decimalLongitude',
            get_random_float_func(-180.0, 180.0, 2, 6),
            'float'
        )
    ]
    generate_csv(csv_filename, 1000, csv_fields)
    wrangler_config = [
        {
            'wrangler_type': 'AcceptedNameOccurrenceWrangler',
            'attribute_name': sp_key,
            'accepted_name_map': SPECIES_MAP
        }
    ]
    factory = WranglerFactory()

    with OccurrenceSplitter(
        get_writer_key_from_fields_func(sp_key),
        get_writer_filename_func(temp_directory)
    ) as splitter:
        splitter.process_reader(
            PointCsvReader(csv_filename, sp_key, x_key, y_key),
            factory.get_wranglers(wrangler_config)
        )

    # Check output
    assert validate_point_csvs(
        glob.glob(f'{temp_directory}/*.csv'), sp_key, x_key, y_key
    )


# .....................................................................................
def test_complex(monkeypatch, generate_temp_filename, temp_directory):
    """Test splitting multiple files of different types.

    Args:
        monkeypatch (pytest.fixture): A fixture for monkeypatching.
        generate_temp_filename (pytest.fixture): A fixture for generating tempoarary
            filenames.
        temp_directory (pytest.fixture): A fixture to get a temporary directory.
    """
    # Initialize wrangler factory
    factory = WranglerFactory()

    # Temporary files
    dwca_1_filename = generate_temp_filename()
    dwca_2_filename = generate_temp_filename()
    csv_1_filename = generate_temp_filename()
    csv_2_filename = generate_temp_filename()

    # Reader and wrangler configurations
    # DWCA 1
    dwca_1_fields = [
        SimulatedField(
            'taxonname',
            'http://rs.tdwg.org/dwc/terms/specificEpithet',
            get_random_choice_func(list(SPECIES_MAP.keys())),
            'str'
        ),
        SimulatedField(
            'latitude',
            'http://rs.tdwg.org/dwc/terms/decimalLatitude',
            get_random_float_func(-90.0, 90.0, 2, 6),
            'float'
        ),
        SimulatedField(
            'longitude',
            'http://rs.tdwg.org/dwc/terms/decimalLongitude',
            get_random_float_func(-180.0, 180.0, 2, 6),
            'float'
        ),
        SimulatedField(
            'occ_source',
            'http://rs.tdwg.org/dwc/terms/collectionID',
            get_random_choice_func(['dwca_1']),
            'str'
        ),
        SimulatedField(
            'throw_away',
            'http://rs.tdwg.org/dwc/terms/eventRemarks',
            get_random_string_func(2, 20),
            'str'
        ),
    ]
    # Accepted name, common fields
    dwca_1_wrangler_conf = [
        {
            'wrangler_type': 'AcceptedNameOccurrenceWrangler',
            'attribute_name': 'taxonname',
            'accepted_name_map': SPECIES_MAP
        },
        {
            'wrangler_type': 'CommonFormatWrangler',
            'attribute_map': {
                'taxonname': 'species',
                'latitude': 'latitude',
                'longitude': 'longitude',
                'occ_source': 'collection'
            }
        }
    ]
    # Write testing data
    generate_dwca(dwca_1_filename, 5000, dwca_1_fields)

    # DWCA 2
    dwca_2_fields = [
        SimulatedField(
            'species_name',
            'http://rs.tdwg.org/dwc/terms/specificEpithet',
            get_random_choice_func(list(SPECIES_MAP.keys())),
            'str'
        ),
        SimulatedField(
            'decimallatitude',
            'http://rs.tdwg.org/dwc/terms/decimalLatitude',
            get_random_float_func(-90.0, 90.0, 2, 6),
            'float'
        ),
        SimulatedField(
            'decimallongitude',
            'http://rs.tdwg.org/dwc/terms/decimalLongitude',
            get_random_float_func(-180.0, 180.0, 2, 6),
            'float'
        ),
        SimulatedField(
            'occ_collection',
            'http://rs.tdwg.org/dwc/terms/collectionID',
            get_random_choice_func(['dwca_2']),
            'str'
        ),
        SimulatedField(
            'throw_away_2',
            'http://rs.tdwg.org/dwc/terms/eventRemarks',
            get_random_string_func(2, 20),
            'str'
        ),
    ]
    # Accepted name, common fields
    dwca_2_wrangler_conf = [
        {
            'wrangler_type': 'AcceptedNameOccurrenceWrangler',
            'attribute_name': 'species_name',
            'accepted_name_map': SPECIES_MAP
        },
        {
            'wrangler_type': 'CommonFormatWrangler',
            'attribute_map': {
                'species_name': 'species',
                'decimallatitude': 'latitude',
                'decimallongitude': 'longitude',
                'occ_collection': 'collection'
            }
        }
    ]
    # Write testing data
    generate_dwca(dwca_2_filename, 5000, dwca_2_fields)

    # CSV 1
    csv_1_fields = [
        SimulatedField(
            'tax',
            'http://rs.tdwg.org/dwc/terms/specificEpithet',
            get_random_choice_func(list(SPECIES_MAP.keys())),
            'str'
        ),
        SimulatedField(
            'lat',
            'http://rs.tdwg.org/dwc/terms/decimalLatitude',
            get_random_float_func(-90.0, 90.0, 2, 6),
            'float'
        ),
        SimulatedField(
            'lon',
            'http://rs.tdwg.org/dwc/terms/decimalLongitude',
            get_random_float_func(-180.0, 180.0, 2, 6),
            'float'
        ),
        SimulatedField(
            'col_1',
            'http://rs.tdwg.org/dwc/terms/collectionID',
            get_random_choice_func(['csv_1']),
            'str'
        ),
        SimulatedField(
            'throw_away_3',
            'http://rs.tdwg.org/dwc/terms/eventRemarks',
            get_random_string_func(2, 20),
            'str'
        ),
    ]
    # Accepted name, common fields
    csv_1_wrangler_conf = [
        {
            'wrangler_type': 'AcceptedNameOccurrenceWrangler',
            'attribute_name': 'tax',
            'accepted_name_map': SPECIES_MAP
        },
        {
            'wrangler_type': 'CommonFormatWrangler',
            'attribute_map': {
                'tax': 'species',
                'lat': 'latitude',
                'lon': 'longitude',
                'col_1': 'collection'
            }
        }
    ]
    # Write testing data
    generate_csv(csv_1_filename, 5000, csv_1_fields)

    # CSV 2
    csv_2_fields = [
        SimulatedField(
            'taxname',
            'http://rs.tdwg.org/dwc/terms/specificEpithet',
            get_random_choice_func(list(SPECIES_MAP.keys())),
            'str'
        ),
        SimulatedField(
            'dec_lat',
            'http://rs.tdwg.org/dwc/terms/decimalLatitude',
            get_random_float_func(-90.0, 90.0, 2, 6),
            'float'
        ),
        SimulatedField(
            'dec_lon',
            'http://rs.tdwg.org/dwc/terms/decimalLongitude',
            get_random_float_func(-180.0, 180.0, 2, 6),
            'float'
        ),
        SimulatedField(
            'collection',
            'http://rs.tdwg.org/dwc/terms/collectionID',
            get_random_choice_func(['csv_2']),
            'str'
        ),
        SimulatedField(
            'throw_away_4',
            'http://rs.tdwg.org/dwc/terms/eventRemarks',
            get_random_string_func(2, 20),
            'str'
        ),
    ]
    # Accepted name, common fields
    csv_2_wrangler_conf = [
        {
            'wrangler_type': 'AcceptedNameOccurrenceWrangler',
            'attribute_name': 'taxname',
            'accepted_name_map': SPECIES_MAP
        },
        {
            'wrangler_type': 'CommonFormatWrangler',
            'attribute_map': {
                'taxname': 'species',
                'dec_lat': 'latitude',
                'dec_lon': 'longitude',
                'collection': 'collection'
            }
        }
    ]
    # Write testing data
    generate_csv(csv_2_filename, 5000, csv_2_fields)

    with OccurrenceSplitter(
        get_writer_key_from_fields_func('species'),
        get_writer_filename_func(temp_directory)
    ) as splitter:
        splitter.process_reader(
            PointDwcaReader(dwca_1_filename), factory.get_wranglers(dwca_1_wrangler_conf)
        )
        splitter.process_reader(
            PointDwcaReader(dwca_2_filename), factory.get_wranglers(dwca_2_wrangler_conf)
        )
        splitter.process_reader(
            PointCsvReader(csv_1_filename, 'tax', 'lon', 'lat'),
            factory.get_wranglers(csv_1_wrangler_conf)
        )
        splitter.process_reader(
            PointCsvReader(csv_2_filename, 'taxname', 'dec_lon', 'dec_lat'),
            factory.get_wranglers(csv_2_wrangler_conf)
        )

    # Check output
    assert validate_point_csvs(
        glob.glob(f'{temp_directory}/*.csv'), 'species', 'longitude', 'latitude'
    )
