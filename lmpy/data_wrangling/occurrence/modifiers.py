"""Module containing occurrence data wranglers for modifying point data."""
from copy import deepcopy

# import osgeo
from osgeo import osr

from lmpy.point import Point
from lmpy.data_wrangling.occurrence.common import get_occurrence_map


# .............................................................................
def get_accepted_name_modifier(accepted_taxa_filename):
    """Get a data wrangler for populating accepted taxon name for points.

    Args:
        accepted_taxa_filename (str): A file containing accepted taxon names.

    Returns:
        Method: A function for filling in accepted taxon name for points.
    """
    accepted_map = {}
    with open(accepted_taxa_filename, 'r') as in_file:
        _ = next(in_file)
        for line in in_file:
            parts = line.split(',')
            accepted_map[parts[0].strip()] = parts[1].strip()

    # .......................
    def accepted_taxon_wrangler(points):
        return_points = []
        if isinstance(points, Point):
            points = [points]
        for point in points:
            check_sp = point.species_name
            # Check if we don't have an entry for this name
            if check_sp not in accepted_map.keys():
                # We don't have it, it doesn't exist
                new_name = ''
                accepted_map[check_sp] = new_name
            accepted_taxon_name = accepted_map[check_sp]
            if accepted_taxon_name is None or len(accepted_taxon_name) < 2:
                # print('No accepted name for {}'.format(check_sp))
                pass
            else:
                point.species_name = accepted_taxon_name
                return_points.append(point)
        return return_points

    return accepted_taxon_wrangler


# .............................................................................
def get_attribute_modifier(att_name, replace_func):
    """Get a function that replaces an Point attribute using a replace func.

    Args:
        att_name (str): The point attribute to modify.
        replace_func (method): A method that returns a replacement value.

    Returns:
        Method: A function that takes a list of points and returns points with the
            coordinates converted.
    """
    # .......................
    def modify_func(point):
        old_val = point.get_attribute(att_name)
        new_pt = deepcopy(point)
        new_pt.set_attribute(att_name, replace_func(old_val))
        return new_pt

    return get_occurrence_map(modify_func)


# .............................................................................
def get_common_format_modifier(attribute_map):
    """Get a function to convert points to a common format (common attributes).

    Args:
        attribute_map (dict): A map of current attribute name to new attribute
            name.

    Returns:
        Method: A function that takes a list of points and returns points with the
            coordinates converted.
    """
    # .......................
    def modify_func(point):
        new_pt = Point(
            point.species_name, point.x, point.y,
            attributes={
                new_name: point.get_attribute(old_name)
                for old_name, new_name in attribute_map.items()})
        return new_pt

    return get_occurrence_map(modify_func)


# .............................................................................
def get_coordinate_converter_modifier(in_epsg, out_epsg):
    """Get a function to convert points from one coordinate system to another.

    Args:
        in_epsg (int): The EPSG code of the incoming points.
        out_epsg (int): The target EPSG code for output points.

    Returns:
        Method: A function that takes a list of points and returns points with the
            coordinates converted.
    """
    source = osr.SpatialReference()
    source.ImportFromEPSG(in_epsg)

    # TODO: Change this in the future when we require GDAL >= 3
    # if int(osgeo.__version__[0]) >= 3:  # pragma: no cover
    #    # GDAL 3 changes axis order: https://github.com/OSGeo/gdal/issues/1546
    #    source.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

    target = osr.SpatialReference()
    target.ImportFromEPSG(out_epsg)

    transform = osr.CoordinateTransformation(source, target)

    # .......................
    def converter_func(point):
        new_x, new_y, _ = transform.TransformPoint(point.x, point.y)
        pt = deepcopy(point)
        pt.x = new_x
        pt.y = new_y
        return pt

    return get_occurrence_map(converter_func)
