"""Test the clean_occurrences tool."""
from copy import deepcopy
import json
import os
import sys
import tempfile

import numpy as np
import pytest

from lmpy.point import Point, PointCsvReader, PointCsvWriter
from lmpy.tools.clean_occurrences import cli


# .....................................................................................
@pytest.fixture(
    scope='function',
    params=[
        ('species_name', 'x', 'y', True),
        ('species_name', 'x', 'y', False),
        ('taxon', 'longitude', 'latitude', True),
        ('taxon', 'longitude', 'latitude', False),
        ('species', 'x_val', 'y_val', True),
        ('a', 'b', 'c', False)
    ]
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
@pytest.fixture(scope='function')
def filenames():
    """Get a group of filenames for use in tests (in, out, wrangler config).

    Yields:
        tuple of (str, str, str, str): A tuple containing file paths to use in test.
    """
    base_fn = tempfile.NamedTemporaryFile().name
    ret_filenames = (
        f'{base_fn}_in.csv',
        f'{base_fn}_out.csv',
        f'{base_fn}_wranglers.json',
        f'{base_fn}_report.json'
    )
    yield ret_filenames
    for fn in ret_filenames:
        if os.path.exists(fn):
            os.remove(fn)


# .....................................................................................
def generate_points(
    count, min_precision, max_precision, sp_key='species_name', x_key='x', y_key='y'
):
    """Generate random Point objects for tests.

    Args:
        count (int): The number of points to generate.
        min_precision (int): The minimum decimal precision for each point.
        max_precision (int): The maximum decimal precision for each point.
        sp_key (str): The attribute to use for the species name.
        x_key (str): The attribute to use for the x value.
        y_key (str): The attribute to use for the y value.

    Returns:
        list of Points: A list of Point objects for testing.
    """
    sp_name = 'Some species'
    points = []
    for _ in range(count):
        x_val = np.round(
             360 * np.random.random() - 180,  # Random value in range (-180, 180)
             np.random.randint(min_precision, max_precision)  # Random precision
        )
        y_val = np.round(
             180 * np.random.random() - 90,  # Random value in range (-90, 90)
             np.random.randint(min_precision, max_precision)  # Random precision
        )
        points.append(
            Point(
                sp_name,
                x_val,
                y_val,
                attributes={sp_key: sp_name, x_key: x_val, y_key: y_val}
            )
        )
    return points


# .....................................................................................
def test_valid(monkeypatch, filenames, data_keys):
    """Perform tests on valid data and validate the results.

    Args:
        monkeypatch (pytest.Fixture): Pytest monkeypatch fixture.
        filenames (pytest.Fixture): Fixture providing test filenames.
        data_keys (pytest.Fixture): Fixture providing configuration parameters.
    """
    target_precision = 4
    # Write wrangler configuration file
    wrangler_config = [
        {
            'wrangler_type': 'decimal_precision_filter',
            'decimal_precision': target_precision
        },
        {'wrangler_type': 'unique_localities_filter'}
    ]
    with open(filenames[2], mode='wt') as json_out:
        json.dump(wrangler_config, json_out)
    sp_key, x_key, y_key, do_report = data_keys
    points = generate_points(100, 1, 6, sp_key=sp_key, x_key=x_key, y_key=y_key)
    # Figure out how many points are valid
    valid_points = set()
    for pt in points:
        if all([
            len(str(pt.x).split('.')[1]) >= target_precision,
            len(str(pt.y).split('.')[1]) >= target_precision
        ]):
            valid_points.add((pt.species_name, pt.x, pt.y))
    # Create some duplicates
    for _ in range(np.random.randint(len(points))):
        points.append(deepcopy(points[np.random.randint(len(points))]))
    # Write points
    with PointCsvWriter(filenames[0], data_keys[:-1]) as writer:
        writer.write_points(points)
    # Run data cleaner
    args = ['clean_occurrences.py']
    # ------
    args.extend(['-sp', sp_key, '-x', x_key, '-y', y_key])
    if do_report:
        args.extend(['-r', filenames[3]])
    # ------
    args.extend(list(filenames[:-1]))
    monkeypatch.setattr('sys.argv', args)
    cli()
    # Read points
    with PointCsvReader(filenames[1], *data_keys[:-1]) as reader:
        cleaned_points = []
        for clean_points in reader:
            cleaned_points.extend(clean_points)
    # Check count
    print(f'Cleaned points: {len(cleaned_points)}')
    print(f'Valid points: {len(valid_points)}')
    assert len(cleaned_points) == len(valid_points)

    # If report, check it
    if do_report:
        with open(filenames[3], mode='rt') as in_report:
            report = json.load(in_report)
        assert 'wranglers' in report.keys()
        assert report['input_records'] == len(points)
        assert report['output_records'] == len(cleaned_points)
