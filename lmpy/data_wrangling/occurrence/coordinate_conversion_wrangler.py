"""Module containing a coordinate converter modifier."""
from copy import deepcopy

from osgeo import osr

from lmpy.data_wrangling.occurrence.base import _OccurrenceDataWrangler


# .....................................................................................
class CoordinateConverterWrangler(_OccurrenceDataWrangler):
    """Tool for converting fron one coordinate system to another via ESPG."""

    # .......................
    def __init__(
        self,
        target_epsg,
        source_epsg=None,
        epsg_attribute=None,
        store_attribute=None,
        pass_value=0,
        fail_value=1,
        original_x_attribute=None,
        original_y_attribute=None,
    ):
        """CoordinateConverterModifier constructor.

        Args:
            target_epsg (int): Target map projection specified by EPSG code.
            source_epsg (int or None): Source map projection specified by EPSG code.
            epsg_attribute (str or None): A point attribute containing EPSG code.
            store_attribute (str or None): A new point attribute to store assessment.
            pass_value (Object): A value to set when the point passess assessment.
            fail_value (Object): A value to set when the point fails assessment.
            original_x_attribute (str or None): An attribute to store the original x
               value.
            original_y_attribute (str or None): An attribute to store the original y
               value.
        """
        self.source_epsg = source_epsg
        self.epsg_attribute = epsg_attribute
        self.original_x_attribute = original_x_attribute
        self.original_y_attribute = original_y_attribute

        _OccurrenceDataWrangler.__init__(
            self,
            store_attribute=store_attribute,
            pass_value=pass_value,
            fail_value=fail_value,
        )
        self.target_sr = osr.SpatialReference()
        self.target_sr.ImportFromEPSG(target_epsg)
        self.transforms = {}

    # .......................
    def _modify_point(self, point):
        """Transform the point coordinates.

        Args:
            point (Point): The point object to modify.

        Returns:
            Point and bool: A modified (or not) Point and boolean indicating if it was
                modified.
        """
        if self.source_epsg is not None:
            epsg = self.source_epsg
        else:
            epsg = point.get_attribute(self.epsg_attribute)

        if epsg in self.transforms.keys():
            transform = self.transforms[epsg]
        else:
            source_sr = osr.SpatialReference()
            source_sr.ImportFromEPSG(epsg)
            transform = osr.CoordinateTransformation(source_sr, self.target_sr)
            self.transforms[epsg] = transform

        new_x, new_y, _ = transform.TransformPoint(point.y, point.x)
        pt = deepcopy(point)
        pt.x = new_x
        pt.y = new_y
        # If we should keep the original values, do so
        if all(
            [
                self.original_x_attribute is not None,
                self.original_y_attribute is not None
            ]
        ):
            pt.set_attribute(self.original_x_attribute, point.x)
            pt.set_attribute(self.original_y_attribute, point.y)

        return pt, True

    # .......................
    def _pass_condition(self, point):
        """Pass condition for coordinate conversion.

        Args:

        Returns:
            bool: Indication if the point passes the test condition.
        """
        if point.x is None or point.y is None:
            return False
        return True
