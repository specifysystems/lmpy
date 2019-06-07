"""Module containing Gotelli swap method for randomizing a PAM
"""
from random import randrange

from LmCommon.common.matrix import Matrix

MAX_TRIES_WITHOUT_SWAP = 1000000

# .............................................................................
def swapRandomize(matrix, num_swaps, max_tries=MAX_TRIES_WITHOUT_SWAP):
    """Randomize a PAM matrix using the Gotelli swap method

    Args:
        matrix (:obj: Matrix): A Lifemapper matrix object with binary elements
        num_swaps (:obj: int): The number of swaps to perform
        max_tries (:obj: int): The maximum number of attempts to swap before
            failing

    Todo:
        Allow num_swaps to be specified as a percentage of the matrix fill
    """
    mtx_headers = matrix.getHeaders()
    swapped_mtx = matrix.data.copy().astype(int)
    counter = 0
    num_tries = 0
    row_len, col_len = matrix.data.shape

    #num_tries is a safety to kill the loop if nothing is ever found
    while counter < num_swaps and num_tries < max_tries:
        num_tries += 1
        column1 = randrange(0, col_len)
        column2 = randrange(0, col_len)
        row1 = randrange(0, row_len)
        while column2 == column1:
            column2 = randrange(0, col_len)
        first_corner = swapped_mtx[row1][column1]
        if first_corner ^ swapped_mtx[row1][column2]:
            row2 = randrange(0, row_len)
            while row2 == row1:
                    row2 = randrange(0, row_len)
            if ((first_corner ^ swapped_mtx[row2][column1]) and
                 (not(first_corner) ^ swapped_mtx[row2][column2])):
                    swapped_mtx[row1][column2] = first_corner
                    swapped_mtx[row2][column1] = first_corner
                    swapped_mtx[row2][column2] = not(first_corner)
                    swapped_mtx[row1][column1] = not(first_corner)
                    counter += 1
                    num_tries = 0
    if num_tries >= max_tries:
        raise Exception(
            'Reached maximum number of tries without finding suitable swap')

    return Matrix(swapped_mtx, headers=mtx_headers)
    