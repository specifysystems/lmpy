"""Test the split occurrence data tool."""
import glob
import json

from lmpy.tools.split_occurrence_data import cli
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
    with open(wrangler_config_filename, mode='wt') as json_out:
        json.dump(
            [
                {
                    'wrangler_type': 'attribute_modifier',
                    'attribute_name': 'taxonname',
                    'map_values': SPECIES_MAP
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
        dwca_filename,
        wrangler_config_filename,
        temp_directory
    ]

    monkeypatch.setattr('sys.argv', params)
    cli()

    # Check output
    assert validate_point_csvs(
        glob.glob(f'{temp_directory}/*.csv'), 'species_name', 'x', 'y'
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
    wrangler_config_filename = generate_temp_filename()

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
    with open(wrangler_config_filename, mode='wt') as json_out:
        json.dump(
            [
                {
                    'wrangler_type': 'attribute_modifier',
                    'attribute_name': sp_key,
                    'map_values': SPECIES_MAP
                }
            ],
            json_out
        )

    # Run script
    params = [
        'split_occurrence_data.py',
        '-k',
        sp_key,
        '--csv',
        csv_filename,
        wrangler_config_filename,
        sp_key,
        x_key,
        y_key,
        temp_directory
    ]

    monkeypatch.setattr('sys.argv', params)
    cli()

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
    # Temporary files
    dwca_1_filename = generate_temp_filename()
    dwca_2_filename = generate_temp_filename()
    csv_1_filename = generate_temp_filename()
    csv_2_filename = generate_temp_filename()

    wrangler_1_filename = generate_temp_filename()
    wrangler_2_filename = generate_temp_filename()
    wrangler_3_filename = generate_temp_filename()
    wrangler_4_filename = generate_temp_filename()

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
            'wrangler_type': 'attribute_modifier',
            'attribute_name': 'taxonname',
            'map_values': SPECIES_MAP
        },
        {
            'wrangler_type': 'attribute_map_modifier',
            'attribute_mapping': {
                'taxonname': 'species',
                'latitude': 'latitude',
                'longitude': 'longitude',
                'occ_source': 'collection'
            }
        }
    ]
    # Write testing data
    generate_dwca(dwca_1_filename, 5000, dwca_1_fields)
    with open(wrangler_1_filename, mode='wt') as json_out:
        json.dump(dwca_1_wrangler_conf, json_out)

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
            'wrangler_type': 'attribute_modifier',
            'attribute_name': 'species_name',
            'map_values': SPECIES_MAP
        },
        {
            'wrangler_type': 'attribute_map_modifier',
            'attribute_mapping': {
                'species_name': 'species',
                'decimallatitude': 'latitude',
                'decimallongitude': 'longitude',
                'occ_collection': 'collection'
            }
        }
    ]
    # Write testing data
    generate_dwca(dwca_2_filename, 5000, dwca_2_fields)
    with open(wrangler_2_filename, mode='wt') as json_out:
        json.dump(dwca_2_wrangler_conf, json_out)

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
            'wrangler_type': 'attribute_modifier',
            'attribute_name': 'tax',
            'map_values': SPECIES_MAP
        },
        {
            'wrangler_type': 'attribute_map_modifier',
            'attribute_mapping': {
                'tax': 'species',
                'lat': 'latitude',
                'lon': 'longitude',
                'col_1': 'collection'
            }
        }
    ]
    # Write testing data
    generate_csv(csv_1_filename, 5000, csv_1_fields)
    with open(wrangler_3_filename, mode='wt') as json_out:
        json.dump(csv_1_wrangler_conf, json_out)

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
            'wrangler_type': 'attribute_modifier',
            'attribute_name': 'taxname',
            'map_values': SPECIES_MAP
        },
        {
            'wrangler_type': 'attribute_map_modifier',
            'attribute_mapping': {
                'taxname': 'species',
                'dec_lat': 'latitude',
                'dec_lon': 'longitude',
                'collection': 'collection'
            }
        }
    ]
    # Write testing data
    generate_csv(csv_2_filename, 5000, csv_2_fields)
    with open(wrangler_4_filename, mode='wt') as json_out:
        json.dump(csv_2_wrangler_conf, json_out)

    # Run script
    params = [
        'split_occurrence_data.py',
        '-k',
        'species',
        '--dwca',
        dwca_1_filename,
        wrangler_1_filename,
        '--dwca',
        dwca_2_filename,
        wrangler_2_filename,
        '--csv',
        csv_1_filename,
        wrangler_3_filename,
        'tax',
        'lon',
        'lat',
        '--csv',
        csv_2_filename,
        wrangler_4_filename,
        'taxname',
        'dec_lon',
        'dec_lat',
        temp_directory
    ]

    monkeypatch.setattr('sys.argv', params)
    cli()

    # Check output
    assert validate_point_csvs(
        glob.glob(f'{temp_directory}/*.csv'), 'species_name', 'x', 'y'
    )
