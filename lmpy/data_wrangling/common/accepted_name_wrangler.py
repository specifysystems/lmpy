"""Module containing a data wrangler base class for resolving taxon names."""
import json
import requests
import time
import urllib

from lmpy.data_wrangling.base import _DataWrangler


# .....................................................................................
def resolve_names_gbif(names, wait_time=.5):
    """Resolve names using GBIF's taxonomic name resolution service.

    Args:
        names (list of str): A list of name strings to resolve.
        wait_time (number): A number of seconds to wait after each request to avoid
            server ire.

    Returns:
        dict: Input names are keys and resolved name or None are values.
    """
    resolved_names = {}
    for name_str in names:
        # Get name
        other_filters = {'name': name_str.strip(), 'verbose': 'true'}
        url = 'http://api.gbif.org/v1/species/match?{}'.format(
            urllib.parse.urlencode(other_filters))
        response = requests.get(url).json()
        if 'status' in response.keys() and response['status'].lower() in (
            'accepted',
            'synonym'
        ):
            resolved_names[name_str] = response['canonicalName']
        else:
            resolved_names[name_str] = None
        if wait_time is not None:
            time.sleep(wait_time)

    return resolved_names


# .....................................................................................
class _AcceptedNameWrangler(_DataWrangler):
    """Base class for accepted taxon name wranglers."""
    # .......................
    def __init__(
        self,
        name_map=None,
        name_resolver=None,
        out_map_filename=None,
        map_write_interval=100,
        out_map_format='json',
    ):
        """Constructor for the base accepted name wrangler.

        Args:
            name_map (dict or str or None): An existing name mapping.
            name_resolver (Method or None): If provided, this should be a function that
                takes a list of names as input and returns a dictionary of name
                mappings.  If omitted, resolving of new names will be skipped.
            out_map_filename (str): A file location to write the updated name map.
            map_write_interval (int): Update the name map output file after each set of
                this many iterations.
            out_map_format (str): The format to write the names map (csv or json).
        """
        if name_map is not None:
            self._load_name_map(name_map)
        else:
            self.name_map = {}
        self._name_resolver = name_resolver
        self.out_name_map_filename = out_map_filename
        self.map_write_interval = map_write_interval
        self._updated_since_write = 0
        self.out_map_format = out_map_format

    # .......................
    def __del__(self):
        """Destructor method, sync map to disk if needed."""
        if all(
            [
                self.out_name_map_filename is not None,
                self._updated_since_write >= 0
            ]
        ):
            self.write_map_to_file(self.out_name_map_filename, self.out_map_format)

    # .......................
    def _load_name_map(self, name_map):
        """Attempt to load names from the name_map provided.

        Args:
            name_map (dict or str): A mapping dictionary or a filename with names.
        """
        if isinstance(name_map, dict):
            self.name_map = name_map
        else:
            self.name_map = {}
            try:
                # Try to load JSON names
                with open(name_map, mode='rt') as in_json:
                    self.name_map = json.load(in_json)
            except json.JSONDecodeError:  # Not a valid json file, try csv
                with open(name_map, mode='rt') as in_csv:
                    for line in in_csv:
                        in_name, out_name = line.strip().split(',')
                        self.name_map[in_name] = out_name

    # .......................
    def resolve_names(self, names):
        """Attempts to resolve a list of names.

        Args:
            names (list or str): A list of names to resolve.

        Returns:
            dict: A dictionary of input name keys and resolved name values.
        """
        if isinstance(names, str):
            names = [names]
        resolved_names = {}
        unmatched_names = []
        for name in names:
            if name in self.name_map.keys():
                resolved_names[name] = self.name_map[name]
                self.log(f'Resolved name {name} to {self.name_map[name]}')
            else:
                unmatched_names.append(name)
                resolved_names[name] = None
                self.log(f'Could not resolve name {name}')

        # If we have a name resolver and names to resolve, do it
        if self._name_resolver is not None and len(unmatched_names) > 0:
            new_names = self._name_resolver(unmatched_names)
            # Update name map and return dictionary
            self.name_map.update(new_names)
            resolved_names.update(new_names)
            self._updated_since_write += len(new_names.keys())
            if all(
                [
                    self.out_name_map_filename is not None,
                    self._updated_since_write >= self.map_write_interval
                ]
            ):
                self.write_map_to_file(self.out_name_map_filename, self.out_map_format)
                self._updated_since_write = 0

        return resolved_names

    # .......................
    def write_map_to_file(self, filename, output_format, mode='wt'):
        """Write the name map to a file so it can be reused.

        Args:
            filename (str): A file location where the map should be written.
            output_format (str): The format to write the map, either 'csv' or 'json'.
            mode (str): How the file should be opened.
        """
        if output_format.lower() == 'json':
            with open(filename, mode=mode) as out_json:
                json.dump(self.name_map, out_json, indent=4)
            self.log(f'Wrote {len(self.name_map)} names to {filename} as JSON')
        else:
            with open(filename, mode=mode) as out_csv:
                out_csv.write('Name,Accepted\n')
                for in_name, out_name in self.name_map.items():
                    out_csv.write(f'{in_name},{out_name}\n')
            self.log(f'Wrote {len(self.name_map)} names to {filename} as CSV')
