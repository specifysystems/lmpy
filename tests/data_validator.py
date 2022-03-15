"""Tools for validating data."""
from lmpy.point import PointCsvReader


# .....................................................................................
def validate_point_csvs(fns, sp_key, x_key, y_key):
    """Validate point csv file(s).

    Args:
        fns (list or str): A file or list of csv files.
        sp_key (str): A header key with species information.
        x_key (str): A header key for x information.
        y_key (str): A header key for y information.

    Returns:
        bool: Indication if file(s) are valid.
    """
    if isinstance(fns, str):
        fns = [fns]
    for fn in fns:
        print(fn)
        i = 0
        with open(fn, mode='rt') as in_file:
            for line in in_file:
                if i < 3:
                    print(line)
                i += 1
        points = []
        with PointCsvReader(fn, sp_key, x_key, y_key) as reader:
            for pts in reader:
                points.extend(pts)
        if len(points) == 0:
            return False
    return True
