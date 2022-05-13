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

    # .......................
    @classmethod
    def from_file(cls, filename):
        """Get a species list from a file.

        Args:
            filename (str): File path of a species list to load.

        Returns:
            SpeciesList: A species list loaded from a file.
        """
        with open(filename, mode='rt') as in_file:
            species = [line.replace('\n', '').strip() for line in in_file]
        return SpeciesList(species)

    # .......................
    def write(self, filename):
        """Write the species list to a file.

        Args:
            filename (str): Path where the species list data should be written.
        """
        with open(filename, mode='wt') as out_file:
            for name in self:
                out_file.write(f'{name}\n')
