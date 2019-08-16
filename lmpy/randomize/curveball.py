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
        #row1, row2 = np.random.choice(row_len, 2, replace=False)
        row1 = randrange(0, row_len)
        row2 = randrange(0, row_len)
        while row1 == row2:
            row2 = randrange(0, row_len)
        # Curveball approach for determining possible columns
        #    Find columns where present in one row and absent in the other
        row_1_cols = np.intersect1d(
            np.where(swapped_mtx[row1, :] == 1),
            np.where(swapped_mtx[row2, :] == 0))
        row_2_cols = np.intersect1d(
            np.where(swapped_mtx[row1, :] == 0),
            np.where(swapped_mtx[row2, :] == 1))
        # If there are two choices
        if len(row_1_cols) > 0 and len(row_2_cols) > 0:
            # Pick two columns from the list of options and swap
            col1 = row_1_cols[randrange(0, row_1_cols.shape[0])]
            col2 = row_2_cols[randrange(0, row_2_cols.shape[0])]
            #col1 = randrange(0, cols.shape[0])
            #col2 = randrange(0, cols.shape[0])
            #while col1 == col2:
            #    col2 = randrange(0, cols.shape[0])
            #col1, col2 = np.random.choice(cols, 2, replace=False)
            # Swap them.  We know row 1 col 1 is 1 and row 2 col 2 is 1, so set
            #    those to zero and r1, c2 and r2, c1 to 1
            v = swapped_mtx[row1][col1]
            swapped_mtx[row1][col1] = not v
            swapped_mtx[row1][col2] = v
            swapped_mtx[row2][col1] = v
            swapped_mtx[row2][col2] = not v
            counter += 1
            num_tries = 0
    if num_tries >= max_tries:  # pragma: nocover
        raise Exception(
            'Reached maximum number of tries without finding suitable swap')

    return Matrix(swapped_mtx, headers=mtx_headers)

# .............................................................................
def curveball_two(matrix, num_swaps=None, max_tries=MAX_TRIES_WITHOUT_SWAP):
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
    
    #swapped_mtx = matrix.copy().astype(int)
    counter = 0
    num_tries = 0
    row_len, col_len = matrix.shape
    if num_swaps is None:
        num_swaps = matrix.size
    
    # Build list of lists
    decks = []
    for i in range(row_len):
        # TODO: Make this isclose probably
        decks.append(list(np.where(matrix[i, :] == 1)[0]))
    

    #  num_tries is a safety to kill the loop if nothing is ever found
    while counter < num_swaps and num_tries < max_tries:
        num_tries += 1
        #row1, row2 = np.random.choice(row_len, 2, replace=False)
        row1 = randrange(0, row_len)
        row2 = randrange(0, row_len)
        while row1 == row2:
            row2 = randrange(0, row_len)
        # Curveball approach for determining possible columns
        #    Find columns where present in one row and absent in the other
        row_1_cols = [j for j in decks[row1] if j not in decks[row2]]
        row_2_cols = [k for k in decks[row2] if k not in decks[row1]]
        
        # If there are two choices
        if len(row_1_cols) > 0 and len(row_2_cols) > 0:
            # Pick two columns from the list of options and swap
            card_1 = row_1_cols[randrange(0, len(row_1_cols))]
            card_2 = row_2_cols[randrange(0, len(row_2_cols))]
            decks[row1].pop(decks[row1].index(card_1))
            decks[row2].pop(decks[row2].index(card_2))
            decks[row1].append(card_2)
            decks[row2].append(card_1)
            counter += 1
            num_tries = 0
    if num_tries >= max_tries:  # pragma: nocover
        raise Exception(
            'Reached maximum number of tries without finding suitable swap')
    # Rebuild matrix
    swapped_mtx = np.zeros((row_len, col_len))
    for i in range(row_len):
        for j in decks[i]:
            swapped_mtx[i, j] = 1

    return Matrix(swapped_mtx, headers=mtx_headers)


# .............................................................................
def curveball_three(matrix, num_swaps, max_tries=MAX_TRIES_WITHOUT_SWAP):
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
        #row1, row2 = np.random.choice(row_len, 2, replace=False)
        row1 = randrange(0, row_len)
        row2 = randrange(0, row_len)
        while row1 == row2:
            row2 = randrange(0, row_len)
        # Curveball approach for determining possible columns
        #    Find columns where present in one row and absent in the other
        tmp = swapped_mtx[row1, :] - swapped_mtx[row2, :]
        row_1_cols = np.where(tmp == 1)[0]
        row_2_cols = np.where(tmp == -1)[0]
        #row_1_cols = np.intersect1d(
        #    np.where(swapped_mtx[row1, :] == 1),
        #    np.where(swapped_mtx[row2, :] == 0))
        #row_2_cols = np.intersect1d(
        #    np.where(swapped_mtx[row1, :] == 0),
        #    np.where(swapped_mtx[row2, :] == 1))
        # If there are two choices
        if len(row_1_cols) > 0 and len(row_2_cols) > 0:
            # Pick two columns from the list of options and swap
            col1 = row_1_cols[randrange(0, row_1_cols.shape[0])]
            col2 = row_2_cols[randrange(0, row_2_cols.shape[0])]
            #col1 = randrange(0, cols.shape[0])
            #col2 = randrange(0, cols.shape[0])
            #while col1 == col2:
            #    col2 = randrange(0, cols.shape[0])
            #col1, col2 = np.random.choice(cols, 2, replace=False)
            # Swap them.  We know row 1 col 1 is 1 and row 2 col 2 is 1, so set
            #    those to zero and r1, c2 and r2, c1 to 1
            v = swapped_mtx[row1][col1]
            swapped_mtx[row1][col1] = not v
            swapped_mtx[row1][col2] = v
            swapped_mtx[row2][col1] = v
            swapped_mtx[row2][col2] = not v
            counter += 1
            num_tries = 0
    if num_tries >= max_tries:  # pragma: nocover
        raise Exception(
            'Reached maximum number of tries without finding suitable swap')

    return Matrix(swapped_mtx, headers=mtx_headers)

__all__ = ['curveball_randomize', 'curveball_two', 'curveball_three']
