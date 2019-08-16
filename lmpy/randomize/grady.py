"""Randomize PAMs using CJ's algorithm

This module contains functions used to randomize a PAM using CJ's algorithm.
This algorithm can run in a parallel fashion and uses a fill-based approach so
as to prevent a bias caused by starting with an initial condition of a
populated matrix.

Todo:
    * Eliminate "could not fix"
"""
import numpy as np
import time

from lmpy.matrix import Matrix

# Number of times to look for a match when fixing problems
SEARCH_THRESHOLD = 100000

# .............................................................................
def fill_shuffle_reshape_heuristic(orig_pam):
    """
    """
    fill = int(np.sum(orig_pam))
    approx = np.zeros((orig_pam.shape), dtype=np.int)
    approx[:fill] = 1
    np.random.shuffle(approx)
    return approx.reshape(orig_pam.shape)

# .............................................................................
def total_fill_percentage_heuristic(orig_pam):
    fill = np.sum(orig_pam)
    fill_percentage = 1.0 * fill / orig_pam.size
    approx = np.random.uniform(
        low=0.0, high=1.0, size=orig_pam.shape) <= fill_percentage
    return approx

# .............................................................................
def max_col_or_row_heuristic(orig_pam):
    """Weighting method using max weight between row and column

    This method returns a matrix of weights where the weight of each cell is
    the maximum between the proportions of the row and col
    """
    row_totals = np.sum(orig_pam, axis=1)
    col_totals = np.sum(orig_pam, axis=0)
    
    row_weights = np.expand_dims(
        row_totals.astype(np.float) / row_totals.shape[0], 1)
    col_weights = np.expand_dims(
        col_totals.astype(np.float) / col_totals.shape[0], 0)
    row_ones = np.ones(row_weights.shape)
    col_ones = np.ones(col_weights.shape)
    a = row_weights * col_ones
    b = row_ones * col_weights
    weights = np.maximum.reduce([a, b])
    return (np.random.uniform(
        low=0.0, high=1.0, size=orig_pam.shape) <= weights).astype(np.int)


# .............................................................................
def min_col_or_row_heuristic(orig_pam):
    """Weighting method using max weight between row and column

    This method returns a matrix of weights where the weight of each cell is
    the maximum between the proportions of the row and col
    """
    row_totals = np.sum(orig_pam, axis=1)
    col_totals = np.sum(orig_pam, axis=0)
    
    row_weights = np.expand_dims(
        row_totals.astype(np.float) / row_totals.shape[0], 1)
    col_weights = np.expand_dims(
        col_totals.astype(np.float) / col_totals.shape[0], 0)
    row_ones = np.ones(row_weights.shape)
    col_ones = np.ones(col_weights.shape)
    a = row_weights * col_ones
    b = row_ones * col_weights
    weights = np.minimum.reduce([a, b])
    return (np.random.uniform(
        low=0.0, high=1.0, size=orig_pam.shape) <= weights).astype(np.int)

# .............................................................................
def all_zeros_heuristic(orig_pam):
    return np.zeros(orig_pam.shape)

def all_ones_heuristic(orig_pam):
    return np.ones(orig_pam.shape)


