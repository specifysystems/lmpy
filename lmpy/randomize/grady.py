"""Randomize PAMs using CJ's algorithm.

This module contains functions used to randomize a PAM using CJ's algorithm.
This algorithm can run in a parallel fashion and uses a fill-based approach so
as to prevent a bias caused by starting with an initial condition of a
populated matrix.
"""
import numpy as np

from lmpy.matrix import Matrix

# Number of times to look for a match when fixing problems
SEARCH_THRESHOLD = 100


# .............................................................................
def fill_shuffle_reshape_heuristic(orig_pam):
    """Create an approximation with the correct number of 1s randomly placed.

    Creates an array with the total number of ones from the original PAM and
    shuffles it then it reshapes it to match the shape of the original PAM.

    Args:
        orig_pam (Matrix): The observed PAM to randomize.

    Returns:
        Matrix: An approximate randomization of the PAM that is uncorrected.
    """
    fill = int(np.sum(orig_pam))
    approx = np.zeros((orig_pam.shape), dtype=int)
    approx[:fill] = 1
    np.random.shuffle(approx)
    return approx.reshape(orig_pam.shape)


# .............................................................................
def total_fill_percentage_heuristic(orig_pam):
    """Create an approximation using the total fill percentage of the PAM.

    Creates an approximation using the total matrix fill of the original PAM
    as a weight threshold to compare with randomly generated numbers.

    Args:
        orig_pam (:obj:`Matrix`): The observed PAM to randomize.

    Returns:
        Matrix: An approximate randomization of the PAM that is uncorrected.
    """
    fill = np.sum(orig_pam)
    fill_percentage = 1.0 * fill / orig_pam.size
    approx = (
        np.random.uniform(low=0.0, high=1.0, size=orig_pam.shape) <= fill_percentage
    ).astype(int)
    return approx


# .............................................................................
def max_col_or_row_heuristic(orig_pam):
    """Weighting method using max weight between row and column.

    This method returns a matrix of weights where the weight of each cell is
    the maximum between the proportions of the row and col

    Args:
        orig_pam (:obj:`Matrix`): The observed PAM to randomize.

    Returns:
        Matrix: An approximate randomization of the PAM that is uncorrected.
    """
    row_totals = np.sum(orig_pam, axis=1)
    col_totals = np.sum(orig_pam, axis=0)

    row_weights = row_totals.astype(float) / row_totals.shape[0]
    col_weights = col_totals.astype(float) / col_totals.shape[0]

    row_weights = np.expand_dims(row_totals.astype(float) / row_totals.shape[0], 1)
    col_weights = np.expand_dims(col_totals.astype(float) / col_totals.shape[0], 0)
    return (
        np.random.uniform(low=0.0, high=1.0, size=orig_pam.shape)
        <= np.maximum(row_weights, col_weights)
    ).astype(int)


# .............................................................................
def min_col_or_row_heuristic(orig_pam):
    """Weighting method using max weight between row and column.

    This method returns a matrix of weights where the weight of each cell is
    the maximum between the proportions of the row and col

    Args:
        orig_pam (:obj:`Matrix`): The observed PAM to randomize.

    Returns:
        Matrix: An approximate randomization of the PAM that is uncorrected.
    """
    row_totals = np.sum(orig_pam, axis=1, dtype=int)
    col_totals = np.sum(orig_pam, axis=0, dtype=int)

    row_weights = np.expand_dims(row_totals.astype(float) / row_totals.shape[0], 1)
    col_weights = np.expand_dims(col_totals.astype(float) / col_totals.shape[0], 0)
    return (
        np.random.uniform(low=0.0, high=1.0, size=orig_pam.shape)
        <= np.minimum(row_weights, col_weights, dtype=np.single)
    ).astype(int)


# .............................................................................
def all_zeros_heuristic(orig_pam):
    """Creates a two-dimensional approximation composed of all zeros.

    Args:
        orig_pam (:obj:`Matrix`): The observed PAM to randomize.

    Returns:
        Matrix: An approximate randomization of the PAM that is uncorrected.
    """
    return np.zeros(orig_pam.shape, dtype=int)


# .............................................................................
def all_ones_heuristic(orig_pam):
    """Creates a two-dimensional approximation composed of all ones.

    Args:
        orig_pam (:obj:`Matrix`): The observed PAM to randomize.

    Returns:
        Matrix: An approximate randomization of the PAM that is uncorrected.
    """
    return np.ones(orig_pam.shape, dtype=int)


