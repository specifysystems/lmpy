"""Tests the randomize Grady method module."""
import numpy as np
import pytest

from lmpy import Matrix
from lmpy.randomize.grady import (
    all_ones_heuristic,
    all_zeros_heuristic,
    fill_shuffle_reshape_heuristic,
    grady_randomize,
    max_col_or_row_heuristic,
    min_col_or_row_heuristic,
    total_fill_percentage_heuristic,
)
from copy import deepcopy


# .............................................................................
@pytest.fixture(
    scope='session',
    params=[
        None,
        all_ones_heuristic,
        all_zeros_heuristic,
        fill_shuffle_reshape_heuristic,
        max_col_or_row_heuristic,
        min_col_or_row_heuristic,
        total_fill_percentage_heuristic,
    ],
)
def heuristic_func(request):
    """Pytest fixture providing heuristic function.

    Args:
        request (Pytest.Request): A request for a test fixture.

    Yields:
        Method: A heuristic method to use for testing.
    """
    yield request.param


# .............................................................................
class Test_grady_randomize:
    """Test the Grady randomize method."""

    # .....................................
    def _test_pam_randomization(self, pam, heuristic=None):
        """Helper function to test randomization.

        Args:
            pam (Matrix): A presence absence matrix to randomize.
            heuristic (Method): A heuristic method for creating an approximate
                randomization.

        Raises:
            Exception: Raised if the PAM was not randomized.
        """
        if heuristic is not None:
            rand = grady_randomize(pam, approximation_heuristic=heuristic)
        else:
            rand = grady_randomize(deepcopy(pam))
        # Randomize until not the same as original
        count = 10
        while np.all(rand == pam) and count > 0:
            if heuristic is not None:
                rand = grady_randomize(pam, approximation_heuristic=heuristic)
            else:
                rand = grady_randomize(deepcopy(pam))
            count -= 1
        if count <= 0:
            raise Exception('Randomized PAM is same as original')

        # Test that marginal totals are the same
        assert np.all(np.sum(pam, axis=1) == np.sum(rand, axis=1))
        assert np.all(np.sum(pam, axis=0) == np.sum(rand, axis=0))

    # .....................................
    def test_empty_column(self, heuristic_func):
        """Test with a known matrix that has an empty column.

        Args:
            heuristic_func (Method): A heuristic method for creating an approximate
                randomization.
        """
        pam = Matrix(
            np.array(
                [[0, 1, 0, 1, 0], [1, 1, 0, 0, 0], [0, 0, 0, 0, 1], [1, 1, 0, 1, 1]]
            )
        )
        self._test_pam_randomization(pam, heuristic=heuristic_func)

    # .....................................
    def test_empty_row(self, heuristic_func):
        """Test with a known matrix that has an empty row.

        Args:
            heuristic_func (Method): A heuristic method for creating an approximate
                randomization.
        """
        pam = Matrix(
            np.array(
                [[0, 1, 0, 1, 0], [1, 1, 1, 0, 0], [0, 0, 0, 0, 0], [1, 1, 0, 1, 1]]
            )
        )
        self._test_pam_randomization(pam, heuristic=heuristic_func)

    # .....................................
    def test_empty_row_and_column(self, heuristic_func):
        """Test with a known matrix that has an empty row and column.

        Args:
            heuristic_func (Method): A heuristic method for creating an approximate
                randomization.
        """
        pam = Matrix(
            np.array(
                [
                    [
                        1,
                        0,
                        0,
                        1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        0,
                        1,
                        0,
                        0,
                    ],
                    [
                        1,
                        0,
                        0,
                        1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        0,
                        0,
                        0,
                        0,
                    ],
                    [
                        1,
                        1,
                        1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        1,
                        0,
                        1,
                        1,
                    ],
                    [
                        1,
                        1,
                        0,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        1,
                        1,
                        0,
                        1,
                        1,
                    ],
                    [
                        1,
                        1,
                        0,
                        1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        1,
                        1,
                        1,
                        0,
                        1,
                        1,
                    ],
                    [
                        1,
                        1,
                        1,
                        1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        1,
                        0,
                        1,
                        1,
                    ],
                    [
                        1,
                        1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        1,
                        0,
                        0,
                        1,
                    ],
                    [
                        1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        1,
                        1,
                        0,
                        0,
                        0,
                    ],
                    [
                        1,
                        1,
                        1,
                        1,
                        1,
                        1,
                        1,
                        0,
                        0,
                        1,
                        1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        1,
                        1,
                        0,
                        1,
                        1,
                    ],
                    [
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                    ],
                    [
                        1,
                        1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        1,
                        1,
                        0,
                        0,
                        0,
                    ],
                    [
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        0,
                        0,
                        0,
                        0,
                    ],
                    [
                        1,
                        0,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        1,
                        0,
                        0,
                        0,
                    ],
                    [
                        1,
                        1,
                        1,
                        0,
                        1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        1,
                        0,
                        1,
                        0,
                        0,
                        0,
                        0,
                        1,
                        0,
                        1,
                        1,
                        0,
                        0,
                        1,
                    ],
                    [
                        1,
                        0,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        1,
                        0,
                        0,
                        0,
                    ],
                    [
                        0,
                        0,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        0,
                        0,
                        0,
                        0,
                    ],
                    [
                        1,
                        0,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        1,
                        0,
                        0,
                        0,
                    ],
                    [
                        1,
                        0,
                        1,
                        0,
                        1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        0,
                        1,
                        1,
                        0,
                        0,
                        0,
                    ],
                    [
                        1,
                        0,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        0,
                        0,
                        0,
                        0,
                    ],
                    [
                        0,
                        0,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        0,
                        0,
                        0,
                        0,
                    ],
                ]
            )
        )
        self._test_pam_randomization(pam, heuristic=heuristic_func)

    # .....................................
    def test_full_column(self, heuristic_func):
        """Test with a known matrix that has a full column.

        Args:
            heuristic_func (Method): A heuristic method for creating an approximate
                randomization.
        """
        pam = Matrix(
            np.array(
                [[0, 1, 1, 1, 0], [1, 1, 1, 0, 0], [0, 0, 1, 0, 1], [1, 1, 1, 1, 1]]
            )
        )
        self._test_pam_randomization(pam, heuristic=heuristic_func)

    # .....................................
    def test_full_row(self, heuristic_func):
        """Test with a known matrix that has a full row.

        Args:
            heuristic_func (Method): A heuristic method for creating an approximate
                randomization.
        """
        pam = Matrix(
            np.array(
                [[0, 1, 0, 1, 0], [1, 1, 1, 1, 1], [0, 0, 1, 0, 1], [1, 1, 0, 1, 1]]
            )
        )
        self._test_pam_randomization(pam, heuristic=heuristic_func)

    # .....................................
    def test_known_matrix(self, heuristic_func):
        """Test with a known matrix.

        Args:
            heuristic_func (Method): A heuristic method for creating an approximate
                randomization.
        """
        pam = Matrix(
            np.array(
                [[0, 1, 0, 1, 0], [1, 1, 1, 0, 0], [0, 0, 1, 0, 1], [1, 1, 0, 1, 1]]
            )
        )
        self._test_pam_randomization(pam, heuristic=heuristic_func)

    # .....................................
    def test_random_large_matrix(self, heuristic_func):
        """Test with a randomly generated large matrix.

        Args:
            heuristic_func (Method): A heuristic method for creating an approximate
                randomization.
        """
        pam = Matrix(np.random.randint(0, 2, size=(1000, 10000)))
        self._test_pam_randomization(pam, heuristic=heuristic_func)

    # .....................................
    def test_random_matrix(self, heuristic_func):
        """Test with a randomly generated matrix.

        Args:
            heuristic_func (Method): A heuristic method for creating an approximate
                randomization.
        """
        pam = Matrix(np.random.randint(0, 2, size=(10, 10)))
        self._test_pam_randomization(pam, heuristic=heuristic_func)
