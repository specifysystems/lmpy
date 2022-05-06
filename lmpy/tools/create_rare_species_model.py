"""Create a rare species model by intersecting convex hull and ecoregions."""
import argparse
import os
import tempfile

import numpy as np
from osgeo import gdal, gdalconst, ogr, osr

from lmpy.point import PointCsvReader
from lmpy.tools._config_parser import _process_arguments


DESCRIPTION = '''\
Create a "rare species" model by intersecting the convex hull for a group of
occurrences with the ecoregions those points fall within and then rasterizing the
result.'''

# Raster formats
AUTO_FORMAT = 'auto'
ASC_FORMAT = 'AAIGrid'
TIF_FORMAT = 'GTiff'


# .....................................................................................
def create_rare_species_model(
    points,
    ecoregions_filename,
    model_raster_filename,
    raster_format=AUTO_FORMAT,
    nodata_value=-9999,
    burn_value=50,
):
    """Create a rare species model from a convex hull intersected with ecoregions.

    Args:
        points (list of Point): A list of occurrence points to use for model.
        ecoregions_filename (str): The file location for the ecoregions data.
        model_raster_filename (str): The file location to write the model raster.
        raster_format (str): The output raster format (default: auto - use filename).
        nodata_value (int): The value to use for nodata in the model raster.
        burn_value (int): The burn value to use for model presence.
    """
    # Get the desired output raster format, either provided or determine
    raster_format = get_raster_format(raster_format, model_raster_filename)

    # Get ecoregions array
    (
        ecoregion_data,
        min_x,
        min_y,
        max_x,
        max_y,
        cell_size,
        epsg,
    ) = get_ecoregions_array(ecoregions_filename)
    num_rows, num_cols = ecoregion_data.shape

    # Get convex hull array
    val_set = set()
    geom_collection = ogr.Geometry(ogr.wkbGeometryCollection)
    # Process points
    for pt in points:
        # Add geometry to collection
        pt_geom = ogr.Geometry(ogr.wkbPoint)
        pt_geom.AddPoint(pt[0], pt[1])
        geom_collection.AddGeometry(pt_geom)
        # Add to value set
        col = int((pt[0] - min_x) / cell_size)
        row = int((max_y - pt[1]) / cell_size)
        val_set.add(ecoregion_data[row, col])
    # Convex hull
    convex_hull_raw = geom_collection.ConvexHull()

    convex_hull_data = get_convex_hull_array(
        convex_hull_raw, num_cols, num_rows, cell_size, min_x, max_y, epsg, burn_value
    )

    # Create model
    model_data = nodata_value * np.ones(ecoregion_data.shape, dtype=int)
    for i in range(ecoregion_data.shape[0]):
        for j in range(ecoregion_data.shape[1]):
            if ecoregion_data[i, j] in val_set and convex_hull_data[i, j] == burn_value:
                model_data[i, j] = burn_value

    # Write model
    if raster_format == ASC_FORMAT:
        write_ascii(
            model_raster_filename, model_data, cell_size, min_x, min_y, nodata_value
        )
    else:
        write_tiff(
            model_raster_filename,
            model_data,
            cell_size,
            min_x,
            max_y,
            epsg,
            nodata_value,
        )


