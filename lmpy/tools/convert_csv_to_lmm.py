"""Convert a numeric (.csv) file to a lmpy Matrix (.lmm) file."""
import argparse

from lmpy import Matrix


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
def cli():
    """Provide a command-line tool for converting csvs to lmms."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
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
    args = parser.parse_args()
    mtx = convert_csv_to_lmm(args.in_csv_filename, args.header_rows, args.header_cols)
    mtx.write(args.out_lmm_filename)


# .....................................................................................
__all__ = ['cli', 'convert_csv_to_lmm']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
