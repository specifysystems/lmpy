"""Module containing tools for evaluating statistical significance."""
from copy import deepcopy
from enum import Enum

import numpy as np

from lmpy import Matrix


# .....................................................................................
class SignificanceMethod(Enum):
    """Methods for determining statistical significance."""
    RAW = 0  # No significance value correction
    BONFERRONI = 1  # Bonferroni correction
    FDR = 2  # Benjamini and Hochberg correction


# .....................................................................................
def compare_absolute_values(observed, test_data):
    """Compares the absolute values of the observed and random data.

    Args:
        observed (:obj:`Numpy array`): A numpy array of observed values.
        test_data (:obj:`Numpy array`): A numpy array of random values.

    Returns:
        bool: Boolean indicating if the absolute value of the test data is greater than
            the absolute value of the observed data.
    """
    return np.abs(test_data) > np.abs(observed)


# .....................................................................................
def compare_signed_values(observed, test_data):
    """Compares the signed values of the observed and random data.

    Args:
        observed (:obj:`Numpy array`): A numpy array of observed values.
        test_data (:obj:`Numpy array`): A numpy array of random values.

    Returns:
        bool: An indication if the test data is greater than the observed data.
    """
    return test_data > observed


# .....................................................................................
def get_significant_values(
    p_values, alpha=0.05, correction_method=SignificanceMethod.RAW
):
    """Get significant values in a p-values matrix.

    Args:
        p_values (Matrix): A matrix of p-values to evaluate.
        alpha (float): An alpha value to use to evaluate significance.
        correction_method (int): The SignificanceMethod to use.

    Returns:
        Matrix: A boolean matrix indicating which values are cells are significant.

    Raises:
        ValueError: Raised if an unknown significance method is provided.
    """
    if correction_method == SignificanceMethod.RAW:
        return Matrix(
            p_values <= alpha,
            headers=p_values.get_headers(),
            metadata={'significance_method': 'Raw'},
        )
    elif correction_method == SignificanceMethod.BONFERRONI:
        return Matrix(
            np.minimum(p_values * p_values.size, 1.0),
            headers=p_values.get_headers(),
            metadata={'significance_method': 'Bonferroni'},
        )
    elif correction_method == SignificanceMethod.FDR:
        # In order to perform Benjamini and Hochberg correction
        # 1. Order p-values
        p_flat = p_values.flatten()
        num_vals = p_flat.size
        comp_p = 0.0
        # 2. Assign rank
        for rank, p_val in enumerate(sorted(list(p_flat))):
            # 3. Find the critical value where last p-val < (rank / num values) * alpha
            crit_val = alpha * ((rank + 1) / num_vals)
            if p_val < crit_val:
                comp_p = p_val
        # 4. All P(j) such that j <= i are significant
        return Matrix(
            p_values <= comp_p,
            headers=p_values.get_headers(),
            metadata={'significance_method': 'Benjamini and Hochberg'},
        )
    else:
        raise ValueError(f'Unknown significance method ({correction_method}).')


# .....................................................................................
class PermutationTests:
    """Tool for performing permutation tests."""
    # .......................
    def __init__(self, observed, compare_fn=compare_signed_values):
        """Constructor for PermutationTests class.

        Args:
            observed (Matrix): Observed values to test against.
            compare_fn (Method): A function used to compare values.
        """
        self.obs = observed
        self.f_counts = Matrix(np.zeros(self.obs.shape, dtype=int))
        self.count = 0
        self.compare_fn = compare_fn

    # .......................
    def add_permutation(self, test_val):
        """Compare the observed value with a test value and add to tracking.

        Args:
            test_val (Matrix): A matrix of permuted values to test against.
        """
        if test_val.ndim > self.obs.ndim:
            tmp_shp = list(self.obs.shape)
            tmp_shp.append(1)
            self.f_counts += np.sum(
                self.compare_fn(self.obs.reshape(tuple(tmp_shp)), test_val),
                axis=test_val.ndim - 1
            )
            self.count += test_val.shape[-1]
        else:
            self.f_counts += self.compare_fn(self.obs, test_val)
            self.count += 1

    # .......................
    def get_p_values(self, num_iterations=None):
        """Compute raw p-values from the permutations.

        Args:
            num_iterations (int): If provided, use this instead of self.count

        Returns:
            Matrix: A Matrix of p-values.
        """
        count = self.count
        if num_iterations is not None:
            count = num_iterations
        return Matrix(self.f_counts / count, headers=deepcopy(self.obs.get_headers()),)


# .....................................................................................
__all__ = [
    'compare_absolute_values',
    'compare_signed_values',
    'get_significant_values',
    'PermutationTests',
    'SignificanceMethod'
]
