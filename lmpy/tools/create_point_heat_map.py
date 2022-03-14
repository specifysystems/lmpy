"""Create a heat map for occurrence data."""
import argparse

from osgeo import gdal
from osgeo.osr import SpatialReference, CoordinateTransformation
import numpy as np

from lmpy.point import PointCsvReader


# .....................................................................................
def get_point_to_xy_func(point_epsg, map_epsg, bbox, resolution):
    """Get a translation function that takes a point as an argument and returns (x, y).

    Args:
        point_epsg (int): The EPSG code (map projection) to convert from.
        map_epsg (int): The EPSG code (map projection) to convert to.
        bbox (tuple of 4 numbers): A bounding box for the map raster.
        resolution (number): The cell size of the map raster cells in map units.

    Returns:
        Method: A function taking a Point as an argument and returning an x,y tuple.
    """
    if point_epsg == map_epsg:

        def convert_func(point):
            """Just get the x,y values of the point.

            Args:
                point (Point): A point object to convert.

            Returns:
                tuple: A tuple of (x, y, 0).
            """
            return (point.x, point.y, 0)

    else:
        pt_epsg_sr = SpatialReference()
        pt_epsg_sr.ImportFromEPSG(point_epsg)
        map_epsg_sr = SpatialReference()
        map_epsg_sr.ImportFromEPSG(map_epsg)
        coordinate_transform = CoordinateTransformation(pt_epsg_sr, map_epsg_sr)

        def convert_func(point):
            """Transform the point from one coordinate system to another.

            Args:
                point (Point): A point object to convert.

            Returns:
                tuple: A tuple of (x, y, 0).
            """
            return coordinate_transform.TransformPoint(point.x, point.y)

    # ................................
    def pt_to_xy(point):
        """Convert Point to (x, y).

        Args:
            point (Point): A point object to convert.

        Returns:
            tuple: A tuple of (x, y) or (None, None).
        """
        x, y = convert_func(point)
        if bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]:
            return (int((y - bbox[1]) / resolution), int((x - bbox[0]) / resolution))
        return None, None

    return pt_to_xy


# .....................................................................................
def create_heat_map(
    points, point_epsg, bbox, resolution, map_epsg, map_filename, nodata_val=-9999
):
    """Create a heat map matrix for the provided points.

    Args:
        points (list of Point): A list of Point objects.
        point_epsg (int): The EPSG code of the point data (map projection).
        bbox (float, float, float, float): The bounding box to use for the map.
        resolution (float): The size of each map cell (in map projection units).
        map_epsg (int): The EPSG code (map projection) to use for the map.
        map_filename (str): The file location to write the map.
        nodata_val (number): A value to use as the nodata value for the raster.
    """
    # Create a map array
    num_rows = np.ceil((bbox[3] - bbox[1]) / resolution)
    num_cols = np.ceil((bbox[2] - bbox[0]) / resolution)
    data = np.zeros((num_rows, num_cols), dtype=int) * nodata_val

    # Get point to cell function
    pt_to_xy = get_point_to_xy_func(point_epsg, map_epsg, bbox, resolution)

    # Process points
    for point in points:
        pt_x, pt_y = pt_to_xy(point)
        # Only try to add to array if point is within range
        if pt_x is not None and pt_y is not None:
            # Set the value to max(val+1, 1) to deal with nodata
            data[pt_y, pt_x] = max(data[pt_y, pt_x] + 1, 1)

    # Write map
    drv = gdal.GetDriverByName('GTiff')
    dataset = drv.Create(map_filename, num_cols, num_rows, 1, gdal.GDT_Int)
    out_band = dataset.GetRasterBand(1)
    out_band.WriteArray(data)
    out_band.FlushCache()
    out_band.SetNoDataValue(nodata_val)
    # dataset.SetGeoTransform(map_transform)
    srs = SpatialReference()
    srs.ImportFromEPSG(map_epsg)
    dataset.SetProjection(srs.ExportToWkt())
    dataset = None


# .....................................................................................
def cli():
    """Function providing command-line interface for the tool."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--point_epsg',
        type=int,
        default=4326,
        help='The EPSG code of the map projection used for the points.',
    )
    parser.add_argument(
        '--map_epsg',
        type=int,
        default=4326,
        help='The EPSG code of the map projection to use for generating the heat map.',
    )
    parser.add_argument(
        'point_csv_filename', type=str, help='A CSV file containing point data.'
    )
    parser.add_argument(
        'species_key', type=str, help='The key used for grouping (species name).'
    )
    parser.add_argument(
        'x_key', type=str, help='The header key for the x column (longitude).'
    )
    parser.add_argument(
        'y_key', type=str, help='The header key for the y column (latitude).'
    )
    parser.add_argument(
        'min_x', type=float, help='The minimum x value for the map bounding box.'
    )
    parser.add_argument(
        'min_y', type=float, help='The minimum y value for the map bounding box.'
    )
    parser.add_argument(
        'max_x', type=float, help='The maximum x value for the map bounding box.'
    )
    parser.add_argument(
        'max_y', type=float, help='The maximum y value for the map bounding box.'
    )
    parser.add_argument(
        'map_resolution',
        type=float,
        help='The size of each map cell (in appropriate map units).',
    )
    parser.add_argument(
        'map_filename', type=str, help='The file location to write the map.'
    )
    args = parser.parse_args()

    points = []
    with PointCsvReader(
        args.point_csv_filename, args.species_key, args.x_key, args.y_key
    ) as reader:
        for pts in reader:
            points.extend(pts)

    create_heat_map(
        points,
        args.point_epsg,
        (args.min_x, args.min_y, args.max_x, args.max_y),
        args.map_resolution,
        args.map_epsg,
        args.map_filename,
    )


# .....................................................................................
__all__ = ['cli', 'create_heat_map', 'get_point_to_xy_func']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
