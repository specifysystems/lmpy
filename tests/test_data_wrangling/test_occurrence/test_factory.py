"""Test the occurrence data wrangler factory module."""
import json
import os

from lmpy.data_wrangling.occurrence.factory import wrangler_factory


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
        with open(occurrence_wrangler_configuration) as in_file:
            raw_string = in_file.read()
            config = json.loads(
                raw_string.replace(
                    '$THIS_DIR$',
                    os.path.dirname(
                        occurrence_wrangler_configuration).replace(
                        '\\', '/')))
        wrangler = wrangler_factory(config)
        assert wrangler
