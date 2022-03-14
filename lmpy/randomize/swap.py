"""Module containing Gotelli swap method for randomizing a PAM."""
import numpy as np

from lmpy.matrix import Matrix

MAX_TRIES_WITHOUT_SWAP = 1000000


# .............................................................................
def swap_randomize(matrix, num_swaps, max_tries=MAX_TRIES_WITHOUT_SWAP):
    """Randomize a PAM matrix using the Gotelli swap method.

    Args:
        matrix (Matrix): A Lifemapper matrix object with binary elements
        num_swaps (int): The number of swaps to perform
        max_tries (int): The maximum number of attempts to swap before failing.

    Returns:
        Matrix: A randomized matrix.

    Raises:
        Exception: Raised when the maximum number of tries is reached without swapping.

    Todo:
        Allow num_swaps to be specified as a percentage of the matrix fill.
    """
    mtx_headers = matrix.get_headers()
    swapped_mtx = matrix.copy().astype(int)
    counter = 0
    num_tries = 0
    row_len, col_len = matrix.shape

    #  num_tries is a safety to kill the loop if nothing is ever found
    while counter < num_swaps and num_tries < max_tries:
        num_tries += 1
        column1 = np.random.randint(0, col_len)
        column2 = np.random.randint(0, col_len)
        row1 = np.random.randint(0, row_len)
        while column2 == column1:
            column2 = np.random.randint(0, col_len)
        first_corner = swapped_mtx[row1][column1]
        if first_corner ^ swapped_mtx[row1][column2]:
            row2 = np.random.randint(0, row_len)
            while row2 == row1:
                row2 = np.random.randint(0, row_len)
            if (first_corner ^ swapped_mtx[row2][column1]) and (
                not (first_corner) ^ swapped_mtx[row2][column2]
            ):
                swapped_mtx[row1][column2] = first_corner
                swapped_mtx[row2][column1] = first_corner
                swapped_mtx[row2][column2] = not first_corner
                swapped_mtx[row1][column1] = not first_corner
                counter += 1
                num_tries = 0
    if num_tries >= max_tries:  # pragma: no cover
        raise Exception('Reached maximum number of tries without finding suitable swap')

    return Matrix(swapped_mtx, headers=mtx_headers)


# .............................................................................
def trial_swap(matrix, num_trials=None):
    """Randomize a PAM matrix using the trial swap method.

    Args:
        matrix (Matrix): A Lifemapper matrix object with binary elements.
        num_trials (int): The number of trials to perform.

    Returns:
        Matrix: A randomized matrix.

    Todo:
        Allow num_swaps to be specified as a percentage of the matrix fill
    """
    mtx_headers = matrix.get_headers()
    swapped_mtx = matrix.copy().astype(int)
    row_len, col_len = matrix.shape
    if num_trials is None:
        num_trials = matrix.size

    for _ in range(num_trials):
        column1 = np.random.randint(0, col_len)
        column2 = np.random.randint(0, col_len)
        row1 = np.random.randint(0, row_len)
        while column2 == column1:
            column2 = np.random.randint(0, col_len)
        first_corner = swapped_mtx[row1][column1]
        if first_corner ^ swapped_mtx[row1][column2]:
            row2 = np.random.randint(0, row_len)
            while row2 == row1:
                row2 = np.random.randint(0, row_len)
            if (first_corner ^ swapped_mtx[row2][column1]) and (
                not (first_corner) ^ swapped_mtx[row2][column2]
            ):
                swapped_mtx[row1][column2] = first_corner
                swapped_mtx[row2][column1] = first_corner
                swapped_mtx[row2][column2] = not first_corner
                swapped_mtx[row1][column1] = not first_corner

    return Matrix(swapped_mtx, headers=mtx_headers)


# .............................................................................
__all__ = ['swap_randomize', 'trial_swap']
