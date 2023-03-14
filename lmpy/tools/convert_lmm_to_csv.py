"""Convert a lmpy Matrix to a (.csv) file."""
import argparse
import json
import logging
import os

from lmpy.log import Logger
from lmpy.matrix import Matrix
from lmpy.tools._config_parser import _process_arguments, test_files


DESCRIPTION = 'Convert a lmpy Matrix to a CSV file with numerical values.'


# .....................................................................................
def convert_lmm_to_csv(mtx, csv_filename):
    """Convert a lmpy Matrix to a csv file.

    Args:
        mtx (Matrix): A lmpy matrix to convert to csv.
        csv_filename (str): The file location of the csv to convert.

    Raises:
        OSError: on failure to write to csv_filename.
        IOError: on failure to write to csv_filename.
    """
    try:
        with open(csv_filename, mode='wt') as csv_out:
            mtx.write_csv(csv_out)
    except OSError:
        raise
    except IOError:
        raise


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool's parameters.
    """
    parser = argparse.ArgumentParser(prog='convert_lmm_to_csv', description=DESCRIPTION)
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
        help="File location to write the report."
    )
    parser.add_argument(
        'in_lmm_filename', type=str, help='Lmpy LMM filename to be converted to CSV.'
    )
    parser.add_argument(
        'out_csv_filename', type=str, help='Location to write the converted matrix CSV.'
    )
    return parser


# .....................................................................................
def test_inputs(args):
    """Test input data and configuration files for existence.

    Args:
        args: arguments pre-processed for this tool.

    Returns:
        all_missing_inputs: Error messages for display on exit.
    """
    all_missing_inputs = test_files((args.in_lmm_filename, "Matrix input"))
    return all_missing_inputs


# .....................................................................................
def cli():
    """Provide a command-line tool for converting lmms to csvs.

    Raises:
        OSError: on failure to write to report_filename.
        IOError: on failure to write to report_filename.
    """
    parser = build_parser()
    args = _process_arguments(parser, config_arg='config_file')
    errs = test_inputs(args)
    if errs:
        print("Errors, exiting program")
        exit('\n'.join(errs))

    script_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = Logger(
        script_name,
        log_filename=args.log_filename,
        log_console=args.log_console
    )

    mtx = Matrix.load(args.in_lmm_filename)

    col_count = len(mtx.get_column_headers())
    row_count = len(mtx.get_row_headers())
    logger.log(
        f"Loaded matrix {args.in_lmm_filename} with {row_count} rows " +
        f"and {col_count} columns", refname=script_name)
    if col_count > 1024:
        logger.log(
            "NOTE: number of columns exceeds maximum allowed in some common "
            "spreadsheet applications, such as Excel (16,384 columns) "
            "or LibreOffice Calc (1024 columns) or Apple Numbers (1000 columns)",
            log_level=logging.WARNING, refname=script_name)
    if row_count > 1048576:
        logger.log(
            "NOTE: number of rows exceeds maximum allowed in some common spreadsheet "
            "applications, such as Excel and LibreOffice Calc (1,048,576 rows) or "
            "Apple Numbers (1,000,000 rows)",
            log_level=logging.WARNING, refname=script_name)

    # convert_lmm_to_csv(mtx, args.out_csv_filename)
    mtx.write_csv(args.out_csv_filename)

    logger.log(
        f"Wrote matrix {args.in_lmm_filename} to CSV file {args.out_csv_filename}",
        refname=script_name)

    # If the output report was requested, write it
    if args.report_filename:
        report = mtx.get_report()
        report["in_matrix_filename"] = args.in_lmm_filename
        report["out_csv_filename"] = args.out_csv_filename
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
__all__ = ['build_parser', 'cli', 'convert_lmm_to_csv']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
