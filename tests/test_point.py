"""Tests the occurrence_transformation module."""
import zipfile

import numpy as np
import pytest

from lmpy import Point
from lmpy.point import (
    none_getter,
    PointCsvReader,
    PointCsvWriter,
    PointDwcaReader,
    PointJsonWriter,
)
from tests.data_simulator import (
    generate_csv,
    generate_dwca,
    get_random_choice_func,
    get_random_dict_func,
    get_random_float_func,
    SimulatedField,
)


# .............................................................................
def _flag_getter(index):
    """Returns a getter for the test flags separated by ', '.

    Args:
        index (int or str): The index that contains flag information in the point.

    Returns:
        Method: A function to get issue flags.
    """

    def getter(obj):
        flag_string = obj[index]
        return flag_string.split(', ')

    return getter


# .............................................................................
def test_none_getter():
    """Tests that none_getter always returns None."""
    getter = none_getter
    assert getter(0) is None
    assert getter('a') is None
    assert getter(None) is None
    assert getter(b'0000') is None


# ............................................................................
class Test_Point:
    """Test Point class."""

    # ..........................
    def test_constructor(self):
        """Basic constructor tests."""
        _ = Point('test_species', 0, 0)
        with pytest.raises(ValueError):
            Point(None, 0, 0)

    # ..........................
    def test_equality(self):
        """Test for point equality and inequality."""
        pt_1 = Point('Species', 30, 30)
        pt_2 = Point('Species 2', 30, 30)
        pt_3 = Point('Species', 30, 30)
        assert pt_1 == pt_3
        assert pt_1 != pt_2

    # ..........................
    def test_less_than(self):
        """Test for less than."""
        pt_1 = Point('Species 1', 30, 30)
        pt_2 = Point('Species 2', 30, 30)
        pt_3 = Point('Species 1', 40, 20)
        pt_4 = Point('Species 1', 20, 40)
        pt_5 = Point('Species 1', 30, 40)
        assert pt_1 < pt_2
        assert pt_1 < pt_3
        assert pt_4 < pt_1
        assert pt_1 < pt_5
        assert not pt_1 < pt_1
        assert not pt_2 < pt_3

    # ..........................
    def test_get_set_attribute(self):
        """Test get and set attribute."""
        pt = Point('Species', 0, 0)
        assert pt.get_attribute('test') is None
        pt.set_attribute('test', 1)
        assert pt.get_attribute('test') == 1

    # ..........................
    def test_repr(self):
        """Test the repr function."""
        assert repr(Point('Species', 0, 0))


# ............................................................................
class Test_PointCsvReader:
    """Test the PointCSVReader class."""

    # ..........................
    def test_reader_species_x_y(self, generate_temp_filename):
        """Test with a CSV file of species, x, y.

        Args:
            generate_temp_filename (pytest.fixture): Method to create temp filenames.
        """
        pt_filename = generate_temp_filename(suffix='.csv')
        fields = [
            SimulatedField(
                'species',
                '',
                get_random_choice_func([f'Species {i}' for i in range(5)]),
                'str',
            ),
            SimulatedField(
                'lon',
                '',
                get_random_float_func(-180.0, 180.0, 3, 5),
                'float',
            ),
            SimulatedField(
                'lat',
                '',
                get_random_float_func(-90.0, 90.0, 3, 5),
                'float',
            )
        ]
        generate_csv(pt_filename, 50, fields)
        with PointCsvReader(pt_filename, 'species', 'lon', 'lat') as reader:
            for points in reader:
                assert len(points) > 0

    # ..........................
    def test_reader_species_geopoint(self, generate_temp_filename):
        """Test with a CSV file of species, geopt.

        Args:
            generate_temp_filename (pytest.fixture): Fixture to generate temporary
                filenames.
        """
        pt_filename = generate_temp_filename(suffix='.csv')

        generate_csv(
            pt_filename,
            10,
            [
                SimulatedField(
                    'species',
                    '',
                    get_random_choice_func([f'Species {i}' for i in range(2)]),
                    'str',
                ),
                SimulatedField(
                    'geopt',
                    '',
                    get_random_dict_func(
                        [
                            SimulatedField(
                                'lon',
                                '',
                                get_random_float_func(-180.0, 180.0, 4, 6),
                                'float',
                            ),
                            SimulatedField(
                                'lat',
                                '',
                                get_random_float_func(-90.0, 90.0, 4, 6),
                                'float',
                            ),
                        ]
                    ),
                    'dict',
                ),
            ],
        )
        with PointCsvReader(
            pt_filename, 'species', 'lon', 'lat', geopoint='geopt'
        ) as reader:
            for points in reader:
                assert len(points) > 0


