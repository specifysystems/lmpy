"""Test the occurrence data wrangler factory module."""
import json
import pytest

from lmpy.data_wrangling.occurrence.factory import wrangler_factory


# ............................................................................
class Test_wrangler_factory:
    """Test the occurrence data wrangler factory."""
    # .......................
    def test_wrangler_config(self, occurrence_wrangler_configuration):
        """Test wrangler configurations."""
        with open(occurrence_wrangler_configuration) as in_file:
            config = json.load(in_file)
        wrangler = wrangler_factory(config)
