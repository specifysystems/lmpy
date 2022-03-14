"""Tests the running statistics module."""
import numpy as np
import pytest

from lmpy import Matrix
from lmpy.statistics.running_stats import (
    compare_absolute_values,
    compare_signed_values,
    RunningStats,
)


# .............................................................................
class Test_RunningStats(object):
    """Test the RunningStats class."""

    # .....................................
    def test_single_values(self):
        """Tests the RunningStats class using single values."""
        vals1 = [1, 2, 3, 4, 5]
        vals2 = [6, 7, 7, 8, 9, 10]
        all_vals = []
        all_vals.extend(vals1)
        all_vals.extend(vals2)
        np_all_vals = np.array(all_vals)

        rs = RunningStats()
        assert rs.variance == 0.0
        for v in vals1:
            rs.push(v)
        rs.push(vals2)
        assert rs.mean == np.mean(np_all_vals)
        assert rs.standard_deviation == np.std(np_all_vals, ddof=1)
        assert rs.variance == np.var(np_all_vals, ddof=1)
        with pytest.raises(Exception):
            rs.p_values

    # .....................................
    def test_single_values_with_p_values(self):
        """Tests the RunningStats class using single values with p-values."""
        f_val = 6
        vals1 = [1, 2, 3, 4, 5]
        vals2 = [6, -7, 7, -8, -9, 10]
        all_vals = []
        all_vals.extend(vals1)
        all_vals.extend(vals2)
        np_all_vals = np.array(all_vals)

        rs = RunningStats(observed=f_val, compare_fn=compare_absolute_values)
        assert rs.variance == 0.0
        for v in vals1:
            rs.push(v)
        rs.push(vals2)
        assert np.isclose(rs.mean, np.mean(np_all_vals))
        assert np.isclose(rs.standard_deviation, np.std(np_all_vals, ddof=1))
        assert np.isclose(rs.variance, np.var(np_all_vals, ddof=1))
        num_greater = 0
        for v in all_vals:
            if np.abs(v) > np.abs(f_val):
                num_greater += 1
        assert rs.p_values == float(num_greater) / len(all_vals)

    # .....................................
    def test_single_values_with_p_values_signed(self):
        """Tests the RunningStats class using single values with p-values."""
        f_val = 6
        vals1 = [1, 2, 3, 4, 5]
        vals2 = [6, -7, 7, -8, 9, 10]
        all_vals = []
        all_vals.extend(vals1)
        all_vals.extend(vals2)
        np_all_vals = np.array(all_vals)

        rs = RunningStats(observed=f_val, compare_fn=compare_signed_values)
        assert rs.variance == 0.0
        for v in vals1:
            rs.push(v)
        rs.push(vals2)
        assert np.isclose(rs.mean, np.mean(np_all_vals))
        assert np.isclose(rs.standard_deviation, np.std(np_all_vals, ddof=1))
        assert np.isclose(rs.variance, np.var(np_all_vals, ddof=1))
        num_greater = 0
        for v in all_vals:
            if v > f_val:
                num_greater += 1
        assert rs.p_values == float(num_greater) / len(all_vals)

    # .....................................
    def test_matrix_with_no_p_values(self):
        """Tests the RunningStats class using Matrix objects without p-values."""
        _ = Matrix(np.random.randint(0, 10, size=(10, 10)))
        vals = []
        rs = RunningStats()
        assert np.all(rs.variance == np.zeros((10, 10)))
        for _ in range(5):
            vals.append(Matrix(np.random.randint(-10, 10, size=(10, 10))))
        rs.push(vals)
        for _ in range(5):
            test_val = Matrix(np.random.randint(-10, 10, size=(10, 10)))
            rs.push(test_val)
            vals.append(test_val)
        v_stack = np.array([v for v in vals])
        assert np.all(np.isclose(rs.mean, np.mean(v_stack, axis=0)))
        assert np.all(
            np.isclose(rs.standard_deviation, np.std(v_stack, axis=0, ddof=1))
        )
        assert np.all(np.isclose(rs.variance, np.var(v_stack, axis=0, ddof=1)))
        with pytest.raises(Exception):
            rs.p_values

    # .....................................
    def test_matrixs_with_p_values_absolute_values(self):
        """Tests the RunningStats class using Matrix objects with p-values."""
        obs = Matrix(np.random.randint(0, 10, size=(10, 10)))
        vals = []
        rs = RunningStats(observed=obs, compare_fn=compare_absolute_values)
        assert np.all(rs.variance == np.zeros((10, 10)))
        for _ in range(5):
            vals.append(Matrix(np.random.randint(-10, 10, size=(10, 10))))
        rs.push(vals)
        for _ in range(5):
            test_val = Matrix(np.random.randint(-10, 10, size=(10, 10)))
            rs.push(test_val)
            vals.append(test_val)
        v_stack = np.array([v for v in vals])
        assert np.all(np.isclose(rs.mean, np.mean(v_stack, axis=0)))
        assert np.all(
            np.isclose(rs.standard_deviation, np.std(v_stack, axis=0, ddof=1))
        )
        assert np.all(np.isclose(rs.variance, np.var(v_stack, axis=0, ddof=1)))
        num_greater = Matrix(np.zeros((10, 10)))
        for i in range(v_stack.shape[0]):
            num_greater += np.abs(v_stack[i, ...]) > np.abs(obs)
        assert np.all(rs.p_values == num_greater.astype(float) / len(vals))

    # .....................................
    def test_matrix_with_p_values_signed(self):
        """Tests the RunningStats class using Matrix objects with p-values."""
        obs = Matrix(np.random.randint(0, 10, size=(10, 10)))
        vals = []
        rs = RunningStats(observed=obs, compare_fn=compare_signed_values)
        assert np.all(rs.variance == np.zeros((10, 10)))
        for _ in range(5):
            vals.append(Matrix(np.random.randint(-10, 10, size=(10, 10))))
        rs.push(vals)
        for _ in range(5):
            test_val = Matrix(np.random.randint(-10, 10, size=(10, 10)))
            rs.push(test_val)
            vals.append(test_val)
        v_stack = np.array([v for v in vals])
        assert np.all(np.isclose(rs.mean, np.mean(v_stack, axis=0)))
        assert np.all(
            np.isclose(rs.standard_deviation, np.std(v_stack, axis=0, ddof=1))
        )
        assert np.all(np.isclose(rs.variance, np.var(v_stack, axis=0, ddof=1)))
        num_greater = Matrix(np.zeros((10, 10)))
        for i in range(v_stack.shape[0]):
            num_greater += v_stack[i, ...] > obs
        assert np.all(rs.p_values == num_greater.astype(float) / len(vals))

    # .....................................
    def test_numpy_arrays_with_no_p_values(self):
        """Tests the RunningStats class using numpy arrays without p-values."""
        vals = []
        rs = RunningStats()
        assert np.all(rs.variance == np.zeros((10, 10)))
        for _ in range(5):
            vals.append(np.random.randint(-10, 10, size=(10, 10)))
        rs.push(vals)
        for _ in range(5):
            test_val = np.random.randint(-10, 10, size=(10, 10))
            rs.push(test_val)
            vals.append(test_val)
        v_stack = np.array(vals)
        assert np.all(np.isclose(rs.mean, np.mean(v_stack, axis=0)))
        assert np.all(
            np.isclose(rs.standard_deviation, np.std(v_stack, axis=0, ddof=1))
        )
        assert np.all(np.isclose(rs.variance, np.var(v_stack, axis=0, ddof=1)))
        with pytest.raises(Exception):
            rs.p_values

    # .....................................
    def test_numpy_arrays_with_p_values_absolute_values(self):
        """Tests the RunningStats class using numpy arrays with p-values."""
        obs = np.random.randint(0, 10, size=(10, 10))
        vals = []
        rs = RunningStats(observed=obs, compare_fn=compare_absolute_values)
        assert np.all(rs.variance == np.zeros((10, 10)))
        for _ in range(5):
            vals.append(np.random.randint(-10, 10, size=(10, 10)))
        rs.push(vals)
        for _ in range(5):
            test_val = np.random.randint(-10, 10, size=(10, 10))
            rs.push(test_val)
            vals.append(test_val)
        v_stack = np.array(vals)
        assert np.all(np.isclose(rs.mean, np.mean(v_stack, axis=0)))
        assert np.all(
            np.isclose(rs.standard_deviation, np.std(v_stack, axis=0, ddof=1))
        )
        assert np.all(np.isclose(rs.variance, np.var(v_stack, axis=0, ddof=1)))
        num_greater = np.zeros((10, 10))
        for i in range(v_stack.shape[0]):
            num_greater += np.abs(v_stack[i, ...]) > np.abs(obs)
        assert np.all(rs.p_values == num_greater.astype(float) / len(vals))

    # .....................................
    def test_numpy_arrays_with_p_values_signed(self):
        """Tests the RunningStats class using numpy arrays with p-values."""
        obs = np.random.randint(0, 10, size=(10, 10))
        vals = []
        rs = RunningStats(observed=obs, compare_fn=compare_signed_values)
        assert np.all(rs.variance == np.zeros((10, 10)))
        for _ in range(5):
            vals.append(np.random.randint(-10, 10, size=(10, 10)))
        rs.push(vals)
        for _ in range(5):
            test_val = np.random.randint(-10, 10, size=(10, 10))
            rs.push(test_val)
            vals.append(test_val)
        v_stack = np.array(vals)
        assert np.all(np.isclose(rs.mean, np.mean(v_stack, axis=0)))
        assert np.all(
            np.isclose(rs.standard_deviation, np.std(v_stack, axis=0, ddof=1))
        )
        assert np.all(np.isclose(rs.variance, np.var(v_stack, axis=0, ddof=1)))
        num_greater = np.zeros((10, 10))
        for i in range(v_stack.shape[0]):
            num_greater += v_stack[i, ...] > obs
        assert np.all(rs.p_values == num_greater.astype(float) / len(vals))
