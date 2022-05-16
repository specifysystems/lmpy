"""Module containing Occurrence Data Wrangler base class."""
from lmpy.data_wrangling.base import _DataWrangler


# .....................................................................................
class _OccurrenceDataWrangler(_DataWrangler):
    """Occurrence data wrangler base class."""
    name = '_OccurrenceDataWrangler'

    # .......................
    def __init__(
        self,
        store_attribute=None,
        pass_value=0,
        fail_value=1,
        **params
    ):
        """Constructor for _OcccurrenceDataWrangler base class.

        Args:
            store_attribute (str or None): If provided, add an assessment field to the
                point.
            pass_value (object): If the point passes the assessment, set the field to
                this value.
            fail_value (object): If the point fails the assessment, set the field to
                this value.
            **params (dict): A dictionary of keyword parameters.
        """
        _DataWrangler.__init__(self, **params)
        self.assessed = 0
        self.filtered = 0
        self.modified = 0

        self.store_attribute = store_attribute
        self.pass_value = pass_value
        self.fail_value = fail_value

    # .......................
    def _modify_point(self, point):
        """A function that modifies a Point object as needed.

        The base class version is a dummy function that returns the input point.

        Args:
            point (Point): A point object to  modify.

        Returns:
            Point, bool: Return the provided point and False indicating that it was not
                modified.
        """
        return point, False

    # .......................
    def _pass_condition(self, point):
        """A function that determines if a point passes some criteria.

        The base class version always passes.

        Args:
            point (Point): A point object to assess.

        Returns:
            bool: Indication if the point passes the test condition.
        """
        return True

    # .......................
    def get_report(self):
        """Get a report of the wrangler's functioning.

        Returns:
            dict: A dictionary of wrangler outputs.
        """
        self.report['assessed'] = self.assessed
        self.report['modified'] = self.modified
        self.report['filtered'] = self.filtered
        return self.report

    # .......................
    def report_point(self, filtered=False, modified=False):
        """Report the result of wrangling a point.

        Args:
            filtered (bool): Was the point filtered.
            modified (bool): Was the point modified.
        """
        self.assessed += 1
        self.modified += int(modified)
        self.filtered += int(filtered)

    # .......................
    def wrangle_points(self, points):
        """Wrangle occurrence `Point` objects.

        Args:
            points (list of Point): A list of points to wrangle.

        Returns:
            list of point: A list of wrangled occurrnece points.
        """
        wrangled_points = []
        for point in points:
            pt = self.wrangle_single_point(point)
            if pt is not None:
                wrangled_points.append(pt)
        return wrangled_points

    # .......................
    def wrangle_single_point(self, point):
        """Wrangle a single point.

        Args:
            point (Point): A point object to wrangle.

        Returns:
            Point or None: An assessed and / or modified point or None if filtered.
        """
        # Do any modifications necessary for the point
        mod_point, is_modified = self._modify_point(point)
        is_filtered = False
        val = self.pass_value

        # Check if the point passes the pass condition
        if not self._pass_condition(point):
            is_filtered = True
            val = self.fail_value

        # If we should just assess the point, set the attribute
        if self.store_attribute is not None:
            mod_point.set_attribute(self.store_attribute, val)
            is_modified = True
        elif is_filtered:
            # If it was filtered and we should remove, do so
            mod_point = None

        self.report_point(filtered=is_filtered, modified=is_modified)
        if is_filtered:
            self.log('Filtered a point.')
        if is_modified:
            self.log('Modified a point.')

        return mod_point
