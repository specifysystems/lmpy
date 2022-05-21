"""Test the occurrence data wrangler factory module."""
import json
import os

from lmpy.data_wrangling.factory import WranglerFactory
from lmpy.data_wrangling.base import _DataWrangler
from lmpy.data_wrangling.occurrence.base import _OccurrenceDataWrangler
from lmpy.data_wrangling.occurrence.unique_localities_wrangler import (
    UniqueLocalitiesFilter,
)


# ............................................................................
class Test_wrangler_factory:
    """Test the occurrence data wrangler factory."""

    # .......................
    def test_wrangler_config(self, occurrence_wrangler_configuration):
        """Test wrangler configurations.

        Args:
            occurrence_wrangler_configuration (str): A file containing wrangler
                configuration information.
        """
        factory = WranglerFactory()

        with open(occurrence_wrangler_configuration) as in_file:
            raw_string = in_file.read()
            config = json.loads(
                raw_string.replace(
                    '$THIS_DIR$',
                    os.path.dirname(occurrence_wrangler_configuration).replace(
                        '\\', '/'
                    ),
                )
            )
        wranglers = factory.get_wranglers(config)
        assert wranglers[0]


# .....................................................................................
def test_wrangler_from_config_with_module(generate_temp_filename):
    """Test that we can get a data wrangler when specifying with a module.

    Args:
        generate_temp_filename (pytest.Fixture): A fixture for generating filenames.
    """
    wrangler_config = {
        'module': 'lmpy.data_wrangling.occurrence.unique_localities_wrangler',
        'wrangler_type': 'UniqueLocalitiesFilter'
    }
    factory = WranglerFactory()
    wranglers = factory.get_wranglers([wrangler_config])
    assert len(wranglers) == 1
    assert isinstance(wranglers[0], _DataWrangler)
    assert isinstance(wranglers[0], _OccurrenceDataWrangler)
    assert isinstance(wranglers[0], UniqueLocalitiesFilter)
