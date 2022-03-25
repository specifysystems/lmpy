"""Data wrangler factory."""
#import data_wrangling.matrix
import lmpy.data_wrangling.occurrence
#import data_wrangling.tree


# .....................................................................................
class WranglerFactory:
    """Factory for configuring data wranglers."""
    def __init__(self):
        self.wrangler_types = {}
        self._load_wranglers()

    def _load_wranglers(self):
        pass

    def get_wranglers(self, wrangler_configs):
        pass