# .............................................................................
def grady_randomize(mtx, approximation_heuristic=total_fill_percentage_heuristic):
    """Main function for creating a random matrix.

    Args:
        mtx (:obj:`Matrix`): A Matrix object representation of a PAM
        approximation_heuristic (:obj:`Method`): A function that generates an
            approximation of a final randomized matrix.

    Returns:
        Matrix: A matrix of random presence absence values with the same
            marginal totals as the input matrix 'mtx'.
    """
    # Step 0. Get marginal totals
    # ...........................
    num_rows, num_cols = mtx.shape
    row_totals = np.sum(mtx, axis=1).reshape((num_rows, 1))
    col_totals = np.sum(mtx, axis=0).reshape((1, num_cols))
    valid_rows = np.sum(mtx, axis=1) != 0
    valid_cols = np.sum(mtx, axis=0) != 0

    # Step 1. Get Initial random matrix
    # ...........................
    # Get approximation
    rand_mtx_data = approximation_heuristic(mtx)

    # Step 2: Purge over-filled marginals
    # ...................................
    # For each row / column with more ones than the marginal total, remove
    #    extra ones until within limit
    row_sums = np.sum(rand_mtx_data, axis=1).reshape((num_rows, 1))
    for i in np.where(row_sums > row_totals)[0]:
        row_choices = np.where(rand_mtx_data[i] == 1)[0]
        change_count = int(row_sums[i] - row_totals[i])
        rand_mtx_data[i, np.random.permutation(row_choices)[:change_count]] = False

    col_sums = np.sum(rand_mtx_data, axis=0).reshape((1, num_cols))
    for j in np.where(col_sums > col_totals)[1]:
        col_choices = np.where(rand_mtx_data[:, j] == 1)[0]
        change_count = int(col_sums[0, j] - col_totals[0, j])
        rand_mtx_data[np.random.permutation(col_choices)[:change_count], j] = False

    # Step 3: Fill
    # ...........................
    problem_rows = []
    problem_cols = []

    row_sums = np.sum(rand_mtx_data, axis=1)
    col_sums = np.sum(rand_mtx_data, axis=0)

    unfilled_cols = np.where(col_sums < col_totals[0, :])[0].tolist()
    for row_idx in np.random.permutation(np.where(row_sums < row_totals[:, 0])[0]):

        possible_cols = np.random.permutation(
            np.intersect1d(
                np.where(rand_mtx_data[row_idx, :] == 0)[0],
                unfilled_cols,
                assume_unique=True,
            )
        )
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
            col_sums[possible_cols[:num_to_fill]]
            == col_totals[0, possible_cols[:num_to_fill]]
        )[0]:
            unfilled_cols.remove(possible_cols[c])

    problem_cols = unfilled_cols

    # Step 4: Fix problems
    # ...........................
    j = 0
    while problem_rows:
        r = np.random.choice(problem_rows)
        c = np.random.choice(problem_cols)
        i = 0

        cs = np.where((rand_mtx_data[r] == 0) & (valid_cols))[0]
        rs = np.where((rand_mtx_data[:, c] == 0) & (valid_rows))[0]

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
            # Can't fix row easily so randomly move a one
            prs = np.where(rand_mtx_data[:, c2] == 1)[0]
            update_row = np.random.choice(prs)
            rand_mtx_data[r, c2] = 1
            rand_mtx_data[update_row, c2] = 0

            # Should we add update row to problem rows or is it already there?
            if update_row not in problem_rows:
                problem_rows.append(update_row)

        r_sum = np.sum(rand_mtx_data[r, :])
        c_sum = np.sum(rand_mtx_data[:, c])

        if r_sum == int(row_totals[r]):
            problem_rows.remove(r)
        if c_sum == int(col_totals[0, c]):
            problem_cols.remove(c)

    row_sums = np.sum(rand_mtx_data, axis=1)

    return Matrix(rand_mtx_data, headers=mtx.get_headers())


# .............................................................................
__all__ = [
    'all_ones_heuristic',
    'all_zeros_heuristic',
    'fill_shuffle_reshape_heuristic',
    'grady_randomize',
    'max_col_or_row_heuristic',
    'min_col_or_row_heuristic',
    'total_fill_percentage_heuristic',
]
