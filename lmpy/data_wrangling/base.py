"""Module containing base class for data wranglers."""

# .....................................................................................
class _DataWrangler:
    """Data wrangler base class."""
    name = '_DataWrangler'
    inputs = None
    # If inputs, this should be a list of (name, type, description) tuples

    # ........................

    def get_report(self):
        pass
