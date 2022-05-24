"""Test the tutorial instructions from aggregate_occurrence_data."""
import json
import os

from lmpy.data_preparation.occurrence_splitter import (
    get_writer_key_from_fields_func,
    get_writer_filename_func,
    OccurrenceSplitter,
)
from lmpy.data_wrangling.factory import WranglerFactory
from lmpy.point import PointCsvReader, PointDwcaReader


# .....................................................................................
def wrangler_configs(data_dir):
    """Get wrangler configurations.

    Args:
        data_dir (str): Data containing tutorial data.

    Returns:
        dict: A dictionary of wrangler parameters.
    """
    return {
        'gbif': [
            dict(
                wrangler_type='AcceptedNameOccurrenceWrangler',
                name_map=os.path.join(data_dir, 'name_map/croc_name_map.json'),
            ),
            dict(
                wrangler_type='AttributeFilterWrangler',
                attribute_name='issue',
                filter_func={
                    'for-each': dict(
                        condition='not-in',
                        values=[
                            'TAXON_MATCH_FUZZY',
                            'TAXON_MATCH_HIGHERRANK'
                            'TAXON_MATCH_NONE'
                        ]
                    )
                }
            ),
            dict(
                wrangler_type='CommonFormatWrangler',
                attribute_map=dict(
                    taxonname='species_name',
                    decimallongitude='x',
                    decimallatitude='y'
                )
            )
        ],
        'idigbio': [
            dict(
                wrangler_type='AcceptedNameOccurrenceWrangler',
                name_map=os.path.join(data_dir, 'name_map/croc_name_map.json'),
            ),
            dict(
                wrangler_type='AttributeFilterWrangler',
                attribute_name='flags',
                filter_func={
                    'for-each': {
                        'condition': 'not-in',
                        'values': [
                            'geopoint_datum_missing',
                            'geopoint_bounds',
                            'geopoint_datum_error',
                            'geopoint_similar_coord',
                            'rev_geocode_mismatch',
                            'rev_geocode_failure',
                            'geopoint_0_coord',
                            'taxon_match_failed',
                            'dwc_kingdom_suspect',
                            'dwc_taxonrank_invalid',
                            'dwc_taxonrank_removed'
                        ]
                    }
                }
            ),
            dict(
                wrangler_type='AttributeModifierWrangler',
                attribute_name='data_source',
                attribute_func=dict(constant='idigbio')
            ),
            dict(
                wrangler_type='CommonFormatWrangler',
                attribute_map=dict(
                    species_name='species_name',
                    x='x',
                    y='y',
                    data_source='data_source'
                )
            )
        ],
        'ala': [
            dict(
                wrangler_type='AcceptedNameOccurrenceWrangler',
                name_map=os.path.join(data_dir, 'name_map/croc_name_map.json'),
            ),
            dict(
                wrangler_type='AttributeModifierWrangler',
                attribute_name='data_source',
                attribute_func=dict(constant='ala')
            ),
            dict(
                wrangler_type='CommonFormatWrangler',
                attribute_map=dict(
                    species_name='species_name',
                    x='x',
                    y='y',
                    data_source='data_source'
                )
            )
        ]
    }


# .....................................................................................
def test_instructions_python(
    tutorial_data_dir,
    generate_temp_filename,
    temp_directory
):
    """Test the python instructions.

    Args:
        tutorial_data_dir (pytest.Fixture): The tutorial data directory.
        generate_temp_filename (pytest.Fixture): A fixture to generate filenames.
        temp_directory (pytest.Fixture): A temporary directory to write outputs.
    """
    gbif_dwca_filename = os.path.join(tutorial_data_dir, 'occurrence/gbif.zip')
    idigbio_dwca_filename = os.path.join(tutorial_data_dir, 'occurrence/idigbio.zip')
    ala_csv_filename = os.path.join(tutorial_data_dir, 'occurrence/ala.csv')
    speces_name_map = os.path.join(tutorial_data_dir, 'name_map/croc_name_map.json')

    species_list_filename = generate_temp_filename(suffix='.txt')
    key_field = ['species_name']
    out_dir = temp_directory
    # Wrangler configuration dictionaries

    # Establish functions for getting writer key and filename
    writer_key_func = get_writer_key_from_fields_func(*tuple(key_field))
    writer_filename_func = get_writer_filename_func(out_dir)

    factory = WranglerFactory()
    readers_and_wranglers = [
        (
            PointDwcaReader(gbif_dwca_filename),
            factory.get_wranglers(wrangler_configs(tutorial_data_dir)['gbif'])
        ),
        (
            PointDwcaReader(idigbio_dwca_filename),
            factory.get_wranglers(wrangler_configs(tutorial_data_dir)['idigbio'])
        ),
        (
            PointCsvReader(
                ala_csv_filename,
                'scientificName',
                'decimalLongitude',
                'decimalLatitude'
            ),
            factory.get_wranglers(wrangler_configs(tutorial_data_dir)['ala'])
        )
    ]
    write_fields = ['species_name', 'x', 'y', 'data_source']

    # Initialize processor
    with OccurrenceSplitter(
        writer_key_func,
        writer_filename_func,
        write_fields=write_fields,
    ) as occurrence_processor:
        for reader, wranglers in readers_and_wranglers:
            occurrence_processor.process_reader(reader, wranglers)
        occurrence_processor.write_species_list(species_list_filename)

    # Check the outputs
    _validate_outputs(
        species_list_filename,
        out_dir,
        speces_name_map
    )


