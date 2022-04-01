"""Module containing a coordinate converter modifier."""
from copy import deepcopy

from osgeo import osr

from lmpy.data_wrangling.occurrence.base import _OccurrenceDataWrangler


# .....................................................................................
def get_srs_for_epsg(epsg):
    """Get a osr.SpatialReference for the specified EPSG code.

    Args:
        epsg (int): An EPSG code to get the SpatialReference for.

    Returns:
        SpatialReference: A spatial reference object for the EPSG.
    """
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)

    try:
        # So we can use GDAL 2 or 3
        # See https://github.com/OSGeo/gdal/issues/1546
        srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    except Exception as err:  # pragma: no cover
        print('Error setting mapping strategy')
        print(err)

    return srs


# .....................................................................................
class CoordinateConverterWrangler(_OccurrenceDataWrangler):
    """Tool for converting fron one coordinate system to another via ESPG."""
    name = 'CoordinateConverterWrangler'
    version = '1.0'

    # .......................
    def __init__(
        self,
        target_epsg,
        source_epsg=None,
        epsg_attribute=None,
        original_x_attribute=None,
        original_y_attribute=None,
        **params
    ):
        """Constructor for CoordinateConverterModifier class.

        Args:
            target_epsg (int): Target map projection specified by EPSG code.
            source_epsg (int or None): Source map projection specified by EPSG code.
            epsg_attribute (str or None): A point attribute containing EPSG code.
            original_x_attribute (str or None): An attribute to store the original x
                value.
            original_y_attribute (str or None): An attribute to store the original y
                value.
            **params (dict): Extra parameters to be sent to the base class.
        """
        self.source_epsg = source_epsg
        self.epsg_attribute = epsg_attribute
        self.original_x_attribute = original_x_attribute
        self.original_y_attribute = original_y_attribute

        _OccurrenceDataWrangler.__init__(self, **params)
        self.target_sr = get_srs_for_epsg(target_epsg)
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
            epsg = int(self.source_epsg)
        else:
            epsg = int(point.get_attribute(self.epsg_attribute))

        if epsg in self.transforms.keys():
            transform = self.transforms[epsg]
        else:
            source_sr = get_srs_for_epsg(epsg)
            transform = osr.CoordinateTransformation(source_sr, self.target_sr)
            self.transforms[epsg] = transform

        new_x, new_y, _ = transform.TransformPoint(point.x, point.y)
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
            point (Point): A point object to assess.

        Returns:
            bool: Indication if the point passes the test condition.
        """
        if point.x is None or point.y is None:
            return False
        return True
