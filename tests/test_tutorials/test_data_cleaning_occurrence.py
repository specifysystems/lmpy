"""Test the occurrence data cleaning tutorial."""
import json
import os
from lmpy.data_wrangling.factory import WranglerFactory
from lmpy.point import PointCsvReader, PointCsvWriter


MIN_DECIMAL_PRECISION = 4
TEST_BBOX = (0, -90, 180, 0)


# .....................................................................................
def wrangler_config():
    """Get an occurrence data wrangler configuration JSON for testing.

    Returns:
        list of dict: A List of wrangler configuration dictionaries.
    """
    return [
        # Decimal precision
        dict(
            wrangler_type='DecimalPrecisionFilter',
            decimal_places=MIN_DECIMAL_PRECISION
        ),
        # Bounding box
        dict(
            wrangler_type='BoundingBoxFilter',
            min_x=TEST_BBOX[0],
            min_y=TEST_BBOX[1],
            max_x=TEST_BBOX[2],
            max_y=TEST_BBOX[3]
        ),
        # Unique localities
        dict(wrangler_type='UniqueLocalitiesFilter')
    ]


# .....................................................................................
def test_instructions_console_script(
    generate_temp_filename,
    tutorial_data_dir,
    script_runner
):
    """Test the instructions for cleaning occurrences using a script.

    Args:
        generate_temp_filename (pytest.Fixture): Fixture for generating filenames.
        tutorial_data_dir (pytest.Fixture): Fixture to get directory of tutorial data.
        script_runner (pytest.Fixture): Fixture to run a script.
    """
    clean_occurrences_filename = generate_temp_filename(suffix='.csv')
    wrangler_config_filename = generate_temp_filename(suffix='.json')
    with open(wrangler_config_filename, mode='wt') as wrangler_out:
        json.dump(wrangler_config(), wrangler_out, indent=4)

    script_args = [
        os.path.join(tutorial_data_dir, 'occurrence/Crocodylus porosus.csv'),
        clean_occurrences_filename,
        wrangler_config_filename,
    ]
    script_runner(
        'wrangle_occurrences',
        'lmpy.tools.wrangle_occurrences',
        script_args
    )
    _validate_outputs(clean_occurrences_filename)


# .....................................................................................
def test_instructions_python(generate_temp_filename, tutorial_data_dir):
    """Test the instructions for cleaning occurrences using python.

    Args:
        generate_temp_filename (pytest.Fixture): Fixture for generating filenames.
        tutorial_data_dir (pytest.Fixture): Fixture to get directory of tutorial data.
    """
    clean_occurrences_filename = generate_temp_filename(suffix='.csv')
    factory = WranglerFactory()
    wranglers = factory.get_wranglers(wrangler_config())
    with PointCsvReader(
        os.path.join(tutorial_data_dir, 'occurrence/Crocodylus porosus.csv'),
        'species_name',
        'x',
        'y'
    ) as reader:
        with PointCsvWriter(
            clean_occurrences_filename, ['species_name', 'x', 'y']
        ) as writer:
            for points in reader:
                for wrangler in wranglers:
                    points = wrangler.wrangle_points(points)
                if len(points) > 0:
                    writer.write_points(points)
    _validate_outputs(clean_occurrences_filename)


# .....................................................................................
def _validate_outputs(clean_occurrences_filename):
    """Validate that the output occurrence records are clean.

    Args:
        clean_occurrences_filename (str): File location of cleaned data to test.
    """
    with PointCsvReader(clean_occurrences_filename, 'species_name', 'x', 'y') as reader:
        seen_localities = []
        for points in reader:
            for point in points:
                # Check decimal precision
                assert len(str(point.x).split('.')[1]) >= MIN_DECIMAL_PRECISION
                assert len(str(point.y).split('.')[1]) >= MIN_DECIMAL_PRECISION
                # Test point is within bounding box
                assert TEST_BBOX[0] <= point.x <= TEST_BBOX[2]
                assert TEST_BBOX[1] <= point.y <= TEST_BBOX[3]
                # Test that this locality has not been seen before
                assert (point.x, point.y) not in seen_localities
                seen_localities.append((point.x, point.y))
