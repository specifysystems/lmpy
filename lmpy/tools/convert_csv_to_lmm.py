"""Convert a numeric (.csv) file to a lmpy Matrix (.lmm) file."""
import argparse

from lmpy.matrix import Matrix
from lmpy.tools._config_parser import _process_arguments


DESCRIPTION = 'Convert a CSV file of numerical values into a lmpy Matrix.'


# .....................................................................................
def convert_csv_to_lmm(csv_filename, num_header_rows, num_header_cols):
    """Convert a CSV file to a lmpy lmm Matrix.

    Args:
        csv_filename (str): The file location of the csv to convert.
        num_header_rows (int): The number of header rows in the csv.
        num_header_cols (int): The number of header columns in the csv.

    Returns:
        Matrix: A matrix from the converted csv file.
    """
    with open(csv_filename, mode='rt') as csv_in:
        mtx = Matrix.load_csv(
            csv_in, num_header_rows=num_header_rows, num_header_cols=num_header_cols
        )
    return mtx


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool's parameters.
    """
    parser = argparse.ArgumentParser(
        prog='convert_csv_to_lmm',
        description=DESCRIPTION
    )
    parser.add_argument(
        '--header_rows',
        '-r',
        type=int,
        default=0,
        help='The number of header rows in the CSV.',
    )
    parser.add_argument(
        '--header_cols',
        '-c',
        type=int,
        default=0,
        help='The number of header columns in the CSV.',
    )
    parser.add_argument(
        'in_csv_filename', type=str, help='CSV filename to convert to lmm Matrix.'
    )
    parser.add_argument('out_lmm_filename', type=str, help='Filename for .lmm Matrix.')
    return parser


# .....................................................................................
def cli():
    """Provide a command-line tool for converting csvs to lmms."""
    parser = build_parser()
    args = _process_arguments(parser)
    mtx = convert_csv_to_lmm(args.in_csv_filename, args.header_rows, args.header_cols)
    mtx.write(args.out_lmm_filename)


# .....................................................................................
__all__ = ['build_parser', 'cli', 'convert_csv_to_lmm']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
