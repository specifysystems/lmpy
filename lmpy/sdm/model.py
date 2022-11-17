"""Module containing tools for creating an SDM."""
import glob
from logging import INFO
import os
from pathlib import Path

from lmpy.point import Point, PointCsvWriter
from lmpy.sdm.maxent import (
    create_maxent_model, DEFAULT_MAXENT_OPTIONS, project_maxent_model)
from lmpy.tools.create_rare_species_model import (
    create_rare_species_model, read_points)


script_name = os.path.splitext(os.path.basename(__file__))[0]


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
def _create_mask(
        point_tuples, ecoregions_filename, env_dir, maxent_arguments, logger):
    mask_filename = os.path.join(env_dir, 'mask.asc')
    tmp_mask_filename = os.path.join(env_dir, 'tmp_mask.asc')

    # Identify one environment layer (not a mask or temp mask) to copy headers from
    files = glob.glob(os.path.join(env_dir, '*.asc'))
    env_lyr_filename = files[0]

    create_rare_species_model(
        point_tuples,
        ecoregions_filename,
        tmp_mask_filename
    )
    # Copy headers
    match_headers(
        mask_filename,
        tmp_mask_filename,
        env_lyr_filename
    )
    if logger:
        logger.log(
            f"Created mask {mask_filename} for current SDM",
            refname=script_name, log_level=INFO)
    # Remove tmp_mask after mask is created and matched
    if os.path.exists(tmp_mask_filename):
        os.remove(tmp_mask_filename)
    maxent_arguments += ' togglelayertype=mask'

    return maxent_arguments, mask_filename


# .....................................................................................
def create_maxent_layer_label(sdm_dir, label_name, touch_file=True):
    """Return a filename to indicate a layer label for an SDM raster in the directory.

    Args:
        sdm_dir (str): Path for output file, same as the dir for associated matrix input
        label_name (str): Name to use in matrix headers
        touch_file (bool): True to create the file

    Returns:
        label_filename (str): File signaling the

    Note:
        This function assumes that only one SDM to be encoded will be in the same
            directory.
    """
    label_filename = os.path.join(sdm_dir, f'{label_name}.label')
    if touch_file is True:
        Path(label_filename).touch(exist_ok=True)
    return label_filename


# .....................................................................................
def create_sdm(
    min_points, csv_filename, env_dir, ecoregions_filename, work_dir, species_name,
    maxent_arguments=DEFAULT_MAXENT_OPTIONS, sp_key=Point.SPECIES_ATTRIBUTE,
    x_key=Point.X_ATTRIBUTE, y_key=Point.Y_ATTRIBUTE, create_mask=True, logger=None
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
    std_species_name = Point.standardize_species_name(species_name)
    # std_file_basename = f"{std_species_name.replace(' ', '_')}"
    point_tuples = read_points(csv_filename, sp_key, x_key, y_key)
    report = {
        "species": std_species_name,
        "num_points": len(point_tuples)
    }

    if not os.path.exists(work_dir):
        os.makedirs(work_dir)

    if len(point_tuples) < min_points:
        proj_distribution_filename = os.path.join(work_dir, f'{std_species_name}.asc')
        if logger:
            logger.log(
                "Create rare species model and map", refname=script_name,
                log_level=INFO)
        create_rare_species_model(
            point_tuples, ecoregions_filename, proj_distribution_filename)
        report["method"] = "rare_species_model"
        report["projected_distribution_file"] = proj_distribution_filename
    else:
        report["method"] = "maxent"
        # Maxent creates SDM filenames from occurrence filenames replacing spaces
        # with underscores.  To keep track of the correct label, create an empty file
        # in the same directory with the original name.  This can inform the label used
        # on a species column when encoding a layer for a PAM.
        _ = create_maxent_layer_label(work_dir, std_species_name, touch_file=True)

        if create_mask:
            maxent_arguments, mask_filename = _create_mask(
                point_tuples, ecoregions_filename, env_dir, maxent_arguments,
                logger=logger)

        me_csv_filename = os.path.join(
            work_dir, f"{std_species_name}.csv")
        with PointCsvWriter(
                me_csv_filename, [Point.SPECIES_ATTRIBUTE, Point.X_ATTRIBUTE,
                                  Point.Y_ATTRIBUTE]
        ) as writer:
            writer.write_points(
                [Point(std_species_name, x, y) for x, y in point_tuples])
        if logger:
            logger.log("Create Maxent model", refname=script_name, log_level=INFO)
        create_maxent_model(me_csv_filename, env_dir, work_dir, maxent_arguments)

        try:
            model_filename = glob.glob(os.path.join(work_dir, "*.lambdas"))[0]
        except IndexError:
            if logger:
                logger.log(
                    f"Failed to produce Maxent model for {csv_filename}",
                    refname=script_name, log_level=INFO)
        else:
            if logger:
                logger.log(
                    f"Completed Maxent model with file {model_filename}",
                    refname=script_name, log_level=INFO)
            report["model_file"] = model_filename

        try:
            proj_distribution_filename = glob.glob(os.path.join(work_dir, "*.asc"))[0]
        except IndexError:
            if logger:
                logger.log(
                    f"Failed to produce Maxent model for {csv_filename}",
                    refname=script_name, log_level=INFO)
        else:
            if logger:
                logger.log(
                    f"Completed Maxent map with file {proj_distribution_filename}",
                    refname=script_name, log_level=INFO)
            report["projected_distribution_file"] = proj_distribution_filename

        # If used a mask, move it from common env dir to work_dir
        if os.path.exists(mask_filename):
            if logger:
                logger.log(
                    f"Delete mask {mask_filename}", refname=script_name, log_level=INFO)
            os.remove(mask_filename)

    return report


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

    if logger:
        logger.log(
            f"Projecting Maxent model {maxent_lambdas_file} onto map",
            refname=script_name, log_level=INFO)
    project_maxent_model(maxent_lambdas_file, env_dir, maxent_raster_filename)
    if logger:
        logger.log(
            f"Completed projecting Maxent model onto map {maxent_raster_filename}",
            refname=script_name, log_level=INFO)

    os.unlink(work_env_dir)
    return maxent_raster_filename, report
