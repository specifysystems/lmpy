"""Module containing SpeciesList class."""


# .....................................................................................
class SpeciesList(set):
    """A class containing a list of species for analysis."""
    # .......................
    def __init__(self, *args, **kwargs):
        """Constructor for SpeciesList.

        Args:
            *args (list of object): A list of positional arguments to send to `list`.
            **kwargs (dict): A dictionary of keyword arguments to send to `list`.
        """
        super().__init__(*args, **kwargs)
