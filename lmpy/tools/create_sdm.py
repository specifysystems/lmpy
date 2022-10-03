"""Create an SDM using a method determined by the data."""
import argparse
import json
import os

from lmpy.log import Logger
from lmpy.point import Point
from lmpy.sdm.maxent import DEFAULT_MAXENT_OPTIONS
from lmpy.sdm.model import create_sdm
from lmpy.tools._config_parser import _process_arguments, test_files


# .....................................................................................
DESCRIPTION = """
Create a species distribution model (SDM) from species data and environmental data and
project the model back onto the environmental data of the same type, but the same or
different values."""


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool's parameters.
    """
    parser = argparse.ArgumentParser(
        prog="create_sdm",
        description=DESCRIPTION,
    )
    parser.add_argument(
        "--config_file",
        type=str,
        help="Configuration file containing script arguments."
    )
    parser.add_argument(
        "--log_filename",
        "-l",
        type=str,
        help="A file location to write logging data."
    )
    parser.add_argument(
        "--log_console",
        action="store_true",
        default=False,
        help="If provided, write log to console."
    )
    parser.add_argument(
        "-r",
        "--report_filename",
        type=str,
        help="File location to write the wrangler report."
    )
    parser.add_argument(
        "-n",
        "--min_points",
        type=int,
        default=12,
        help="Minimum number of points to use Maxent.",
    )
    parser.add_argument(
        "-p",
        "--maxent_params",
        type=str,
        help=f"Extra options to send to Maxent (added to {DEFAULT_MAXENT_OPTIONS}.",
    )
    parser.add_argument(
        "--species_key",
        type=str,
        default=Point.SPECIES_ATTRIBUTE,
        help="Header of CSV column containing species information."
    )
    parser.add_argument(
        "--x_key",
        type=str,
        default=Point.X_ATTRIBUTE,
        help="Header of CSV column containing X value for record."
    )
    parser.add_argument(
        "--y_key",
        type=str,
        default=Point.Y_ATTRIBUTE,
        help="Header of CSV column containing Y value for record."
    )
    parser.add_argument(
        "--points_layer",
        type=str,
        default=[],
        nargs="+",
        help="One or more CSV files containing occurrences in species, x, y format.",
    )
    parser.add_argument(
        "--points_dir",
        type=str,
        default=None,
        help="Directory of CSV files containing occurrences in species, x, y format.",
    )
    parser.add_argument(
        "env_dir",
        type=str,
        help="Directory containing environment layers for modeling."
    )
    parser.add_argument(
        "ecoregions_filename", type=str, help="Ecoregions raster filename."
    )
    parser.add_argument(
        "out_dir", type=str,
        help="Parent directory for species directories of" +
             "computations and completed outputs.")
    return parser


# .....................................................................................
def test_inputs(args):
    """Test input data and configuration files for existence.

    Args:
        args: arguments pre-processed for this tool.

    Returns:
        all_missing_inputs: Error messages for display on exit.
    """
    all_errors = test_files(
        # (args.points_filename, "Occurrence data input"),
        (args.ecoregions_filename, "Ecoregion input file"))
    point_names = {}
    for fn in args.points_layer:
        outname = os.path.splitext(os.path.basename(fn))[0]
        try:
            other_fn = point_names[outname]
            all_errors.append(
                f"File {fn}, Point input has base name {outname} used by {other_fn}.")
        except KeyError:
            point_names[outname] = fn
        errs = test_files((fn, "Point layer input"))
        all_errors.extend(errs)
    return all_errors


# .....................................................................................
def cli():
    """Provide a command-line interface for SDM modeling."""
    parser = build_parser()
    try:
        args = _process_arguments(parser, "config_file")
    except FileNotFoundError as e:
        print("Missing file, exiting program")
        exit(f"{str(e)}")

    point_files = []
    if args.points_dir is not None:
        import glob
        pfiles = glob.glob(os.path.join(args.points_dir, "*.csv"))
        point_files.extend(pfiles)
    for fn in args.points_layer:
        point_files.append(fn)

    errs = test_inputs(args)
    if errs:
        print("Errors, exiting program")
        exit("\n".join(errs))

    script_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = Logger(
        script_name,
        log_filename=args.log_filename,
        log_console=args.log_console
    )
    logger.log(
        f"\n\n***Create SDMs for {len(point_files)} species occurrence CSVs",
        refname=script_name)

    maxent_params = DEFAULT_MAXENT_OPTIONS
    if args.maxent_params is not None:
        maxent_params += f" {args.maxent_params}"

    full_report = {}
    i = 0
    ct = len(point_files)
    for point_filename in point_files:
        i += 1
        # species_name contains spaces
        species_name = os.path.splitext(os.path.basename(point_filename))[0]
        # work_dir contains underscores
        work_dir = os.path.join(args.out_dir, species_name.replace(" ", "_"))
        logger.log(
            f"\n*** Starting SDM for {species_name}, file {i} of {ct}",
            refname=script_name)
        report = create_sdm(
            args.min_points,
            point_filename,
            args.env_dir,
            args.ecoregions_filename,
            work_dir,
            species_name,
            maxent_arguments=maxent_params,
            sp_key=args.species_key,
            x_key=args.x_key,
            y_key=args.y_key,
            create_mask=True,
            logger=logger
        )
        logger.log(
            f"\n*** Completed SDM computation for {species_name}\n",
            refname=script_name)
        full_report[point_filename] = report

    # Conditionally write report file
    if args.report_filename is not None:
        with open(args.report_filename, mode="wt") as out_json:
            json.dump(full_report, out_json, indent=4)


# .....................................................................................
if __name__ == "__main__":
    workdir = os.getcwd()
    print(f"PWD is {workdir}")
    cli()