# .............................................................................
#def grady_randomize(mtx, weights_fn=max_col_or_row):
#def grady_randomize(mtx, weights_fn=min_col_or_row):
#def grady_randomize(mtx, weights_fn=all_ones):
def grady_randomize(mtx, approximation_heuristic=total_fill_percentage_heuristic):
    """Main function for creating a random matrix

    Args:
        mtx (Matrix): A Matrix object representation of a PAM
        weights_fn (function): A function that takes row and column totals as
            arguments and outputs a Matrix of weights.

    Returns:
        Matrix: A matrix of random presence absence values with the same
            marginal totals as the input matrix 'mtx'.
    """
    # Step 0. Initialize
    # ..................
    mtx_data = mtx
    mtx_headers = mtx.get_headers()

    # Get marginal totals
    row_totals = np.sum(mtx_data, axis=1)
    col_totals = np.sum(mtx_data, axis=0)
    num_rows, num_cols = mtx_data.shape

    # Step 1. Build weights matrix
    #weights = weights_fn(row_totals, col_totals)

    row_totals = row_totals.reshape((num_rows, 1))
    col_totals = col_totals.reshape((1, num_cols))

    # Step 2. Get Initial random matrix
    # ...........................
    #rand_mtx_data = (np.random.uniform(
    #    low=0.0, high=1.0, size=mtx_data.shape) <= weights).astype(np.int)
    # Get approximation
    rand_mtx_data = approximation_heuristic(mtx).astype(np.int)

    # Step 3: Fix broken marginals
    # ...........................
    # For each row / column with more ones than the marginal total, remove
    #    extra ones until within limit
    row_sums = np.sum(rand_mtx_data, axis=1).reshape((num_rows, 1))
    for i in np.where(row_sums > row_totals)[0]:
        row_choices = np.where(rand_mtx_data[i] == 1)[0]
        change_count = int(row_sums[i] - row_totals[i])
        rand_mtx_data[
            i, np.random.permutation(row_choices)[:change_count]] = False

    col_sums = np.sum(rand_mtx_data, axis=0).reshape((1, num_cols))
    for j in np.where(col_sums > col_totals)[1]:
        col_choices = np.where(rand_mtx_data[:, j] == 1)[0]
        change_count = int(col_sums[0, j] - col_totals[0, j])
        rand_mtx_data[
            np.random.permutation(col_choices)[:change_count], j] = False

    # Step 4: Fill
    # ...........................
    problem_rows = []
    problem_cols = []

    row_sums = np.sum(rand_mtx_data, axis=1)
    col_sums = np.sum(rand_mtx_data, axis=0)

    unfilled_cols = np.where(col_sums < col_totals[0, :])[0].tolist()
    for row_idx in np.random.permutation(
            np.where(row_sums < row_totals[:, 0])[0]):

        possible_cols = np.random.permutation(
            np.intersect1d(
                np.where(rand_mtx_data[row_idx, :] == 0)[0],
                unfilled_cols, assume_unique=True))
        num_to_fill = int(row_totals[row_idx, 0] - row_sums[row_idx])
        if num_to_fill > possible_cols.shape[0]:
            # Add this row to problem rows because we can't fill it enough
            problem_rows.append(row_idx)
            # Just fill what we can
            num_to_fill = possible_cols.shape[0]
        # Fill cells
        rand_mtx_data[row_idx, possible_cols[:num_to_fill]] = True

        # Add to col_sums
        col_sums[possible_cols[:num_to_fill]] += 1

        # Check if we should remove these columns from the list
        for c in np.where(
            col_sums[possible_cols[:num_to_fill]] == col_totals[
                0, possible_cols[:num_to_fill]])[0]:
            unfilled_cols.remove(possible_cols[c])

    problem_cols = unfilled_cols

    # Step 5: Fix problems
    # ...........................
    j = 0
    while problem_rows:
        r = np.random.choice(problem_rows)
        c = np.random.choice(problem_cols)
        i = 0

        cs = np.where(rand_mtx_data[r] == 0)[0]
        rs = np.where(rand_mtx_data[:, c] == 0)[0]

        num_tries = 0
        found = False

        while not found and num_tries < SEARCH_THRESHOLD:
            r2 = np.random.choice(rs)
            c2 = np.random.choice(cs)
            num_tries += 1

            if rand_mtx_data[r2, c2] == 1:
                rand_mtx_data[r, c2] = 1
                rand_mtx_data[r2, c2] = 0
                rand_mtx_data[r2, c] = 1
                found = True

        if not found:  # pragma: no cover
            raise Exception('Couldn\'t fix row, col ({}, {})'.format(r, c))

        r_sum = np.sum(rand_mtx_data[r, :])
        c_sum = np.sum(rand_mtx_data[:, c])

        if r_sum == int(row_totals[r]):
            problem_rows.remove(r)
        if c_sum == int(col_totals[0, c]):
            problem_cols.remove(c)

    row_sums = np.sum(rand_mtx_data, axis=1)

    return Matrix(rand_mtx_data, headers=mtx_headers)

__all__ = [
    'all_ones_heuristic', 'all_zeros_heuristic',
    'fill_shuffle_reshape_heuristic', 'grady_randomize',
    'max_col_or_row_heuristic', 'min_col_or_row_heuristic',
    'total_fill_percentage_heuristic']
