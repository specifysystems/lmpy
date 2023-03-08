"""Module containing methods to build a grid."""
import math
import numpy as np
import os
from osgeo import ogr, osr

# Calculate this once and store as a constant instead of for every cell
SQRT_3 = math.sqrt(3)


# .............................................................................
def make_polygon_wkt_from_points(points):
    """Create a polygon WKT string from a list of points.

    Args:
        points (list of tuple): A list of (x,y) points for each vertex of the polygon.

    Note:
        Points should be ordered following right hand rule.

    Returns:
        str: A polygon well-known text string.
    """
    points.append(points[0])
    point_strings = ['{} {}'.format(x, y) for x, y in points]
    return 'POLYGON(({}))'.format(','.join(point_strings))


# .............................................................................
def hexagon_wkt_generator(min_x, min_y, max_x, max_y, x_res, y_res):
    """Generator producing hexagonal WKT for cells of the grid.

    Args:
        min_x (numeric): The minimum x value.
        min_y (numeric): The minimum y value.
        max_x (numeric): The maximum x value.
        max_y (numeric): The maximum y value.
        x_res (numeric): The x size of the cell.
        y_res (numeric): The y size of the cell.

    Yields:
        str: Well-known text polygons for the cells.
    """
    y_coord = max_y
    y_row = True
    y_step = -1 * y_res * SQRT_3 / 4
    x_step = x_res * 1.5

    while y_coord > min_y:
        # Every other row needs to be shifted slightly
        x_coord = min_x if y_row else min_x + (x_res * 0.75)

        while x_coord < max_x:
            yield make_polygon_wkt_from_points(
                [
                    (x_coord - (x_res * 0.25), y_coord + (y_res * 0.25) * SQRT_3),
                    (x_coord + (x_res * 0.25), y_coord + (y_res * 0.25) * SQRT_3),
                    (x_coord + (x_res * 0.25), y_coord),
                    (x_coord + (x_res * 0.25), y_coord - (y_res * 0.25) * SQRT_3),
                    (x_coord - (x_res * 0.25), y_coord - (y_res * 0.25) * SQRT_3),
                    (x_coord - (x_res * 0.5), y_coord),
                ]
            )
            x_coord += x_step
        y_row = not y_row
        y_coord += y_step


# .............................................................................
def square_wkt_generator(min_x, min_y, max_x, max_y, x_res, y_res):
    """Generator producing square WKT for cells of the grid.

    Args:
        min_x (numeric): The minimum x value.
        min_y (numeric): The minimum y value.
        max_x (numeric): The maximum x value.
        max_y (numeric): The maximum y value.
        x_res (numeric): The x size of the cell.
        y_res (numeric): The y size of the cell.

    Yields:
        str: Well-known text polygons for the cells.

    Note:
        The function holds UL coordinates (min_x and max_y) static, but LR coordinates
         (max_x, min_y) may change to accommodate the resolution requested.
    """
    y_upper_coords = np.arange(max_y, min_y, -y_res)
    x_left_coords = np.arange(min_x, max_x, x_res)
    for y_coord in y_upper_coords:
        for x_coord in x_left_coords:
            # Coordinates are corners: UL, UR, LR, LL
            yield make_polygon_wkt_from_points(
                [
                    (x_coord, y_coord),
                    (x_coord + x_res, y_coord),
                    (x_coord + x_res, y_coord - y_res),
                    (x_coord, y_coord - y_res),
                ]
            )