# .....................................................................................
def test_instructions_console_script(
    tutorial_data_dir,
    script_runner,
    generate_temp_filename,
    temp_directory,
):
    """Test the console script instructions.

    Args:
        tutorial_data_dir (pytest.Fixture): A directory with tutorial data.
        script_runner (pytest.Fixture): Fixture for running scripts.
        generate_temp_filename (pytest.Fixture): Fixture for creating filenames.
        temp_directory (pytest.Fixture): A temporary work directory.
    """
    gbif_dwca_filename = os.path.join(tutorial_data_dir, 'occurrence/gbif.zip')
    idigbio_dwca_filename = os.path.join(tutorial_data_dir, 'occurrence/idigbio.zip')
    ala_csv_filename = os.path.join(tutorial_data_dir, 'occurrence/ala.csv')
    species_list_filename = generate_temp_filename(suffix='.txt')
    gbif_wranglers_filename = generate_temp_filename(suffix='.json')
    idigbio_wranglers_filename = generate_temp_filename(suffix='.json')
    ala_wranglers_filename = generate_temp_filename(suffix='.json')
    output_dir = temp_directory

    # Write out data wranglers
    with open(gbif_wranglers_filename, mode='wt') as gbif_wranglers_out:
        json.dump(
            wrangler_configs(tutorial_data_dir)['gbif'],
            gbif_wranglers_out
        )
    with open(idigbio_wranglers_filename, mode='wt') as idigbio_wranglers_out:
        json.dump(
            wrangler_configs(tutorial_data_dir)['idigbio'],
            idigbio_wranglers_out
        )
    with open(ala_wranglers_filename, mode='wt') as ala_wranglers_out:
        json.dump(
            wrangler_configs(tutorial_data_dir)['ala'],
            ala_wranglers_out
        )

    script_args = [
        f'--species_list_filename={species_list_filename}',
        '--dwca',
        gbif_dwca_filename,
        gbif_wranglers_filename,
        '--dwca',
        idigbio_dwca_filename,
        idigbio_wranglers_filename,
        '--csv',
        ala_csv_filename,
        ala_wranglers_filename,
        'scientificName',
        'decimalLongitude',
        'decimalLatitude',
        output_dir,
    ]
    script_runner(
        'split_occurrence_data',
        'lmpy.tools.split_occurrence_data',
        script_args
    )

    # Check the outputs
    _validate_outputs(
        species_list_filename,
        output_dir,
        os.path.join(tutorial_data_dir, 'name_map/croc_name_map.json')
    )


# .....................................................................................
def _validate_outputs(species_list_filename, output_dir, accepted_names_filename):
    """Validate outputs to ensure they are what we expect.

    Args:
        species_list_filename (str): File containing species seen.
        output_dir (str): Directory where outputs are stored.
        accepted_names_filename (str): File containing accepted names mapping.
    """
    # Load accepted names
    with open(accepted_names_filename, mode='rt') as in_species:
        accepted_names = [
            val.lower() for val in json.load(in_species).values() if val is not None
        ]

    with open(species_list_filename, mode='rt') as species_list_in:
        for line in species_list_in:
            species = line.strip()
            assert species.lower() not in ['null', 'none']
            species_filename = os.path.join(output_dir, f'{species}.csv')
            assert os.path.exists(species_filename)
            sp_point_count = 0
            with PointCsvReader(species_filename, 'species_name', 'x', 'y') as reader:
                for points in reader:
                    for point in points:
                        sp_point_count += 1
                        assert point.species_name.lower() in accepted_names
            assert sp_point_count > 0
