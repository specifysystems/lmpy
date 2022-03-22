"""Test configuration fixtures."""
import glob
import os
import shutil
import tempfile

import pytest


# .............................................................................
# .                                 Constants                                 .
# .............................................................................
DWCA_DIR = 'dwcas'
TREES_DIR = 'trees'
LAYER_ENCODER_DIR = 'encoding_layers'
OCCURRENCE_WRANGLER_DIR = 'data_wranglers/occurrence'

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DATA_PATH = os.path.join(THIS_DIR, 'data_dir')


# .............................................................................
class SampleDataFiles(object):
    """This class is used to retrieve sample data for the tests.

    Note:
        * For test files, the format should be something like:
            "(in)valid_{name}.{extension}".
    """

    # ...........................
    def get_shapegrid_filenames(self):
        """Get a list of shapegrid filenames.

        Returns:
            A list of shapegrid filenames
        """
        ENCODER_DATA_PATH = os.path.join(SAMPLE_DATA_PATH, LAYER_ENCODER_DIR)
        return glob.glob(os.path.join(ENCODER_DATA_PATH, 'shapegrid*.shp'))

    # ...........................
    def get_raster_env_filenames(self):
        """Get a list of raster environmental layer filenames.

        Returns:
            A list of raster filenames
        """
        ENCODER_DATA_PATH = os.path.join(SAMPLE_DATA_PATH, LAYER_ENCODER_DIR)
        return [glob.glob(os.path.join(ENCODER_DATA_PATH, 'env*.tif'))]

    # ...........................
    def get_vector_env_filenames(self):
        """Get a list of vector environmental layer filenames.

        Returns:
            A list of vector filenames
        """
        ENCODER_DATA_PATH = os.path.join(SAMPLE_DATA_PATH, LAYER_ENCODER_DIR)
        return [glob.glob(os.path.join(ENCODER_DATA_PATH, 'env*.shp'))]

    # ...........................
    def get_raster_pa_filenames(self):
        """Get a list of raster presence absence layer filenames.

        Returns:
            A list of raster filenames
        """
        ENCODER_DATA_PATH = os.path.join(SAMPLE_DATA_PATH, LAYER_ENCODER_DIR)
        return [glob.glob(os.path.join(ENCODER_DATA_PATH, 'sdm*.tif'))]

    # ...........................
    def get_vector_pa_filenames(self):
        """Get a list of vector presence absence layer filenames.

        Returns:
            A list of vector filenames
        """
        ENCODER_DATA_PATH = os.path.join(SAMPLE_DATA_PATH, LAYER_ENCODER_DIR)
        return [glob.glob(os.path.join(ENCODER_DATA_PATH, 'sdm*.shp'))]

    # ...........................
    def get_bio_geo_filenames(self):
        """Get a list of biogeographic hypothesis filenames.

        Returns:
            A list of hypothesis filenames
        """
        ENCODER_DATA_PATH = os.path.join(SAMPLE_DATA_PATH, LAYER_ENCODER_DIR)
        return [glob.glob(os.path.join(ENCODER_DATA_PATH, 'bg_hyp*.shp'))]

    # ...........................
    def get_dwcas(self):
        """Get a list of sample Darwin Core Archive filenames.

        Returns:
            list: A list of sample dwca zip files.
        """
        DWCA_DATA_PATH = os.path.join(SAMPLE_DATA_PATH, DWCA_DIR)
        return [glob.glob(os.path.join(DWCA_DATA_PATH, '*.zip'))]

    # ...........................
    def get_occurrence_wrangler_configurations(self):
        """Get a list of occurrence data wrangler configruation files.

        Returns:
            A list of occurrence data wrangler configuration filenames.
        """
        OCCURRENCE_WRANGLER_PATH = os.path.join(
            SAMPLE_DATA_PATH, OCCURRENCE_WRANGLER_DIR
        )
        return glob.glob(os.path.join(OCCURRENCE_WRANGLER_PATH, '*.json'))

    # ...........................
    def get_trees(self, fmt, is_valid):
        """Gets an alignment file from the sample data.

        Args:
            fmt (str): The format of the file you want (newick, nexus).
            is_valid (bool): Return valid data files if true, invalid files if
                not.

        Returns:
            A list of tree filenames.
        """
        TREE_PATH = os.path.join(SAMPLE_DATA_PATH, TREES_DIR)
        return glob.glob(
            self._get_glob_string(TREE_PATH, is_valid, self._get_format_extension(fmt))
        )

    # ...........................
    def _get_format_extension(self, fmt):
        """Get the file extension for a format.

        Args:
            fmt (str): The name of a format to get the file extension for.

        Returns:
            str: A file extension for the specified format.

        Raises:
            Exception: If the specified format was not found.
        """
        if fmt.lower() == 'newick':
            return '.tre'
        elif fmt.lower() == 'nexus':
            return '.nex'
        elif fmt.lower() == 'nexml':
            return '.xml'
        else:
            raise Exception('Cannot handle format: {}'.format(fmt))

    # ...........................
    def _get_glob_string(self, search_dir, is_valid, fmt_ext):
        """Get a glob string for returning files.

        Args:
            search_dir (str): A directory to search for files.
            is_valid (bool): If True, look for files with 'valid' in filename
                otherwise look for 'invalid'.
            fmt_ext (str): Look for files with this file extension.

        Returns:
            A string that can be sent to glob to retrieve files matching the
                provided parameters.
        """
        if is_valid:
            valid_str = 'valid'
        else:
            valid_str = 'invalid'
        return os.path.join(search_dir, '{}_*{}'.format(valid_str, fmt_ext))


