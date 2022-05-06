# lmpy Tools

lmpy tools are command-line scripts that are included in the system's PATH when the
library is installed.

## Conventions

This repository uses a few conventions in these scripts so that they are consistent.

### cli method

Each script should include a `cli` method that is called in `__main__` and is used to
expose the tool.

### build_parser

The tool should include a `build_parser` method that takes no arguments and returns an
`argparse.ArgumentParser` object.  This method is used for automatic usage
documentation in the Sphinx docs.

### Use `_process_arguments` to support for sending arguments in a configuration file

The `_process_arguments` function from `lmpy.tools._config_parser` takes an
`argparse.ArgumentParser` and a config file option as arguments and returns an
`argparse.Namespace` of processed arguments.  This is a drop in replacement for the
parser's `parse_args` method and it will pull arguments for a configuration file if it
is provided for both optional arguments and positional arguments.  This method allows
for this support without having to add a lot of processing code to your new tool.

### Sphinx documentation

Any new tool should also be accompanied by a matching RST file in
`_sphinx_config/scripts/`.  So a new script file named `lmpy/tools/my_script.py` would
require `_sphinx_config/scripts/my_script.rst` to be created as well that has contents
similar to:

```text
.. sphinx_argparse_cli::
  :module: lmpy.tools.my_script
  :func: build_parser
  :prog: my_script
```

If this documentation file is not included, the build tests will fail.

### Script added to `console_scripts` under `[options.entry_points]` in `setup.cfg`

In `setup.cfg` under `[options.entry_points]` in `console_scripts` add a line for the
new tool like:

```text
[options.entry_points]
console_scripts =
    ... other scripts ...
    my_script = lmpy.tools.my_script:cli

```

## New Tool Boilerplate

Below is some boilerplate that can be used as a starting point for a new tool.

```python
"""This is the module documentation for the tool."""

import argparse

from lmpy.tools._config_parser import _process_arguments


DESCRIPTION = 'Description of the tool.'


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool's parameters.
    """
    parser = argparse.ArgumentParser(
        prog='my_prog_name',
        description=DESCRIPTION
    )
    # The '--config_file' argument is used for providing arguments in a configuration
    #     file instead of the command line
    parser.add_argument('--config_file', type=str, help='Path to configuration file.')
    parser.add_argument(
        '--option_1',
        '-o',
        type=int,
        default=0,
        help='Some optional argument.',
    )
    parser.add_argument(
        'positional_arg_1',
        type=str,
        help='Some positional argument.',
    )
    return parser


# .....................................................................................
def cli():
    """Provide a command-line tool for converting csvs to lmms."""
    parser = build_parser()
    args = _process_arguments(parser, config_args='config_file')
    # ... Do something with the arguments ...


# .....................................................................................
__all__ = ['build_parser', 'cli']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
```