# .....................................................................................
def get_convex_hull_array(
    convex_hull_geom,
    num_cols,
    num_rows,
    cell_size,
    min_x,
    max_y,
    epsg,
    burn_value,
    buffer_distance=0.5,
    num_quad_segs=30,
):
    """Create a convex hull array.

    Args:
        convex_hull_geom (geometry): Convex hull geometry for a set of points.
        num_cols (int): The number of columns in the array.
        num_rows (int): The number of rows in the array.
        cell_size (number): The size of each cell in map units.
        min_x (number): The minimum x value in the raster.
        max_y (number): The maximum y value in the raster.
        epsg (int): The EPSG code of the map projection to use.
        burn_value (number): A value to burn into the raster for the convex hull.
        buffer_distance (number): A buffer distance to add to the convex hull.
        num_quad_segs (int): The number of segments to use for buffering.

    Returns:
        numpy.ndarray: Convex hull data converted to an array.
    """
    buffered_convex_hull = convex_hull_geom.Buffer(buffer_distance, num_quad_segs)
    tmp_shp_filename = tempfile.NamedTemporaryFile(suffix='.shp', delete=True).name
    tmp_tif_filename = tempfile.NamedTemporaryFile(suffix='.tif', delete=True).name

    shp_drv = ogr.GetDriverByName('ESRI Shapefile')

    # Create the convex hull shapefile
    out_ds = shp_drv.CreateDataSource(tmp_shp_filename)
    out_lyr = out_ds.CreateLayer('ConvexHull', geom_type=ogr.wkbPolygon)

    # Add an ID field
    id_field = ogr.FieldDefn('id', ogr.OFTInteger)
    out_lyr.CreateField(id_field)

    # Create the feature
    feat_defn = out_lyr.GetLayerDefn()
    feat = ogr.Feature(feat_defn)
    feat.SetGeometry(buffered_convex_hull)
    feat.SetField('id', 1)
    out_lyr.CreateFeature(feat)
    feat = None

    # Rasterize the shapefile
    tiff_drv = gdal.GetDriverByName('GTiff')
    rst_ds = tiff_drv.Create(
        tmp_tif_filename, num_cols, num_rows, 1, gdalconst.GDT_Int16
    )
    rst_ds.SetGeoTransform([min_x, cell_size, 0, max_y, 0, -cell_size])

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)
    rst_ds.SetProjection(srs.ExportToWkt())

    gdal.RasterizeLayer(rst_ds, [1], out_lyr, burn_values=[burn_value])

    rst_ds.FlushCache()

    out_ds = None
    rst_ds = None

    # Get the data array
    rst_ds = gdal.Open(tmp_tif_filename)
    band = rst_ds.GetRasterBand(1)
    data = np.array(band.ReadAsArray())

    return data


# .....................................................................................
def get_ecoregions_array(ecoregions_filename):
    """Get ecoregions data array.

    Args:
        ecoregions_filename (str): File location of ecoregions data.

    Returns:
        tuple: (Ecoregion data as numpy array, min x, min y, max x, max y, cell size)
    """
    region_ds = gdal.Open(ecoregions_filename)
    reg_band = region_ds.GetRasterBand(1)
    num_cols = region_ds.RasterXSize
    num_rows = region_ds.RasterYSize
    min_x, cell_size, _, max_y, _, _ = region_ds.GetGeoTransform()
    min_y = max_y - (cell_size * num_rows)
    max_x = min_x + (num_cols * cell_size)

    proj = osr.SpatialReference(wkt=region_ds.GetProjection())
    epsg = int(proj.GetAttrValue('AUTHORITY', 1))

    ecoregion_data = reg_band.ReadAsArray(0, 0, num_cols, num_rows)
    region_ds = None

    return ecoregion_data, min_x, min_y, max_x, max_y, cell_size, epsg


# .....................................................................................
def get_raster_format(provided_format, model_raster_filename):
    """Get the output raster format.

    Args:
        provided_format (str): The user provided raster format.
        model_raster_filename (str): The model raster output filename.

    Returns:
        str: The output raster format string (ASC_FORMAT or TIF_FORMAT).
    """
    if provided_format in [ASC_FORMAT, TIF_FORMAT]:
        # If provided format is known, use it, else we'll determine it
        return provided_format
    elif os.path.splitext(model_raster_filename)[1].lower() == '.asc':
        # If model filename ends in .asc, use ASCII format
        return ASC_FORMAT
    return TIF_FORMAT


# .....................................................................................
def read_points(csv_filename, sp_key, x_key, y_key):
    """Read points from a csv file.

    Args:
        csv_filename (str): Path to CSV file containing occurrence records.
        sp_key (str): The CSV column header containing species information.
        x_key (str): The CSV column header containing X values.
        y_key (str): The CSV column header containing Y values.

    Returns:
        list of (float, float) tuples: A list of (x, y) tuples for occurrences.
    """
    point_set = set()
    with PointCsvReader(csv_filename, sp_key, x_key, y_key) as reader:
        for points in reader:
            point_set = point_set.union({(pt.x, pt.y) for pt in points})
    return list(point_set)


