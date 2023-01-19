"""Convert a numeric (.csv) file to a lmpy Matrix (.lmm) file."""
import argparse
import json
import os

from lmpy.log import Logger
from lmpy.matrix import Matrix
from lmpy.tools._config_parser import _process_arguments, test_files

script_name = os.path.splitext(os.path.basename(__file__))[0]
DESCRIPTION = "Convert a CSV file of numerical values into a lmpy Matrix."


# .....................................................................................
def convert_csv_to_lmm(
        csv_filename, header_rows, header_cols, data_type_str, logger):
    """Convert a CSV file to a lmpy lmm Matrix.

    Args:
        csv_filename (str): The file location of the csv to convert.
        header_rows (int): The number of header rows in the csv.
        header_cols (int): The number of header columns in the csv.
        data_type_str (str): The type of data in the matrix, float or int.
        logger (lmpy.log.Logger): object for writing log statements.

    Raises:
        Exception: on data_type other than 'float' or 'int'.

    Returns:
        Matrix: A matrix from the converted csv file.
    """
    if data_type_str == "float":
        data_type = float
    elif data_type_str == "int":
        data_type = int
    else:
        raise Exception(f"Unsupported data_type {data_type_str}")

    with open(csv_filename, mode="rt") as csv_in:
        mtx = Matrix.load_csv(
            csv_in, dtype=data_type, num_header_rows=header_rows,
            num_header_cols=header_cols
        )
    logger.log(
        f"Read CSV file {csv_filename} of data type `{data_type_str}`, " +
        f"with {header_rows} header rows indicating column metadata " +
        f"and {header_cols} header columns indicating row metadata ",
        refname=script_name)
    return mtx


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool"s parameters.
    """
    parser = argparse.ArgumentParser(
        prog="convert_csv_to_lmm",
        description=DESCRIPTION
    )
    parser.add_argument('--config_file', type=str, help='Path to configuration file.')
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
        "--data_type",
        choices=["float", "int"],
        type=str,
        default="float",
        help="The data type of the values in the CSV, options are `float` or `int`.",
    )
    parser.add_argument(
        "--header_rows",
        type=int,
        default=0,
        help="The number of header rows in the CSV.",
    )
    parser.add_argument(
        "--header_cols",
        type=int,
        default=0,
        help="The number of header columns in the CSV.",
    )
    parser.add_argument(
        "in_csv_filename", type=str, help="CSV filename to convert to lmm Matrix."
    )
    parser.add_argument("out_lmm_filename", type=str, help="Filename for .lmm Matrix.")
    return parser


# .....................................................................................
def test_inputs(args):
    """Test input data and configuration files for existence.

    Args:
        args: arguments pre-processed for this tool.

    Returns:
        all_missing_inputs: Error messages for display on exit.
    """
    all_missing_inputs = test_files((args.in_csv_filename, "CSV input"))
    return all_missing_inputs


# .....................................................................................
def cli():
    """Provide a command-line tool for converting csvs to lmms.

    Raises:
        OSError: on failure to write to report_filename.
        IOError: on failure to write to report_filename.
    """
    parser = build_parser()
    args = _process_arguments(parser, config_arg='config_file')
    errs = test_inputs(args)
    if errs:
        print("Errors, exiting program")
        exit("\n".join(errs))

    logger = Logger(
        script_name,
        log_filename=args.log_filename,
        log_console=args.log_console
    )

    mtx = convert_csv_to_lmm(
        args.in_csv_filename, args.header_rows, args.header_cols, args.data_type,
        logger)
    report = mtx.get_report()

    mtx.write(args.out_lmm_filename)
    logger.log(
        f"Wrote into matrix {args.out_lmm_filename} containing " +
        f"{report['rows']} rows and {report['columns']} columns", refname=script_name)

    # If the output report was requested, write it
    if args.report_filename:
        report["in_csv_filename"] = args.in_csv_filename
        report["header_rows"] = args.header_rows
        report["header_cols"] = args.header_cols
        report["out_lmm_filename"] = args.out_lmm_filename
        try:
            with open(args.report_filename, mode='wt') as out_file:
                json.dump(report, out_file, indent=4)
        except OSError:
            raise
        except IOError:
            raise
        logger.log(
            f"Wrote report file to {args.report_filename}", refname=script_name)


# .....................................................................................
__all__ = ["build_parser", "cli", "convert_csv_to_lmm"]


# .....................................................................................
if __name__ == "__main__":  # pragma: no cover
    cli()
