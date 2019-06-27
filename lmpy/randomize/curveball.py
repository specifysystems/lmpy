"""Module containing Curveball swap method
"""
import numpy as np
from random import randrange

from lmpy.matrix import Matrix

MAX_TRIES_WITHOUT_SWAP = 1000000


# .............................................................................
def curveball_randomize(matrix, num_swaps, max_tries=MAX_TRIES_WITHOUT_SWAP):
    """Randomize a PAM matrix using the Gotelli swap method with curveball

    Args:
        matrix (:obj: Matrix): A Lifemapper matrix object with binary elements
        num_swaps (:obj: int): The number of swaps to perform
        max_tries (:obj: int): The maximum number of attempts to swap before
            failing

    Todo:
        Allow num_swaps to be specified as a percentage of the matrix fill
    """
    mtx_headers = matrix.get_headers()
    swapped_mtx = matrix.copy().astype(int)
    counter = 0
    num_tries = 0
    row_len, col_len = matrix.shape

    #  num_tries is a safety to kill the loop if nothing is ever found
    while counter < num_swaps and num_tries < max_tries:
        num_tries += 1
        row1, row2 = np.random.choice(row_len, 2, replace=False)
        row1 = randrange(0, row_len)
        row2 = randrange(0, row_len)
        while row1 == row2:
            row2 = randrange(0, row_len)
        # Curveball approach for determining possible columns
        #    Find columns where present in one row and absent in the other
        cols = np.where(
            np.logical_xor(swapped_mtx[row1, :], swapped_mtx[row2, :]))[0]
        # If there are two choices
        if len(cols) > 1:
            # Pick two columns from the list of options and swap
            col1 = randrange(0, cols.shape[0])
            col2 = randrange(0, cols.shape[0])
            while col1 == col2:
                col2 = randrange(0, cols.shape[0])
            #col1, col2 = np.random.choice(cols, 2, replace=False)
            # Swap them.  We know row 1 col 1 is 1 and row 2 col 2 is 1, so set
            #    those to zero and r1, c2 and r2, c1 to 1
            swapped_mtx[row1][col1] = 0
            swapped_mtx[row1][col2] = 1
            swapped_mtx[row2][col1] = 1
            swapped_mtx[row2][col2] = 0
            counter += 1
            num_tries = 0
    if num_tries >= max_tries:  # pragma: nocover
        raise Exception(
            'Reached maximum number of tries without finding suitable swap')

    return Matrix(swapped_mtx, headers=mtx_headers)

__all__ = ['curveball_randomize']
