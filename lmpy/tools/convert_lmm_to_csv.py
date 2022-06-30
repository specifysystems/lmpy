"""Convert a lmpy Matrix to a (.csv) file."""
import argparse

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
    parser = argparse.ArgumentParser(
        prog='convert_lmm_to_csv',
        description=DESCRIPTION,
    )
    parser.add_argument(
        'in_lmm_filename', type=str, help='Lmpy LMM filename to convert to CSV.'
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
    """Provide a command-line tool for converting lmms to csvs."""
    parser = build_parser()
    args = _process_arguments(parser)
    errs = test_inputs(args)
    if errs:
        print("Errors, exiting program")
        exit('\n'.join(errs))
    mtx = Matrix.load(args.in_lmm_filename)
    convert_lmm_to_csv(mtx, args.out_csv_filename)


# .....................................................................................
__all__ = ['build_parser', 'cli', 'convert_lmm_to_csv']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
