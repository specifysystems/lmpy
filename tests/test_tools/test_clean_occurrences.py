"""Test the clean_occurrences tool."""
from lmpy.tools.clean_occurrences import cli


# .....................................................................................
def test_cli(monkeypatch):
    monkeypatch.setattr('sys.argv', ['clean_occurrences.py', '...'])
    cli()


"""
Create or use some occurrence file
Configure some data wranglers
Get output
Check outputs

Optional args to check various headers and report yes / no
"""