# .............................................................................
@pytest.fixture(scope="session")
def data_files():
    """Gets test fixture used to retrieve sample data files.

    Returns:
        A `SampleDataFiles` object.
    """
    return SampleDataFiles()


# .....................................................................................
@pytest.fixture(scope='session')
def generate_temp_filename(request):
    """Get a function to generate (and clean up) temporary files.

    Args:
        request (pytest.fixture): A pytest request fixture.

    Returns:
        Method: A function to generate a temporary filename.
    """
    delete_globs = []

    # ..................
    def get_filename(suffix='', wildcard_delete=True):
        """Get a temporary filename.

        Args:
            suffix (str): A suffix to add to the filename.
            wildcard_delete (bool): Delete all files with returned basename.

        Returns:
            str: A temporary filename.
        """
        base_name = tempfile.NamedTemporaryFile(suffix=suffix).name
        fn = f'{base_name}{suffix}'
        if wildcard_delete:
            delete_globs.append(f'{base_name}*')
        else:
            delete_globs.append(fn)
        return fn

    # ..................
    def finalizer():
        """Clean up temporary files."""
        for del_glob in delete_globs:
            for fn in glob.glob(del_glob):
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
    os.makedirs(dir_name)
    yield dir_name

    shutil.rmtree(dir_name)


# .............................................................................
def pytest_generate_tests(metafunc):
    """Pytest function for generating tests.

    Args:
        metafunc (:obj:`pytest.Metafunc`): Pytest metafunc object passed to
            test hook.

    Note:
        * We are catching this function to parameterize tests here in a central
            location rather than for each test instance
    """
    df = SampleDataFiles()
    # Tuples of (fixture name, parameterization lists)
    fixture_tuples = [
        ('valid_newick_tree', df.get_trees('newick', True)),
        ('valid_nexml_tree', df.get_trees('nexml', True)),
        ('valid_nexus_tree', df.get_trees('nexus', True)),
        ('shapegrid_filename', df.get_shapegrid_filenames()),
        ('raster_env_filenames', df.get_raster_env_filenames()),
        ('vector_env_filenames', df.get_vector_env_filenames()),
        ('raster_pa_filenames', df.get_raster_pa_filenames()),
        ('vector_pa_filenames', df.get_vector_pa_filenames()),
        ('bio_geo_filenames', df.get_bio_geo_filenames()),
        (
            'occurrence_wrangler_configuration',
            df.get_occurrence_wrangler_configurations(),
        ),
        ('dwca_filename', df.get_dwcas()),
    ]
    for fixture_name, fixture_values in fixture_tuples:
        if fixture_name in metafunc.fixturenames:
            metafunc.parametrize(fixture_name, fixture_values)
