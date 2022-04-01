"""Test the clean_occurrences tool."""
from copy import deepcopy
import json

import numpy as np
import pytest

from lmpy.point import PointCsvReader, PointCsvWriter
from lmpy.tools.clean_occurrences import cli

from tests.data_simulator import (
    generate_csv,
    get_random_choice_func,
    get_random_float_func,
    SimulatedField,
)


# .....................................................................................
@pytest.fixture(
    scope='function',
    params=[
        ('species_name', 'x', 'y', True),
        ('species_name', 'x', 'y', False),
        ('taxon', 'longitude', 'latitude', True),
        ('taxon', 'longitude', 'latitude', False),
        ('species', 'x_val', 'y_val', True),
        ('a', 'b', 'c', False),
    ],
)
def data_keys(request):
    """Get a set of csv header keys for testing.

    Args:
        request (pytest.Fixture): Pytest request fixture.

    Yields:
        tuple of (str, str, str, bool): Species key, x key, y key, should report
    """
    yield request.param


# .....................................................................................
def test_valid(monkeypatch, generate_temp_filename, data_keys):
    """Perform tests on valid data and validate the results.

    Args:
        monkeypatch (pytest.Fixture): Pytest monkeypatch fixture.
        generate_temp_filename (pytest.fixture): Fixture to generate filenames.
        data_keys (pytest.Fixture): Fixture providing configuration parameters.
    """
    in_points_fn = generate_temp_filename(suffix='.csv')
    out_points_fn = generate_temp_filename(suffix='.csv')
    wranglers_fn = generate_temp_filename(suffix='.json')
    report_fn = generate_temp_filename(suffix='.json')

    target_precision = 4
    # Write wrangler configuration file
    wrangler_config = [
        {
            'wrangler_type': 'DecimalPrecisionFilter',
            'decimal_places': target_precision,
        },
        {
            'wrangler_type': 'UniqueLocalitiesFilter',
            'do_reset': 'False'
        },
    ]
    with open(wranglers_fn, mode='wt') as json_out:
        json.dump(wrangler_config, json_out)
    sp_key, x_key, y_key, do_report = data_keys

    # Generate points
    generate_csv(
        in_points_fn,
        100,
        [
            SimulatedField(
                sp_key,
                '',
                get_random_choice_func([f'Species {i}' for i in range(5)]),
                'str'
            ),
            SimulatedField(
                x_key,
                '',
                get_random_float_func(-180.0, 180.0, 1, 6),
                'float'
            ),
            SimulatedField(
                y_key,
                '',
                get_random_float_func(-90.0, 90.0, 1, 6),
                'float'
            ),
        ]
    )
    points = []
    with PointCsvReader(in_points_fn, sp_key, x_key, y_key) as reader:
        for pts in reader:
            points.extend(pts)

    # Figure out how many points are valid
    valid_points = set()
    for pt in points:
        if all(
            [
                len(str(pt.x).split('.')[1]) >= target_precision,
                len(str(pt.y).split('.')[1]) >= target_precision,
            ]
        ):
            valid_points.add((pt.species_name, pt.x, pt.y))
    # Create some duplicates
    for _ in range(np.random.randint(len(points))):
        points.append(deepcopy(points[np.random.randint(len(points))]))
    # Write points
    with PointCsvWriter(in_points_fn, data_keys[:-1]) as writer:
        writer.write_points(points)
    # Run data cleaner
    args = ['clean_occurrences.py']
    # ------
    args.extend(['-sp', sp_key, '-x', x_key, '-y', y_key])
    if do_report:
        args.extend(['-r', report_fn])
    # ------
    args.extend([in_points_fn, out_points_fn, wranglers_fn])
    monkeypatch.setattr('sys.argv', args)
    cli()
    # Read points
    with PointCsvReader(out_points_fn, *data_keys[:-1]) as reader:
        cleaned_points = []
        for clean_points in reader:
            cleaned_points.extend(clean_points)
    # Check count
    print(f'Cleaned points: {len(cleaned_points)}')
    print(f'Valid points: {len(valid_points)}')
    assert len(cleaned_points) == len(valid_points)

    # If report, check it
    if do_report:
        with open(report_fn, mode='rt') as in_report:
            report = json.load(in_report)
        assert 'wranglers' in report.keys()
        assert report['input_records'] == len(points)
        assert report['output_records'] == len(cleaned_points)
