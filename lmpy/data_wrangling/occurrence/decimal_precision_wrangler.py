"""Module containing occurrence data wranglers for filtering points."""
from lmpy.data_wrangling.occurrence.base import _OccurrenceDataWrangler


# .....................................................................................
class DecimalPrecisionFilter(_OccurrenceDataWrangler):
    """Get an occurrence data wrangler for filtering by decimal precision."""
    name = 'DecimalPrecisionFilter'
    version = '1.0'

    # .......................
    def __init__(self, decimal_places, **params):
        """Get an occurrence data wrangler for filtering by decimal precision.

        Args:
            decimal_places (int): Only keep points with at least this many decimal
                places of precision.
            **params (dict): Extra parameters to be sent to the base class.
        """
        self.decimal_places = decimal_places
        _OccurrenceDataWrangler.__init__(self, **params)

    # .......................
    def _pass_condition(self, point):
        """Assessment condition for a point.

        Args:
            point (Point): A point object to assess.

        Returns:
            bool: Indication if the point passed assessment.
        """
        lat_str = str(point.y)
        lon_str = str(point.x)

        try:
            lat_decimals = len(lat_str) - lat_str.index('.') - 1
            lon_decimals = len(lon_str) - lon_str.index('.') - 1
        except ValueError:
            # TODO: Handle numbers with 'e' example: 1e-05
            return False
        return min([lat_decimals, lon_decimals]) >= self.decimal_places