# .....................................................................................
def write_ascii(out_filename, model_data, cell_size, min_x, min_y, nodata_value):
    """Write model data to ascii file.

    Args:
        out_filename (str): The file location to write the raster.
        model_data (numpy.ndarray): Raster data in the form of a matrix or array.
        cell_size (number): The desired size of each raster cell in map units.
        min_x (number): The minimum x value for the raster in map units.
        min_y (number): The minimum y value for the raster in map units.
        nodata_value (number): The value to be considered "nodata" in the raster.
    """
    with open(out_filename, mode='wt') as out_f:
        out_f.write('ncols      {}\n'.format(model_data.shape[1]))
        out_f.write('nrows      {}\n'.format(model_data.shape[0]))
        out_f.write('xllcorner  {}\n'.format(min_x))
        out_f.write('yllcorner  {}\n'.format(min_y))
        out_f.write('cellsize   {}\n'.format(cell_size))
        out_f.write('NODATA_value       {}\n'.format(nodata_value))
        np.savetxt(out_f, model_data, fmt='%i')


# .....................................................................................
def write_tiff(out_filename, model_data, cell_size, min_x, max_y, epsg, nodata_value):
    """Write model data to tiff file.

    Args:
        out_filename (str): The file location to write the raster.
        model_data (numpy.ndarray): Raster data in the form of a matrix or array.
        cell_size (number): The desired size of each raster cell in map units.
        min_x (number): The minimum x value for the raster in map units.
        max_y (number): The maximum y value for the raster in map units.
        epsg (int): The EPSG code to use to define the map projection.
        nodata_value (number): The value to be considered "nodata" in the raster.
    """
    drv = gdal.GetDriverByName('GTiff')
    dataset = drv.Create(
        out_filename, model_data.shape[1], model_data.shape[0], 1, gdalconst.GDT_Byte
    )
    dataset.SetGeoTransform([min_x, cell_size, 0, max_y, 0, -cell_size])

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)
    dataset.SetProjection(srs.ExportToWkt())

    out_band = dataset.GetRasterBand(1)
    out_band.WriteArray(model_data)
    out_band.FlushCache()
    out_band.SetNoDataValue(nodata_value)


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool's parameters.
    """
    parser = argparse.ArgumentParser(
        prog='create_rare_species_model',
        description=DESCRIPTION,
    )
    parser.add_argument('--config_file', type=str, help='Path to configuration file.')
    parser.add_argument(
        '--species_column',
        '-sp',
        type=str,
        default='species_name',
        help='CSV column for species or group name.',
    )
    parser.add_argument(
        '--x_column',
        '-x',
        type=str,
        default='x',
        help='CSV column containing x coordinate (ex. longitude).',
    )
    parser.add_argument(
        '--y_column',
        '-y',
        type=str,
        default='y',
        help='CSV column containing y coordinate (ex. latitude).',
    )
    parser.add_argument(
        '--burn_value',
        '-b',
        type=int,
        default=50,
        help='Raster burn value for model presence.',
    )
    parser.add_argument(
        '--nodata_value',
        '-n',
        type=int,
        default=-9999,
        help='Raster nodata value for model absence.',
    )
    parser.add_argument(
        '--output_format',
        '-of',
        type=str,
        choices=['auto', 'AAIGrid', 'GTiff'],
        default='auto',
        help=(
            'The output format for the model raster.'
            '(AAIGrid -> Ascii Grid, GTiff -> GeoTiff, auto -> Choose by filename.'
        ),
    )
    parser.add_argument(
        'point_csv_filename', type=str, help='File location of an occurrence csv file.'
    )
    parser.add_argument(
        'ecoregions_filename', type=str, help='File location of ecoregions raster file.'
    )
    parser.add_argument(
        'model_raster_filename',
        type=str,
        help='File location to write the model raster file.',
    )
    return parser


# .....................................................................................
def cli():
    """Command-line interface for creating a rare species model."""
    parser = build_parser()
    args = _process_arguments(parser, config_arg='config_file')

    # Read points
    points = read_points(
        args.point_csv_filename, args.species_column, args.x_column, args.y_column
    )
    # Create model
    create_rare_species_model(
        points,
        args.ecoregions_filename,
        args.model_raster_filename,
        raster_format=args.output_format,
        nodata_value=args.nodata_value,
        burn_value=args.burn_value,
    )


# .....................................................................................
__all__ = ['build_parser', 'cli', 'create_rare_species_model', 'write_tiff']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
