"""Module containing tools for creating an SDM."""
import glob
from logging import INFO
import os

from lmpy.point import Point, PointCsvWriter
from lmpy.sdm.maxent import (
    create_maxent_model, DEFAULT_MAXENT_OPTIONS, project_maxent_model)
from lmpy.tools.create_rare_species_model import (
    create_rare_species_model, read_points)


# .....................................................................................
def match_headers(mask_filename, tmp_mask_filename, template_layer_filename):
    """Match headers with template layer.

    Args:
        mask_filename: Input filename to update with headers
        tmp_mask_filename: Raster filename fromm which to copy the values above the 6th
        template_layer_filename: Layer filename from which to copy the first 6 values
    """
    with open(mask_filename, mode='wt') as mask_out:
        with open(template_layer_filename, mode='rt') as template_in:
            for _ in range(6):
                mask_out.write(next(template_in))
        with open(tmp_mask_filename, mode='rt') as tmp_mask_in:
            i = 0
            for line in tmp_mask_in:
                i += 1
                if i > 6:
                    mask_out.write(line)


# .....................................................................................
def _create_mask(point_tuples, ecoregions_filename, work_dir, maxent_arguments):
    work_env_dir = os.path.join(work_dir, 'model_layers')
    mask_filename = os.path.join(work_env_dir, 'mask.asc')
    tmp_mask_filename = os.path.join(work_dir, 'tmp_mask.asc')
    create_rare_species_model(
        point_tuples,
        ecoregions_filename,
        tmp_mask_filename
    )
    # Copy headers from one of the environment layers so that they match
    match_headers(
        mask_filename,
        tmp_mask_filename,
        # glob.glob(os.path.join(env_dir, '*.asc'))[0]
        glob.glob(os.path.join(work_env_dir, '*.asc'))[0]
    )
    maxent_arguments += ' togglelayertype=mask'

    return maxent_arguments


# .....................................................................................
def create_sdm(
    min_points, csv_filename, env_dir, ecoregions_filename, work_dir, species_name,
    maxent_arguments=DEFAULT_MAXENT_OPTIONS, sp_key='species_name', x_key='x',
    y_key='y', create_mask=True, logger=None
):
    """Create an SDM, Maxent model if there are enough points, `rare species` if not.

    Args:
        min_points (int): Number of points to determine whether to use Maxent or
            rare-species modeling
        csv_filename (str): input filename with species points
        env_dir (str): directory containing environmental layers for model creation
        ecoregions_filename (str): Vector file containing ecoregions or other
            environmental regions for masking in Maxent or intersecting with a convex
            hull in rare-species model
        work_dir (str): directory for temporary modeling files
        maxent_arguments (str): space-separated values for Maxent parameters
        species_name (str): name to use for the output model filename
        sp_key (str): fieldname of the column containing the species name for grouping
        x_key (str): fieldname of the column containing the longitude coordinate
        y_key (str): fieldname of the column containing the latitude coordinate
        create_mask (bool): flag indicating whether to create a mask for Maxent
        logger (logging.logger): Logger for writing messages to console and/or file.

    Returns:
                output_filename: either model raster filename for rare species model
                    or lambdas filename for Maxent
        report (dict): dictionary containing relevant metadata about the model
    """
    point_tuples = read_points(csv_filename, sp_key, x_key, y_key)
    report = {
        "species": species_name,
        "num_points": len(point_tuples)
    }

    if not os.path.exists(work_dir):
        os.makedirs(work_dir)

    maxent_lambdas_filename = None
    if len(point_tuples) < min_points:
        projected_distribution_filename = os.path.join(work_dir, f'{species_name}.asc')
        log("Create rare species model and map", logger, log_level=INFO)
        create_rare_species_model(
            point_tuples, ecoregions_filename, projected_distribution_filename)
        report["method"] = "rare_species_model"
    else:
        report["method"] = "maxent"
        report["operation"] = "model"
        # Create model env layer directory in work dir
        work_env_dir = os.path.join(work_dir, 'model_layers')
        try:
            os.symlink(env_dir, work_env_dir)
        except FileExistsError:
            pass

        if create_mask:
            maxent_arguments = _create_mask(
                point_tuples, ecoregions_filename, work_dir, maxent_arguments)

        me_csv_filename = os.path.join(work_dir, f"{species_name}.csv")
        with PointCsvWriter(me_csv_filename, ["species_name", "x", "y"]) as writer:
            writer.write_points([Point(species_name, x, y) for x, y in point_tuples])
        log("Create Maxent model", logger, log_level=INFO)
        create_maxent_model(me_csv_filename, work_env_dir, work_dir, maxent_arguments)
        maxent_lambdas_filename = os.path.join(work_dir, f"{species_name}.lambdas")
        projected_distribution_filename = os.path.join(work_dir, f"{species_name}.asc")
        if os.path.exists(maxent_lambdas_filename):
            log(f"Completed Maxent model with lambdas file {maxent_lambdas_filename}",
                logger, log_level=INFO)

        # project_maxent_model(lambdas_filename, work_env_dir, model_raster_filename)

        os.unlink(work_env_dir)
    return projected_distribution_filename, maxent_lambdas_filename, report


# .....................................................................................
def project_sdm(maxent_lambdas_file, env_dir, species_name, work_dir, logger=None):
    """Project a Maxent model onto env. layers for a potential distribution map.

    Note:
        create_sdm creates a raster projected distribution map using the same
        environmental layers as were used for modeling.  This function is intended to
        project an pre-created model onto different environmental layres.

    Args:
        maxent_lambdas_file (str): input filename with Maxent rules
        env_dir (str): directory containing environmental layers for model projection
        work_dir (str): directory for temporary modeling files
        species_name (str): name to use for the output model filename
        logger (logging.logger): Logger for writing messages to console and/or file.

    Returns:
        projection_raster_filename: output filename
        report (dict): dictionary containing relevant metadata about the model
    """
    report = {"species": species_name, "method": "maxent", "operation": "project"}

    maxent_raster_filename = os.path.join(work_dir, f'{species_name}.asc')
    # Create model env layer directory in work dir
    work_env_dir = os.path.join(work_dir, "proj_layers")
    os.symlink(env_dir, work_env_dir)

    log(f"Projecting Maxent model {maxent_lambdas_file} onto map",
        logger, log_level=INFO)
    project_maxent_model(maxent_lambdas_file, env_dir, maxent_raster_filename)
    log(f"Completed projecting Maxent model onto map {maxent_raster_filename}",
        logger, log_level=INFO)

    os.unlink(work_env_dir)
    return maxent_raster_filename, report


# .....................................................................................
def log(msg, logger, log_level=INFO):
    """Log a message.

    Args:
        msg (str): A message to write to the logger.
        logger (logging.logger): Logger for writing messages to console and/or file.
        log_level (int): A level to use when logging the message.
    """
    if logger is not None:
        caller = callersname()
        logger.log(log_level, f"{caller}: {msg}")


# .....................................................................................
def callersname():
    """Find the name of the function from which this method is called.

    Returns:
        The function name.
    """
    import sys
    return sys._getframe(2).f_code.co_name