# .............................................................................
def build_grid(
    grid_file_name,
    min_x,
    min_y,
    max_x,
    max_y,
    cell_size,
    epsg_code,
    cell_sides,
    site_id='siteid',
    site_x='siteX',
    site_y='siteY',
    cutout_wkt=None,
    logger=None
):
    """Build a grid with an optional cutout.

    Args:
        grid_file_name (str): The location to store the resulting grid.
        min_x (numeric): The minimum value for X of the grid.
        min_y (numeric): The minimum value for Y of the grid.
        max_x (numeric): The maximum value for X of the grid.
        max_y (numeric): The maximum value for Y of the grid.
        cell_size (numeric): The size of each cell (in units indicated by EPSG).
        epsg_code (int): The EPSG code for the new grid.
        cell_sides (int): The number of sides for each cell of the grid.
            4 - square cells, 6 - hexagon cells
        site_id (str): The name of the site id field for the shapefile.
        site_x (str): The name of the X field for the shapefile.
        site_y (str): The name of the Y field for the shapefile.
        cutout_wkt (None or str): WKT for an area of the grid to be cut out.
        logger (lmpy.log.Logger): An optional local logger to use for logging output
            with consistent options

    Returns:
        int: The number of cells in the new grid.

    Raises:
        ValueError: Raised if invalid bbox or cell sides.
    """
    report = {
        "gridname": grid_file_name,
        "site_id_field": site_id,
        "x_field": site_x,
        "y_field": site_y,
        "epsg_code": epsg_code,
        "min_x_coordinate": min_x,
        "max_x_coordinate": max_x,
        "min_y_coordinate": min_y,
        "max_y_coordinate": max_y,
        "cell_sides": cell_sides,
        "size": cell_size
    }
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    if min_x >= max_x or min_y >= max_y:
        raise ValueError(f'Illegal bounds: ({min_x}, {min_y}, {max_x}, {max_y})')
    # We'll always check for intersection to reduce amount of work
    if cutout_wkt is None:
        cutout_wkt = make_polygon_wkt_from_points(
            [(min_x, max_y), (max_x, max_y), (max_x, min_y), (min_x, min_y)]
        )
    selected_poly = ogr.CreateGeometryFromWkt(cutout_wkt)

    # Just in case we decide that these can vary at some point
    x_res = y_res = cell_size

    # Initialize shapefile
    target_srs = osr.SpatialReference()
    target_srs.ImportFromEPSG(epsg_code)

    drv = ogr.GetDriverByName('ESRI Shapefile')
    data_set = drv.CreateDataSource(grid_file_name)

    layer = data_set.CreateLayer(
        data_set.GetName(), geom_type=ogr.wkbPolygon, srs=target_srs
    )
    layer.CreateField(ogr.FieldDefn(site_id, ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn(site_x, ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn(site_y, ogr.OFTReal))

    # Set up generator
    if cell_sides == 4:
        wkt_generator = square_wkt_generator(min_x, min_y, max_x, max_y, x_res, y_res)
    elif cell_sides == 6:
        wkt_generator = hexagon_wkt_generator(min_x, min_y, max_x, max_y, x_res, y_res)
    else:
        raise ValueError(
            'Cannot generate grid cells with {} sides'.format(cell_sides)
        )

    if logger is not None:
        logger.log(
            f"Build {grid_file_name} in EPSG:{epsg_code} with  " +
            f"{cell_sides}-sided cells of {cell_size} size and x-extent {min_x} " +
            f"to {max_x}, y-extent {min_y} to {max_y}.", refname=script_name)

    # Note that site_id is 0-based
    site_headers = []
    shape_id = 0
    for cell_wkt in wkt_generator:
        geom = ogr.CreateGeometryFromWkt(cell_wkt)
        # Check for intersection
        if geom.Intersection(selected_poly):
            feat = ogr.Feature(feature_def=layer.GetLayerDefn())
            feat.SetGeometry(geom)
            centroid = geom.Centroid()
            feat.SetField(site_x, centroid.GetX())
            feat.SetField(site_y, centroid.GetY())
            feat.SetField(site_id, shape_id)
            site_headers.append((shape_id, centroid.GetX(), centroid.GetY()))
            layer.CreateFeature(feat)
            shape_id += 1
        feat.Destroy()
    data_set.Destroy()
    report["size"] = shape_id
    # report["site_headers"] = site_headers
    if logger is not None:
        logger.log(
            f"Wrote {grid_file_name} with {shape_id} sites.", refname=script_name)
    return report


# .............................................................................
__all__ = [
    'build_grid',
    'hexagon_wkt_generator',
    'make_polygon_wkt_from_points',
    'square_wkt_generator',
]
