"""Convert a lmpy Matrix to a (.csv) file."""
import argparse

from lmpy.matrix import Matrix
from lmpy.tools._config_parser import _process_arguments


DESCRIPTION = 'Convert a lmpy Matrix to a CSV file with numerical values.'


# .....................................................................................
def convert_lmm_to_csv(mtx, csv_filename):
    """Convert a lmpy Matrix to a csv file.

    Args:
        mtx (Matrix): A lmpy matrix to convert to csv.
        csv_filename (str): The file location of the csv to convert.
    """
    with open(csv_filename, mode='wt') as csv_out:
        mtx.write_csv(csv_out)


# .....................................................................................
def cli():
    """Provide a command-line tool for converting lmms to csvs."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        'in_lmm_filename', type=str, help='Lmpy LMM filename to convert to CSV.'
    )
    parser.add_argument(
        'out_csv_filename', type=str, help='Location to write the converted matrix CSV.'
    )
    args = _process_arguments(parser)
    mtx = Matrix.load(args.in_lmm_filename)
    convert_lmm_to_csv(mtx, args.out_csv_filename)


# .....................................................................................
__all__ = ['cli', 'convert_lmm_to_csv']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
