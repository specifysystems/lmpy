"""Data wrangler factory."""
import importlib
import inspect

from lmpy.data_wrangling.base import _DataWrangler


# .....................................................................................
class WranglerFactory:
    """Factory for configuring data wranglers."""

    # .......................
    def __init__(self):
        """Constructor for the WranglerFactory class."""
        self.wrangler_types = {}
        self._load_wranglers()

    # .......................
    def _load_wranglers(self):
        """Load possible data wrangler types."""

        def _find_data_wranglers(base_module, base_class):
            """Recursive function for finding data wranglers for factory.

            Args:
                base_module (Module): A python module to traverse.
                base_class (Class): Returned classes should be subclasses of this.
            """
            for element_name in dir(base_module):
                # Ignore anything that starts with an underscore
                if not element_name.startswith("_"):
                    # Check the element
                    element = getattr(base_module, element_name)

                    if inspect.isclass(element) and issubclass(element, base_class):
                        # If we found a subclass of our base class, add it
                        self.wrangler_types[element.name] = element
                    elif inspect.ismodule(element) and element.__package__.startswith(
                        base_module.__package__
                    ):
                        # If this is a submodule of the provided module, recurse
                        _find_data_wranglers(element, base_class)

        # Load data_wrangling package now to avoid circular imports
        _find_data_wranglers(
            importlib.import_module("lmpy.data_wrangling"), _DataWrangler
        )

    # .......................
    def get_wranglers(self, wrangler_configs):
        """Get configured data wranglers.

        Args:
            wrangler_configs (list of dicts): A list of wrangler configuration
                dictionaries.

        Returns:
            list of _DataWrangler subclasses: A List of configured data wranglers.
        """
        if isinstance(wrangler_configs, dict):
            wrangler_configs = [wrangler_configs]

        return [
            self.wrangler_types[config["wrangler_type"]].from_config(
                config
            )
            for config in wrangler_configs
        ]