# .....................................................................................
class Test_PointCsvWriter:
    """Test PointCsvWriter class."""

    # ..........................
    def test_basic(self, generate_temp_filename):
        """Perform simple test.

        Args:
            generate_temp_filename (pytest.fixture): Fixture to generate temporary
                filenames.
        """
        filename = generate_temp_filename(suffix='.csv')
        test_points = [
            Point('species', 0, 0),
            Point('species', 10, 10),
            Point('species', 20, 20),
            Point('species', -30, -30),
        ]
        with PointCsvWriter(filename, ['species_name', 'x', 'y']) as writer:
            writer.write_points(test_points[0])
            writer.write_points(test_points[1:])

        # Check that there are the correct number of points read
        with PointCsvReader(filename, 'species_name', 'x', 'y') as reader:
            points = []
            for read_points in reader:
                points.extend(read_points)

        assert len(test_points) == len(points)

    # ..........................
    def test_reopen(self, generate_temp_filename):
        """Open, write, close, and reopen test.

        Args:
            generate_temp_filename (pytest.fixture): Fixture to generate temporary
                filenames.
        """
        filename = generate_temp_filename(suffix='.csv')
        test_points = [
            Point(
                'species',
                np.random.randint(-180, 180),
                np.random.randint(-90, 90)
            ) for _ in range(np.random.randint(20, 100))
        ]
        # Write some points
        with PointCsvWriter(filename, ['species_name', 'x', 'y']) as writer:
            writer.write_points(test_points[:15])

        # Reopen
        with PointCsvWriter(
            filename, ['species_name', 'x', 'y'], mode='at', write_headers=False
        ) as writer:
            writer.write_points(test_points[15:])

        # Check that there are the correct number of points read
        with PointCsvReader(filename, 'species_name', 'x', 'y') as reader:
            points = []
            for read_points in reader:
                points.extend(read_points)

        assert len(test_points) == len(points)


# .....................................................................................
class Test_PointDwcaReader:
    """Test PointDwcaReader class."""

    # ..........................
    def test_generated_dwca(self, generate_temp_filename):
        """Test the DWCA reader with generated data.

        Args:
            generate_temp_filename (pytest.fixture): Fixture to generate filenames.
        """
        dwca_filename = generate_temp_filename(suffix='.zip')

        generate_dwca(
            dwca_filename,
            1000,
            [
                SimulatedField(
                    'species',
                    'http://rs.tdwg.org/dwc/terms/scientificName>',
                    get_random_choice_func([f'Species {i}' for i in range(2)]),
                    'str',
                ),
                SimulatedField(
                    'lon',
                    'http://rs.tdwg.org/dwc/terms/decimalLongitude',
                    get_random_float_func(-180.0, 180.0, 4, 6),
                    'float',
                ),
                SimulatedField(
                    'lat',
                    'http://rs.tdwg.org/dwc/terms/decimalLatitude',
                    get_random_float_func(-90.0, 90.0, 4, 6),
                    'float',
                ),
            ]
        )
        with PointDwcaReader(dwca_filename) as reader:
            # For each point
            for points in reader:
                # Check that all records are points
                for pt in points:
                    assert isinstance(pt, Point)

    # ..........................
    def test_aggregator_dwca(self, dwca_filename):
        """Test that an aggregator DWCA file can be processed correctly.

        Args:
            dwca_filename (str): A DWCA file to process.
        """
        for fn in dwca_filename:
            with PointDwcaReader(fn) as reader:
                for points in reader:
                    for pt in points:
                        assert isinstance(pt, Point)

    # ..........................
    def test_constants_dwca(self, generate_temp_filename):
        """Test that constant fields are added to point attributes.

        Args:
            generate_temp_filename (pytest.fixture): Fixture to generate temporary
                filenames.
        """
        # Create zip file
        dwca_filename = generate_temp_filename(suffix='.zip')
        constant_field = 'constant_field'
        constant_value = 'test_default'
        occ_data = '\n'.join(
            [
                'Some species,1,2',
                'Some species,18,28',
                'Some species,18,2',
                'Some species,12,2',
                'Some species2,1,22',
                'Some species2,18,23',
                'Some species2,13,2',
            ]
        )

        meta_xml_data = '\n'.join(
            [
                '<archive xmlns="http://rs.tdwg.org/dwc/text/">',
                '<core',
                ' encoding="utf-8"',
                ' fieldsTerminatedBy=","',
                ' linesTerminatedBy="\n"',
                ' ignoreHeaderLines="1"',
                ' rowType="http://rs.tdwg.org/dwc/terms/Occurrence">',
                '<files><location>occurrence.csv</location></files>',
                '<field index="0"',
                ' term="http://rs.tdwg.org/dwc/terms/scientificName"/>',
                '<field index="1"',
                ' term="http://rs.tdwg.org/dwc/terms/decimalLongitude"/>',
                '<field index="2"',
                ' term="http://rs.tdwg.org/dwc/terms/decimalLatitude"/>',
                '<field term="{}" default="{}"/>'.format(
                    constant_field, constant_value
                ),
                '</core>',
                '</archive>',
            ]
        )

        with zipfile.ZipFile(
            dwca_filename, mode='w', compression=zipfile.ZIP_DEFLATED
        ) as zip_file:
            zip_file.writestr('occurrence.csv', occ_data)
            zip_file.writestr('meta.xml', meta_xml_data)

        # Set up reader
        with PointDwcaReader(dwca_filename) as reader:
            # For each point
            for points in reader:
                # Check that all records are points
                for pt in points:
                    assert isinstance(pt, Point)
                    # Check for constant field
                    assert pt.get_attribute(constant_field) == constant_value


# Test that constants work
# Test specific fields


# ............................................................................
class Test_PointJsonWriter:
    """Test PointJsonWriter class."""

    # ..........................
    def test_basic(self, generate_temp_filename):
        """Perform simple test.

        Args:
            generate_temp_filename (pytest.fixture): Fixture to generate temporary
                filenames.
        """
        filename = generate_temp_filename(suffix='.json')
        with PointJsonWriter(filename) as writer:
            writer.write_points(Point('species', 0, 0))
            writer.write_points(
                [
                    Point('species', 10, 10),
                    Point('species', 20, 20),
                    Point('species', -30, -30),
                ]
            )
