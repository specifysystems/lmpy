"""Class for keeping track of running statistics to save memory.

Note:
    * Mean and standard deviation computations based on
        https://www.johndcook.com/blog/standard_deviation/
"""
# .............................................................................
from copy import deepcopy
import numpy as np

from lmpy import Matrix


# .............................................................................
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


# .............................................................................
def compare_signed_values(observed, test_data):
    """Compares the signed values of the observed and random data.

    Args:
        observed (:obj:`Numpy array`): A numpy array of observed values.
        test_data (:obj:`Numpy array`): A numpy array of random values.

    Returns:
        bool: An indication if the test data is greater than the observed data.
    """
    return test_data > observed


# .............................................................................
class RunningStats(object):
    """Keep track of running statistics to reduce required memory."""

    # .....................................
    def __init__(self, observed=None, compare_fn=compare_absolute_values):
        """Construct a RunningStats instance.

        Args:
            observed (numeric): The observed value to be used when computing an
                F-statistic.  It can be a single value or an array-type.
            compare_fn (:obj:method): A function used to compare pushed values
                to the observed statistic value.
        """
        self.count = 0.0
        self.compare_fn = compare_fn
        if observed is not None:
            self.observed = observed
            try:
                self.f_counts = Matrix(np.zeros(self.observed.shape))
            except Exception:
                self.f_counts = 0.0
        else:
            self.observed = None
            self.f_counts = None
        self.mean = 0.0
        self.s_k = 0.0

    # .....................................
    def push(self, val):
        """Add a test value to the running totals.

        Args:
            val (Matrix, Numpy array, or numeric): A value to use for the
                running statistics.
        """
        if not isinstance(val, list):
            val = [val]
        if self.count == 0 and isinstance(val[0], Matrix):
            self.mean = Matrix(np.zeros(val[0].shape))
            self.s_k = Matrix(np.zeros(val[0].shape))
            self.f_counts = Matrix(self.f_counts)
        for v in val:
            self.count += 1.0
            mean_k_1 = deepcopy(self.mean)
            self.mean = mean_k_1 + ((v - mean_k_1) / self.count)
            self.s_k = self.s_k + (v - mean_k_1) * (v - self.mean)
            mean_k_1 = None

            if self.observed is not None:
                self.f_counts += self.compare_fn(self.observed, v)

    # .....................................
    @property
    def standard_deviation(self):
        """Retrieve the standard deviation of the test values.

        Returns:
            float: The standard deviation of the test values.
        """
        return np.sqrt(self.variance)

    # .....................................
    @property
    def variance(self):
        """Retrieve the variance of the test values.

        Returns:
            float: The variance of the test values.
        """
        if self.count > 1:
            return self.s_k / (self.count - 1)
        return 0.0

    # .....................................
    @property
    def p_values(self):
        """Retrieve p-values from the test values greater than the f-statistic.

        Returns:
            Matrix: Computed p-values.

        Raises:
            Exception: Raised if there are no observed values.
        """
        if self.f_counts is not None:
            return self.f_counts / float(self.count)
        else:
            raise Exception('P-values cannot be computed without observed values')


# .............................................................................
__all__ = ['RunningStats', 'compare_absolute_values', 'compare_signed_values']
